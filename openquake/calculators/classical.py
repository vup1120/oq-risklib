# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2014-2016 GEM Foundation
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

from __future__ import division
import operator
import collections
from functools import partial
import numpy

from openquake.hazardlib.geo.utils import get_spherical_bounding_box
from openquake.hazardlib.geo.utils import get_longitudinal_extent
from openquake.hazardlib.geo.geodetic import npoints_between
from openquake.hazardlib.calc.filters import source_site_distance_filter
from openquake.hazardlib.calc.hazard_curve import (
    hazard_curves_per_trt, zero_curves, zero_maps,
    array_of_curves, ProbabilityMap)
from openquake.risklib import scientific
from openquake.commonlib import parallel, datastore, source
from openquake.baselib.general import AccumDict

from openquake.calculators import base, calc


HazardCurve = collections.namedtuple('HazardCurve', 'location poes')


# this is needed for the disaggregation
class BoundingBox(object):
    """
    A class to store the bounding box in distances, longitudes and magnitudes,
    given a source model and a site. This is used for disaggregation
    calculations. The goal is to determine the minimum and maximum
    distances of the ruptures generated from the model from the site;
    moreover the maximum and minimum longitudes and magnitudes are stored, by
    taking in account the international date line.
    """
    def __init__(self, lt_model_id, site_id):
        self.lt_model_id = lt_model_id
        self.site_id = site_id
        self.min_dist = self.max_dist = None
        self.east = self.west = self.south = self.north = None

    def update(self, dists, lons, lats):
        """
        Compare the current bounding box with the value in the arrays
        dists, lons, lats and enlarge it if needed.

        :param dists:
            a sequence of distances
        :param lons:
            a sequence of longitudes
        :param lats:
            a sequence of latitudes
        """
        if self.min_dist is not None:
            dists = [self.min_dist, self.max_dist] + dists
        if self.west is not None:
            lons = [self.west, self.east] + lons
        if self.south is not None:
            lats = [self.south, self.north] + lats
        self.min_dist, self.max_dist = min(dists), max(dists)
        self.west, self.east, self.north, self.south = \
            get_spherical_bounding_box(lons, lats)

    def update_bb(self, bb):
        """
        Compare the current bounding box with the given bounding box
        and enlarge it if needed.

        :param bb:
            an instance of :class:
            `openquake.engine.calculators.hazard.classical.core.BoundingBox`
        """
        if bb:  # the given bounding box must be non-empty
            self.update([bb.min_dist, bb.max_dist], [bb.west, bb.east],
                        [bb.south, bb.north])

    def bins_edges(self, dist_bin_width, coord_bin_width):
        """
        Define bin edges for disaggregation histograms, from the bin data
        collected from the ruptures.

        :param dists:
            array of distances from the ruptures
        :param lons:
            array of longitudes from the ruptures
        :param lats:
            array of latitudes from the ruptures
        :param dist_bin_width:
            distance_bin_width from job.ini
        :param coord_bin_width:
            coordinate_bin_width from job.ini
        """
        dist_edges = dist_bin_width * numpy.arange(
            int(self.min_dist / dist_bin_width),
            int(numpy.ceil(self.max_dist / dist_bin_width) + 1))

        west = numpy.floor(self.west / coord_bin_width) * coord_bin_width
        east = numpy.ceil(self.east / coord_bin_width) * coord_bin_width
        lon_extent = get_longitudinal_extent(west, east)

        lon_edges, _, _ = npoints_between(
            west, 0, 0, east, 0, 0,
            numpy.round(lon_extent / coord_bin_width) + 1)

        lat_edges = coord_bin_width * numpy.arange(
            int(numpy.floor(self.south / coord_bin_width)),
            int(numpy.ceil(self.north / coord_bin_width) + 1))

        return dist_edges, lon_edges, lat_edges

    def __nonzero__(self):
        """
        True if the bounding box is non empty.
        """
        return (self.min_dist is not None and self.west is not None and
                self.south is not None)


@parallel.litetask
def classical(sources, sitecol, siteidx, rlzs_assoc, monitor):
    """
    :param sources:
        a non-empty sequence of sources of homogeneous tectonic region type
    :param sitecol:
        a SiteCollection instance
    :param siteidx:
        index of the first site (0 if there is a single tile)
    :param rlzs_assoc:
        a RlzsAssoc instance
    :param monitor:
        a monitor instance
    :returns:
        an AccumDict rlz -> curves
    """
    truncation_level = monitor.oqparam.truncation_level
    imtls = monitor.oqparam.imtls
    trt_model_id = sources[0].trt_model_id
    # sanity check: the trt_model must be the same for all sources
    for src in sources[1:]:
        assert src.trt_model_id == trt_model_id
    gsims = rlzs_assoc.gsims_by_trt_id[trt_model_id]
    trt = sources[0].tectonic_region_type
    max_dist = monitor.oqparam.maximum_distance[trt]

    dic = AccumDict()
    dic.siteslice = slice(siteidx, siteidx + len(sitecol))
    if monitor.oqparam.poes_disagg:
        sm_id = rlzs_assoc.sm_ids[trt_model_id]
        dic.bbs = [BoundingBox(sm_id, sid) for sid in sitecol.sids]
    else:
        dic.bbs = []
    # NB: the source_site_filter below is ESSENTIAL for performance inside
    # hazard_curves_per_trt, since it reduces the full site collection
    # to a filtered one *before* doing the rupture filtering
    dic[trt_model_id] = hazard_curves_per_trt(
        sources, sitecol, imtls, gsims, truncation_level,
        source_site_filter=source_site_distance_filter(max_dist),
        maximum_distance=max_dist, bbs=dic.bbs, monitor=monitor)
    dic.calc_times = monitor.calc_times  # added by hazard_curves_per_trt
    dic.eff_ruptures = {trt_model_id: monitor.eff_ruptures}  # idem
    return dic


@base.calculators.add('classical')
class ClassicalCalculator(base.HazardCalculator):
    """
    Classical PSHA calculator
    """
    core_task = classical
    source_info = datastore.persistent_attribute('source_info')

    def agg_dicts(self, acc, val):
        """
        Aggregate dictionaries of hazard curves by updating the accumulator.

        :param acc: accumulator dictionary
        :param val: a nested dictionary trt_id -> ProbabilityMap
        """
        with self.monitor('aggregate curves', autoflush=True):
            if hasattr(val, 'calc_times'):
                acc.calc_times.extend(val.calc_times)
            if hasattr(val, 'eff_ruptures'):
                acc.eff_ruptures += val.eff_ruptures
            for bb in getattr(val, 'bbs', []):
                acc.bb_dict[bb.lt_model_id, bb.site_id].update_bb(bb)
            acc |= val
        self.datastore.flush()
        return acc

    def count_eff_ruptures(self, result_dict, trt_model):
        """
        Returns the number of ruptures in the trt_model (after filtering)
        or 0 if the trt_model has been filtered away.

        :param result_dict: a dictionary with keys (trt_id, gsim)
        :param trt_model: a TrtModel instance
        """
        return (result_dict.eff_ruptures.get(trt_model.id, 0) /
                self.manager.num_tiles)

    def zerodict(self):
        """
        Initial accumulator, an empty ProbabilityMap
        """
        zd = ProbabilityMap()
        zd.calc_times = []
        zd.eff_ruptures = AccumDict()  # trt_id -> eff_ruptures
        zd.bb_dict = {
            (smodel.ordinal, site.id): BoundingBox(smodel.ordinal, site.id)
            for site in self.sitecol
            for smodel in self.csm.source_models
        } if self.oqparam.poes_disagg else {}
        return zd

    def execute(self):
        """
        Run in parallel `core_task(sources, sitecol, monitor)`, by
        parallelizing on the sources according to their weight and
        tectonic region type.
        """
        monitor = self.monitor.new(self.core_task.__name__)
        monitor.oqparam = self.oqparam
        curves_by_trt_id = self.manager.tm.reduce(
            self.agg_dicts, self.zerodict(), posthook=self.save_data_transfer)
        with self.monitor('store source_info', autoflush=True):
            self.store_source_info(curves_by_trt_id)
        self.rlzs_assoc = self.csm.info.get_rlzs_assoc(
            partial(self.count_eff_ruptures, curves_by_trt_id))
        self.datastore['csm_info'] = self.csm.info
        return curves_by_trt_id

    def store_source_info(self, curves_by_trt_id):
        # store the information about received data
        received = self.manager.tm.received
        if received:
            tname = self.manager.tm.name
            self.datastore.save('job_info', {
                tname + '_max_received_per_task': max(received),
                tname + '_tot_received': sum(received),
                tname + '_num_tasks': len(received)})
        # then save the calculation times per each source
        calc_times = getattr(curves_by_trt_id, 'calc_times', [])
        if calc_times:
            sources = self.csm.get_sources()
            info_dict = {(rec['trt_model_id'], rec['source_id']): rec
                         for rec in self.source_info}
            for src_idx, dt in calc_times:
                src = sources[src_idx]
                info = info_dict[src.trt_model_id, src.source_id]
                info['calc_time'] += dt
            self.source_info = numpy.array(
                sorted(info_dict.values(), key=operator.itemgetter(7),
                       reverse=True), source.source_info_dt)
        self.datastore.hdf5.flush()

    def post_execute(self, curves_by_trt_id):
        """
        Collect the hazard curves by realization and export them.

        :param curves_by_trt_id:
            a dictionary trt_id -> hazard curves
        """
        nsites = len(self.sitecol)
        imtls = self.oqparam.imtls
        curves_by_trt_gsim = {}

        with self.monitor('saving probability maps', autoflush=True):
            for trt_id in curves_by_trt_id:
                key = 'poes/%04d' % trt_id
                self.datastore[key] = curves_by_trt_id[trt_id]
                self.datastore.set_attrs(
                    key, trt=self.csm.info.get_trt(trt_id))
                gsims = self.rlzs_assoc.gsims_by_trt_id[trt_id]
                for i, gsim in enumerate(gsims):
                    curves_by_trt_gsim[trt_id, gsim] = (
                        curves_by_trt_id[trt_id].extract(i))
            self.datastore.set_nbytes('poes')

        with self.monitor('combine curves_by_rlz', autoflush=True):
            curves_by_rlz = self.rlzs_assoc.combine_curves(curves_by_trt_gsim)

        self.save_curves({rlz: array_of_curves(curves, nsites, imtls)
                          for rlz, curves in curves_by_rlz.items()})

    def save_curves(self, curves_by_rlz):
        """
        Save the dictionary curves_by_rlz
        """
        oq = self.oqparam
        rlzs = self.rlzs_assoc.realizations
        nsites = len(self.sitecol)
        if oq.individual_curves:
            with self.monitor('save curves_by_rlz', autoflush=True):
                for rlz, curves in curves_by_rlz.items():
                    self.store_curves('rlz-%03d' % rlz.ordinal, curves, rlz)

            if len(rlzs) == 1:  # cannot compute statistics
                [self.mean_curves] = curves_by_rlz.values()
                return

        with self.monitor('compute and save statistics', autoflush=True):
            weights = (None if oq.number_of_logic_tree_samples
                       else [rlz.weight for rlz in rlzs])

            # mean curves are always computed but stored only on request
            zc = zero_curves(nsites, oq.imtls)
            self.mean_curves = numpy.array(zc)
            for imt in oq.imtls:
                self.mean_curves[imt] = scientific.mean_curve(
                    [curves_by_rlz.get(rlz, zc)[imt] for rlz in rlzs], weights)

            self.quantile = {}
            for q in oq.quantile_hazard_curves:
                self.quantile[q] = qc = numpy.array(zc)
                for imt in oq.imtls:
                    curves = [curves_by_rlz[rlz][imt] for rlz in rlzs]
                    qc[imt] = scientific.quantile_curve(
                        curves, q, weights).reshape((nsites, -1))

            if oq.mean_hazard_curves:
                self.store_curves('mean', self.mean_curves)
            for q in self.quantile:
                self.store_curves('quantile-%s' % q, self.quantile[q])

    def hazard_maps(self, curves):
        """
        Compute the hazard maps associated to the curves
        """
        maps = zero_maps(
            len(self.sitecol), self.oqparam.imtls, self.oqparam.poes)
        for imt in curves.dtype.fields:
            # build a matrix of size (N, P)
            data = calc.compute_hazard_maps(
                curves[imt], self.oqparam.imtls[imt], self.oqparam.poes)
            for poe, hmap in zip(self.oqparam.poes, data.T):
                maps['%s~%s' % (imt, poe)] = hmap
        return maps

    def store_curves(self, kind, curves, rlz=None):
        """
        Store all kind of curves, optionally computing maps and uhs curves.

        :param kind: the kind of curves to store
        :param curves: an array of N curves to store
        :param rlz: hazard realization, if any
        """
        oq = self.oqparam
        self._store('hcurves/' + kind, curves, rlz, nbytes=curves.nbytes)
        self.datastore['hcurves'].attrs['imtls'] = [
            (imt, len(imls)) for imt, imls in self.oqparam.imtls.items()]
        if oq.hazard_maps or oq.uniform_hazard_spectra:
            # hmaps is a composite array of shape (N, P)
            hmaps = self.hazard_maps(curves)
            self._store('hmaps/' + kind, hmaps, rlz,
                        poes=oq.poes, nbytes=hmaps.nbytes)

    def _store(self, name, curves, rlz, **kw):
        self.datastore.hdf5[name] = curves
        dset = self.datastore.hdf5[name]
        if rlz is not None:
            dset.attrs['uid'] = rlz.uid
        for k, v in kw.items():
            dset.attrs[k] = v


def nonzero(val):
    """
    :returns: the sum of the composite array `val`
    """
    return sum(val[k].sum() for k in val.dtype.names)
