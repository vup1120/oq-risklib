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

from __future__ import print_function
import io
import os
import logging

from openquake.hazardlib.calc.hazard_curve import zero_curves
from openquake.commonlib import sap, datastore
from openquake.commonlib.oqvalidation import OqParam
from openquake.commonlib.writers import write_csv
from openquake.commonlib.reportwriter import set_ancestors
from openquake.commonlib.util import rmsep
from openquake.risklib import scientific


def get_hcurves_and_means(dstore):
    """
    Extract hcurves from the datastore and compute their means.

    :returns: curves_by_rlz, mean_curves
    """
    oq = OqParam.from_(dstore.attrs)
    hcurves = dstore['hcurves']
    realizations = dstore['rlzs_assoc'].realizations
    weights = [rlz.weight for rlz in realizations]
    curves_by_rlz = {rlz: hcurves['rlz-%03d' % rlz.ordinal]
                     for rlz in realizations}
    N = len(dstore['sitemesh'])
    mean_curves = zero_curves(N, oq.imtls)
    for imt in oq.imtls:
        mean_curves[imt] = scientific.mean_curve(
            [curves_by_rlz[rlz][imt] for rlz in sorted(curves_by_rlz)],
            weights)
    return curves_by_rlz, mean_curves


def show(what, calc_id=-1):
    """
    Show the content of a datastore.

    :param what: key or view of the datastore
    :param calc_id: numeric calculation ID; if -1, show the last calculation
    """
    if what == 'all':  # show all
        if not os.path.exists(datastore.DATADIR):
            return
        rows = []
        for calc_id in datastore.get_calc_ids(datastore.DATADIR):
            try:
                ds = datastore.read(calc_id)
                oq = OqParam.from_(ds.attrs)
                cmode, descr = oq.calculation_mode, oq.description
            except:
                # invalid datastore file, or missing calculation_mode
                # and description attributes, perhaps due to a manual kill
                logging.warn('Removed invalid calculation %d', calc_id)
                os.remove(
                    os.path.join(datastore.DATADIR, 'calc_%s.hdf5' % calc_id))
                continue
            else:
                rows.append((calc_id, cmode, descr))
                ds.close()
        for row in sorted(rows, key=lambda row: row[0]):  # by calc_id
            print('#%d %s: %s' % row)
        return
    elif what == 'views':
        for name in sorted(datastore.view):
            print(name)
        return

    ds = datastore.read(calc_id)
    set_ancestors(ds)

    # this part is experimental
    if what == 'rlzs' and 'hcurves' in ds:
        min_value = 0.01  # used in rmsep
        curves_by_rlz, mean_curves = get_hcurves_and_means(ds)
        dists = []
        for rlz, curves in curves_by_rlz.items():
            dist = sum(rmsep(mean_curves[imt], curves[imt], min_value)
                       for imt in mean_curves.dtype.fields)
            dists.append((dist, rlz))
        print('Realizations in order of distance from the mean curves')
        for dist, rlz in sorted(dists):
            print('%s: rmsep=%s' % (rlz, dist))
    elif what in datastore.view:
        print(datastore.view(what, ds))
    else:
        obj = ds[what]
        if hasattr(obj, 'value'):  # an array
            print(write_csv(io.StringIO(), obj.value))
        else:
            print(obj)


parser = sap.Parser(show)
parser.arg('what', 'key or view of the datastore')
parser.arg('calc_id', 'calculation ID', type=int)
