# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2015-2016 GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.

import os
import re
import pydoc
from openquake.baselib.python3compat import pickle
import collections

import numpy
try:
    import h5py
except ImportError:
    # there is no need of h5py in the workers
    class mock_h5py(object):
        def __getattr__(self, name):
            raise ImportError('Could not import h5py.%s' % name)
    h5py = mock_h5py()

from openquake.baselib.hdf5 import Hdf5Dataset
from openquake.baselib.general import CallableDict
from openquake.commonlib.writers import write_csv


# a dictionary of views datastore -> array
view = CallableDict()

DATADIR = os.environ.get('OQ_DATADIR', os.path.expanduser('~/oqdata'))


def get_nbytes(dset):
    """
    If the dataset has an attribute 'nbytes', return it. Otherwise get the size
    of the underlying array. Returns None if the dataset is actually a group.
    """
    if 'nbytes' in dset.attrs:
        # look if the dataset has an attribute nbytes
        return dset.attrs['nbytes']
    elif hasattr(dset, 'value'):
        # else extract nbytes from the underlying array
        return dset.size * numpy.zeros(1, dset.dtype).nbytes


class ByteCounter(object):
    """
    A visitor used to measure the dimensions of a HDF5 dataset or group.
    Use it as ByteCounter.get_nbytes(dset_or_group).
    """
    @classmethod
    def get_nbytes(cls, dset):
        nbytes = get_nbytes(dset)
        if nbytes is not None:
            return nbytes
        # else dip in the tree
        self = cls()
        dset.visititems(self)
        return self.nbytes

    def __init__(self, nbytes=0):
        self.nbytes = nbytes

    def __call__(self, name, dset_or_group):
        nbytes = get_nbytes(dset_or_group)
        if nbytes:
            self.nbytes += nbytes


def get_calc_ids(datadir=DATADIR):
    """
    Extract the available calculation IDs from the datadir, in order.
    """
    if not os.path.exists(datadir):
        return []
    calc_ids = []
    for f in os.listdir(DATADIR):
        mo = re.match(r'calc_(\d+)\.hdf5', f)
        if mo:
            calc_ids.append(int(mo.group(1)))
    return sorted(calc_ids)


def get_last_calc_id(datadir):
    """
    Extract the latest calculation ID from the given directory.
    If none is found, return 0.
    """
    calcs = get_calc_ids(datadir)
    if not calcs:
        return 0
    return calcs[-1]


def read(calc_id, mode='r', datadir=DATADIR):
    """
    :param calc_id: calculation ID
    :param mode: 'r' or 'w'
    :param datadir: the directory where to look
    :returns: the corresponding DataStore instance

    Read the datastore, if it exists and it is accessible.
    """
    if calc_id < 0:  # retrieve an old datastore
        calc_id = get_calc_ids(datadir)[calc_id]
    fname = os.path.join(datadir, 'calc_%s.hdf5' % calc_id)
    open(fname).close()  # check if the file exists and is accessible
    return DataStore(calc_id, datadir, mode=mode)


class DataStore(collections.MutableMapping):
    """
    DataStore class to store the inputs/outputs of a calculation on the
    filesystem.

    Here is a minimal example of usage:

    >>> ds = DataStore()
    >>> ds['example'] = 'hello world'
    >>> ds.items()
    [(u'example', 'hello world')]
    >>> ds.clear()

    When reading the items, the DataStore will return a generator. The
    items will be ordered lexicographically according to their name.

    There is a serialization protocol to store objects in the datastore.
    An object is serializable if it has a method `__toh5__` returning
    an array and a dictionary, and a method `__fromh5__` taking an array
    and a dictionary and populating the object.
    For an example of use see :class:`openquake.hazardlib.site.SiteCollection`.
    """
    def __init__(self, calc_id=None, datadir=DATADIR,
                 export_dir='.', params=(), mode=None):
        if not os.path.exists(datadir):
            os.makedirs(datadir)
        if calc_id is None:  # use a new datastore
            self.calc_id = get_last_calc_id(datadir) + 1
        elif calc_id < 0:  # use an old datastore
            calc_ids = get_calc_ids(datadir)
            try:
                self.calc_id = calc_ids[calc_id]
            except IndexError:
                raise IndexError('There are %d old calculations, cannot '
                                 'retrieve the %s' % (len(calc_ids), calc_id))
        else:  # use the given datastore
            self.calc_id = calc_id
        self.parent = ()  # can be set later
        self.datadir = datadir
        self.calc_dir = os.path.join(datadir, 'calc_%s' % self.calc_id)
        self.export_dir = export_dir
        self.hdf5path = self.calc_dir + '.hdf5'
        mode = mode or 'r+' if os.path.exists(self.hdf5path) else 'w'
        self.hdf5 = h5py.File(self.hdf5path, mode, libver='latest')
        self.attrs = self.hdf5.attrs
        for name, value in params:
            self.attrs[name] = value

    def set_parent(self, parent):
        """
        Give a parent to a datastore and update its .attrs with the parent
        attributes, which are assumed to be literal strings.
        """
        self.parent = parent
        # merge parent attrs into child attrs
        for name, value in self.parent.attrs.items():
            if name not in self.attrs:  # add missing parameter
                self.attrs[name] = value

    def set_nbytes(self, key):
        """
        Set the `nbytes` attribute on the HDF5 object identified by `key`.
        """
        obj = self.hdf5[key]
        obj.attrs['nbytes'] = nbytes = ByteCounter.get_nbytes(obj)
        return nbytes

    def set_attrs(self, key, **kw):
        """
        Set the HDF5 attributes of the given key
        """
        for k, v in kw.items():
            self.hdf5[key].attrs[k] = v

    def get_attr(self, key, name, default=None):
        """
        :param key: dataset path
        :param name: name of the attribute
        :param default: value to return if the attribute is missing
        """
        obj = self[key]
        try:
            return obj.attrs[name]
        except KeyError:
            if default is None:
                raise
            return default

    def create_dset(self, key, dtype, size=None, compression=None):
        """
        Create a one-dimensional HDF5 dataset.

        :param key: name of the dataset
        :param dtype: dtype of the dataset (usually composite)
        :param size: size of the dataset (if None, the dataset is extendable)
        """
        return Hdf5Dataset.create(self.hdf5, key, dtype, size, compression)

    def export_path(self, relname, export_dir=None):
        """
        Return the path of the exported file by adding the export_dir in
        front, the calculation ID at the end.

        :param relname: relative file name
        :param export_dir: export directory (if None use .export_dir)
        """
        assert not os.path.dirname(relname), relname
        name, ext = relname.rsplit('.', 1)
        newname = '%s_%s.%s' % (name, self.calc_id, ext)
        if export_dir is None:
            export_dir = self.export_dir
        return os.path.join(export_dir, newname)

    def export_csv(self, key):
        """
        Generic csv exporter
        """
        return write_csv(self.export_path(key, 'csv'), self[key])

    def flush(self):
        """Flush the underlying hdf5 file"""
        self.hdf5.flush()

    def close(self):
        """Close the underlying hdf5 file"""
        if self.parent:
            self.parent.close()
        if self.hdf5:  # is open
            self.hdf5.close()

    def clear(self):
        """Remove the datastore from the file system"""
        self.close()
        os.remove(self.hdf5path)

    def getsize(self, key=None):
        """
        Return the size in byte of the output associated to the given key.
        If no key is given, returns the total size of all files.
        """
        if key is None:
            return os.path.getsize(self.hdf5path)
        return ByteCounter.get_nbytes(self.hdf5[key])

    def get(self, key, default):
        """
        :returns: the value associated to the datastore key, or the default
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        try:
            val = self.hdf5[key]
        except KeyError:
            if self.parent:
                try:
                    val = self.parent.hdf5[key]
                except KeyError:
                    raise KeyError(
                        'No %r found in %s' % (key, [self, self.parent]))
            else:
                raise KeyError('No %r found in %s' % (key, self))
        try:
            shape = val.shape
        except AttributeError:  # val is a group
            return val
        if '__pyclass__' in val.attrs:  # serialized object
            value, attrs = val.value, dict(val.attrs)
            cls = pydoc.locate(attrs.pop('__pyclass__'))
            val = cls.__new__(cls)
            val.__fromh5__(value, attrs)
        if not shape:
            val = pickle.loads(val.value)
        return val

    def __setitem__(self, key, value):
        attrs = {}
        if hasattr(value, '__toh5__'):
            val, attrs = value.__toh5__()
            attrs['__pyclass__'] = '.'.join([value.__class__.__module__,
                                             value.__class__.__name__])
        elif (not isinstance(value, numpy.ndarray) or
                value.dtype is numpy.dtype(object)):
            val = numpy.array(pickle.dumps(value, pickle.HIGHEST_PROTOCOL))
        else:
            val = value
        if key in self.hdf5:
            # there is a bug in the current version of HDF5 for composite
            # arrays: is impossible to save twice the same key; so we remove
            # the key first, then it is possible to save it again
            del self[key]
        try:
            self.hdf5[key] = val
        except RuntimeError as exc:
            raise RuntimeError('Could not save %s: %s in %s' %
                               (key, exc, self.hdf5path))
        # save attributes if any
        for k, v in attrs.items():
            self.hdf5[key].attrs[k] = v

    def __delitem__(self, key):
        if (h5py.version.version <= '2.0.1' and not
                hasattr(self.hdf5[key], 'shape')):
            # avoid bug when deleting groups that produces a segmentation fault
            return
        del self.hdf5[key]

    def __enter__(self):
        return self

    def __exit__(self, etype, exc, tb):
        self.close()

    def __iter__(self):
        if not self.hdf5:
            raise RuntimeError('%s is closed' % self)
        for path in sorted(self.hdf5):
            yield path

    def __contains__(self, key):
        return key in self.hdf5

    def __len__(self):
        return sum(1 for f in self)

    def __repr__(self):
        return '<%s %d>' % (self.__class__.__name__, self.calc_id)


class Fake(dict):
    """
    A fake datastore as a dict subclass, useful in tests and such
    """
    def __init__(self, attrs=None, **kwargs):
        self.attrs = {k: repr(v) for k, v in attrs.items()} if attrs else {}
        self.update(kwargs)


def persistent_attribute(key):
    """
    Persistent attributes are persisted to the datastore and cached.
    Modifications to mutable objects are not automagically persisted.
    If you have a huge object that does not fit in memory use the datastore
    directory (for instance, open a HDF5 file to create an empty array, then
    populate it). Notice that you can use any dict-like data structure in
    place of the datastore, provided you can set attributes on it.
    Here is an example:

    >>> class Datastore(dict):
    ...     "A fake datastore"

    >>> class Store(object):
    ...     a = persistent_attribute('a')
    ...     def __init__(self, a):
    ...         self.datastore = Datastore()
    ...         self.a = a  # this assegnation will store the attribute

    >>> store = Store([1])
    >>> store.a  # this retrieves the attribute
    [1]
    >>> store.a.append(2)
    >>> store.a = store.a  # remember to store the modified attribute!

    :param key: the name of the attribute to be made persistent
    :returns: a property to be added to a class with a .datastore attribute
    """
    privatekey = '_' + key

    def getter(self):
        # Try to get the value from the privatekey attribute (i.e. from
        # the cache of the datastore); if not possible, get the value
        # from the datastore and set the cache; if not possible, get the
        # value from the parent and set the cache. If the value cannot
        # be retrieved, raise an AttributeError.
        try:
            return getattr(self.datastore, privatekey)
        except AttributeError:
            value = self.datastore[key]
            setattr(self.datastore, privatekey, value)
            return value

    def setter(self, value):
        # Update the datastore and the private key
        self.datastore[key] = value
        setattr(self.datastore, privatekey, value)

    return property(getter, setter)
