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

import time
import os.path
import operator
import logging
import collections

import numpy

from openquake.baselib import hdf5
from openquake.baselib.general import AccumDict, groupby
from openquake.baselib.performance import Monitor
from openquake.hazardlib.calc.filters import \
    filter_sites_by_distance_to_rupture
from openquake.hazardlib.calc.hazard_curve import zero_curves
from openquake.hazardlib import geo, site, calc
from openquake.hazardlib.gsim.base import ContextMaker
from openquake.commonlib import readinput, parallel, datastore
from openquake.commonlib.util import max_rel_diff_index, Rupture

from openquake.calculators import base
from openquake.calculators.calc import gmvs_to_haz_curve
from openquake.calculators.classical import ClassicalCalculator

# ######################## rupture calculator ############################ #

U16 = numpy.uint16
U32 = numpy.uint32
F32 = numpy.float32
HAZCURVES = 1

event_dt = numpy.dtype([('eid', U32), ('ses', U32), ('occ', U32)])

def get_geom(surface, is_from_fault_source, is_multi_surface):
    """
    The following fields can be interpreted different ways,
    depending on the value of `is_from_fault_source`. If
    `is_from_fault_source` is True, each of these fields should
    contain a 2D numpy array (all of the same shape). Each triple
    of (lon, lat, depth) for a given index represents the node of
    a rectangular mesh. If `is_from_fault_source` is False, each
    of these fields should contain a sequence (tuple, list, or
    numpy array, for example) of 4 values. In order, the triples
    of (lon, lat, depth) represent top left, top right, bottom
    left, and bottom right corners of the the rupture's planar
    surface. Update: There is now a third case. If the rupture
    originated from a characteristic fault source with a
    multi-planar-surface geometry, `lons`, `lats`, and `depths`
    will contain one or more sets of 4 points, similar to how
    planar surface geometry is stored (see above).

    :param rupture: an instance of :class:`openquake.hazardlib.source.rupture.BaseProbabilisticRupture`
    :param is_from_fault_source: a boolean
    :param is_multi_surface: a boolean
    """
    if is_from_fault_source:
        # for simple and complex fault sources,
        # rupture surface geometry is represented by a mesh
        surf_mesh = surface.get_mesh()
        lons = surf_mesh.lons
        lats = surf_mesh.lats
        depths = surf_mesh.depths
    else:
        if is_multi_surface:
            # `list` of
            # openquake.hazardlib.geo.surface.planar.PlanarSurface
            # objects:
            surfaces = surface.surfaces

            # lons, lats, and depths are arrays with len == 4*N,
            # where N is the number of surfaces in the
            # multisurface for each `corner_*`, the ordering is:
            #   - top left
            #   - top right
            #   - bottom left
            #   - bottom right
            lons = numpy.concatenate([x.corner_lons for x in surfaces])
            lats = numpy.concatenate([x.corner_lats for x in surfaces])
            depths = numpy.concatenate([x.corner_depths for x in surfaces])
        else:
            # For area or point source,
            # rupture geometry is represented by a planar surface,
            # defined by 3D corner points
            lons = numpy.zeros((4))
            lats = numpy.zeros((4))
            depths = numpy.zeros((4))

            # NOTE: It is important to maintain the order of these
            # corner points. TODO: check the ordering
            for i, corner in enumerate((surface.top_left,
                                        surface.top_right,
                                        surface.bottom_left,
                                        surface.bottom_right)):
                lons[i] = corner.longitude
                lats[i] = corner.latitude
                depths[i] = corner.depth
    return lons, lats, depths


class EBRupture(object):
    """
    An event based rupture. It is a wrapper over a hazardlib rupture
    object, containing an array of site indices affected by the rupture,
    as well as the tags of the corresponding seismic events.
    """
    def __init__(self, rupture, indices, events, source_id, trt_id, serial):
        self.rupture = rupture
        self.indices = indices
        self.events = events
        self.source_id = source_id
        self.trt_id = trt_id
        self.serial = serial

    @property
    def etags(self):
        """
        An array of tags for the underlying seismic events
        """
        tags = []
        for (eid, ses, occ) in self.events:
            tag = 'trt=%02d~ses=%04d~src=%s~rup=%d-%02d' % (
                self.trt_id, ses, self.source_id, self.serial, occ)
            tags.append(tag)
        return numpy.array(tags)

    @property
    def eids(self):
        """
        An array with the underlying event IDs
        """
        return self.events['eid']

    @property
    def multiplicity(self):
        """
        How many times the underlying rupture occurs.
        """
        return len(self.events)

    def export(self, mesh):
        """
        Yield :class:`openquake.commonlib.util.Rupture` objects, with all the
        attributes set, suitable for export in XML format.
        """
        rupture = self.rupture
        for etag in self.etags:
            new = Rupture(etag, self.indices)
            new.mesh = mesh[self.indices]
            new.etag = etag
            new.rupture = new
            new.is_from_fault_source = iffs = isinstance(
                rupture.surface, (geo.ComplexFaultSurface,
                                  geo.SimpleFaultSurface))
            new.is_multi_surface = ims = isinstance(
                rupture.surface, geo.MultiSurface)
            new.lons, new.lats, new.depths = get_geom(
                rupture.surface, iffs, ims)
            new.surface = rupture.surface
            new.strike = rupture.surface.get_strike()
            new.dip = rupture.surface.get_dip()
            new.rake = rupture.rake
            new.hypocenter = rupture.hypocenter
            new.tectonic_region_type = rupture.tectonic_region_type
            new.magnitude = new.mag = rupture.mag
            new.top_left_corner = None if iffs or ims else (
                new.lons[0], new.lats[0], new.depths[0])
            new.top_right_corner = None if iffs or ims else (
                new.lons[1], new.lats[1], new.depths[1])
            new.bottom_left_corner = None if iffs or ims else (
                new.lons[2], new.lats[2], new.depths[2])
            new.bottom_right_corner = None if iffs or ims else (
                new.lons[3], new.lats[3], new.depths[3])
            yield new

    def __lt__(self, other):
        return self.serial < other.serial

    def __repr__(self):
        return '<%s #%d, trt_id=%d>' % (self.__class__.__name__,
                                        self.serial, self.trt_id)


class RuptureFilter(object):
    """
    Implement two filtering mechanism:

    1. if min_iml is empty, use the usual filtering on the maximum distance
    2. otherwise, filter on the ground motion minimum intensity.

    In other words, if a ground motion is below the minimum intensity
    for all hazard sites and for all intensity measure types, ignore
    the rupture. When a RuptureFilter instance is called on a rupture,
    returns None if the rupture has to be discarded, or a
    FilteredSiteCollection with the sites having ground motion intensity
    over the threshold.

    :param sites:
        sites to filter (usually already prefiltered)
    :param maximum_distance:
        the maximum distance to use in the distance filtering
    :param imts:
        a list of intensity measure types
    :param trunc_level:
        the truncation level used in the GMF calculation
    :param min_iml:
        a dictionary with the minimum intensity measure level for each IMT
    """
    def __init__(self, sites, maximum_distance, imts, gsims, trunc_level,
                 min_iml):
        self.sites = sites
        self.max_dist = maximum_distance
        self.imts = imts
        self.gsims = gsims
        self.trunc_level = trunc_level
        self.min_iml = min_iml

    def __call__(self, rupture):
        """
        :returns: a FilteredSiteCollection or None
        """
        if self.min_iml:
            computer = calc.gmf.GmfComputer(
                rupture, self.sites, self.imts, self.gsims, self.trunc_level)
            ok = numpy.zeros(len(self.sites), bool)
            gmf_by_rlz_imt = computer.calcgmfs(1, rupture.seed)
            for rlz, gmf_by_imt in gmf_by_rlz_imt.items():
                for imt, gmf in gmf_by_imt.items():
                    # NB: gmf[:, 0] because the multiplicity is 1
                    ok += gmf[:, 0] >= self.min_iml[imt]
            return computer.sites.filter(ok)
        else:  # maximum_distance filtering
            return filter_sites_by_distance_to_rupture(
                rupture, self.max_dist, self.sites)


def getdefault(dic_with_default, key):
    """
    :param dic_with_default: a dictionary with a 'default' key
    :param key: a key that may be present in the dictionary or not
    :returns: the value associated to the key, or to 'default'
    """
    try:
        return dic_with_default[key]
    except KeyError:
        return dic_with_default['default']


@parallel.litetask
def compute_ruptures(sources, sitecol, siteidx, rlzs_assoc, monitor):
    """
    :param sources:
        List of commonlib.source.Source tuples
    :param sitecol:
        a :class:`openquake.hazardlib.site.SiteCollection` instance
    :param siteidx:
        always equal to 0
    :param rlzs_assoc:
        a :class:`openquake.commonlib.source.RlzsAssoc` instance
    :param monitor:
        monitor instance
    :returns:
        a dictionary trt_model_id -> [Rupture instances]
    """
    assert siteidx == 0, (
        'siteidx can be nonzero only for the classical_tiling calculations: '
        'tiling with the EventBasedRuptureCalculator is an error')
    # NB: by construction each block is a non-empty list with
    # sources of the same trt_model_id
    trt_model_id = sources[0].trt_model_id
    oq = monitor.oqparam
    trt = sources[0].tectonic_region_type
    try:
        max_dist = oq.maximum_distance[trt]
    except KeyError:
        max_dist = oq.maximum_distance['default']
    cmaker = ContextMaker(rlzs_assoc.gsims_by_trt_id[trt_model_id])
    params = cmaker.REQUIRES_RUPTURE_PARAMETERS
    rup_data_dt = numpy.dtype(
        [('rupserial', U32), ('multiplicity', U16), ('numsites', U32)] + [
            (param, F32) for param in params])
    eb_ruptures = []
    rup_data = []
    calc_times = []
    rup_mon = monitor('filtering ruptures', measuremem=False)

    # Compute and save stochastic event sets
    for src in sources:
        t0 = time.time()
        s_sites = src.filter_sites_by_distance_to_source(max_dist, sitecol)
        if s_sites is None:
            continue

        rupture_filter = RuptureFilter(
            s_sites, max_dist, oq.imtls, cmaker.gsims,
            oq.truncation_level, oq.minimum_intensity)
        num_occ_by_rup = sample_ruptures(
            src, oq.ses_per_logic_tree_path, rlzs_assoc.csm_info)
        # NB: the number of occurrences is very low, << 1, so it is
        # more efficient to filter only the ruptures that occur, i.e.
        # to call sample_ruptures *before* the filtering
        for ebr in build_eb_ruptures(
                src, num_occ_by_rup, rupture_filter, oq.random_seed, rup_mon):
            nsites = len(ebr.indices)
            rc = cmaker.make_rupture_context(ebr.rupture)
            ruptparams = tuple(getattr(rc, param) for param in params)
            rup_data.append((ebr.serial, len(ebr.etags), nsites) + ruptparams)
            eb_ruptures.append(ebr)
        dt = time.time() - t0
        calc_times.append((src.id, dt))
    res = AccumDict({trt_model_id: eb_ruptures})
    res.calc_times = calc_times
    res.rup_data = numpy.array(rup_data, rup_data_dt)
    res.trt = trt
    return res


def sample_ruptures(src, num_ses, info):
    """
    Sample the ruptures contained in the given source.

    :param src: a hazardlib source object
    :param num_ses: the number of Stochastic Event Sets to generate
    :param info: a :class:`openquake.commonlib.source.CompositionInfo` instance
    :returns: a dictionary of dictionaries rupture -> {ses_id: num_occurrences}
    """
    # the dictionary `num_occ_by_rup` contains a dictionary
    # ses_id -> num_occurrences for each occurring rupture
    num_occ_by_rup = collections.defaultdict(AccumDict)
    # generating ruptures for the given source
    for rup_no, rup in enumerate(src.iter_ruptures()):
        rup.seed = seed = src.serial[rup_no] + info.seed
        numpy.random.seed(seed)
        for ses_idx in range(1, num_ses + 1):
            num_occurrences = rup.sample_number_of_occurrences()
            if num_occurrences:
                num_occ_by_rup[rup] += {ses_idx: num_occurrences}
        rup.rup_no = rup_no + 1
    return num_occ_by_rup


def build_eb_ruptures(
        src, num_occ_by_rup, rupture_filter, random_seed, rup_mon):
    """
    Filter the ruptures stored in the dictionary num_occ_by_rup and
    yield pairs (rupture, <list of associated EBRuptures>)
    """
    for rup in sorted(num_occ_by_rup, key=operator.attrgetter('rup_no')):
        with rup_mon:
            r_sites = rupture_filter(rup)
        if r_sites is None:
            # ignore ruptures which are far away
            del num_occ_by_rup[rup]  # save memory
            continue

        # creating EBRuptures
        serial = rup.seed - random_seed + 1
        events = []
        for ses_idx, num_occ in sorted(
                num_occ_by_rup[rup].items()):
            for occ_no in range(1, num_occ + 1):
                # NB: the 0 below is a placeholder; the right eid will be
                # set later, in EventBasedRuptureCalculator.post_execute
                events.append((0, ses_idx, occ_no))
        if events:
            yield EBRupture(rup, r_sites.indices,
                            numpy.array(events, event_dt),
                            src.source_id, src.trt_model_id, serial)


def get_gmvs_by_sid(gmfa):
    """
    Returns a dictionary sid -> array of composite ground motion values
    """
    return groupby(gmfa, operator.itemgetter('sid'), lambda group:
                   numpy.array([record['gmv'] for record in group]))


def fix_minimum_intensity(min_iml, imts):
    """
    Make sure the dictionary minimum_intensity (provided by the user in the
    job.ini file) is filled for all intensity measure types and has no key
    named 'default'. Here is how it works:

    >>> min_iml = {'PGA': 0.1, 'default': 0.05}
    >>> fix_minimum_intensity(min_iml, ['PGA', 'PGV'])
    >>> sorted(min_iml.items())
    [('PGA', 0.1), ('PGV', 0.05)]
    """
    if min_iml:
        for imt in imts:
            try:
                min_iml[imt] = getdefault(min_iml, imt)
            except KeyError:
                raise ValueError(
                    'The parameter `minimum_intensity` in the job.ini '
                    'file is missing the IMT %r' % imt)
    if 'default' in min_iml:
        del min_iml['default']


@base.calculators.add('event_based_rupture')
class EventBasedRuptureCalculator(ClassicalCalculator):
    """
    Event based PSHA calculator generating the ruptures only
    """
    core_task = compute_ruptures
    etags = datastore.persistent_attribute('etags')
    is_stochastic = True

    def init(self):
        """
        Set the random seed passed to the SourceManager and the
        minimum_intensity dictionary.
        """
        oq = self.oqparam
        self.random_seed = oq.random_seed
        fix_minimum_intensity(oq.minimum_intensity, oq.imtls)

    def count_eff_ruptures(self, ruptures_by_trt_id, trt_model):
        """
        Returns the number of ruptures sampled in the given trt_model.

        :param ruptures_by_trt_id: a dictionary with key trt_id
        :param trt_model: a TrtModel instance
        """
        return sum(
            len(ruptures) for trt_id, ruptures in ruptures_by_trt_id.items()
            if trt_model.id == trt_id)

    def agg_curves(self, acc, val):
        """
        For the rupture calculator, increment the AccumDict trt_id -> ruptures
        and save the rup_data
        """
        acc += val
        if len(val.rup_data):
            try:
                dset = self.rup_data[val.trt]
            except KeyError:
                dset = self.rup_data[val.trt] = self.datastore.create_dset(
                    'rup_data/' + val.trt, val.rup_data.dtype)
            dset.extend(val.rup_data)

    def zerodict(self):
        """
        Initial accumulator, a dictionary trt_model_id -> list of ruptures
        """
        smodels = self.rlzs_assoc.csm_info.source_models
        zd = AccumDict((tm.id, []) for smodel in smodels
                       for tm in smodel.trt_models)
        zd.calc_times = []
        return zd

    def post_execute(self, result):
        """
        Save the SES collection
        """
        logging.info('Generated %d EBRuptures',
                     sum(len(v) for v in result.values()))
        with self.monitor('saving ruptures', autoflush=True):
            # ordering ruptures
            sescollection = []
            for trt_id in result:
                for ebr in result[trt_id]:
                    sescollection.append(ebr)
            sescollection.sort(key=operator.attrgetter('serial'))
            etags = numpy.concatenate([ebr.etags for ebr in sescollection])
            self.etags = numpy.array(etags, (bytes, 100))
            nr = len(sescollection)
            logging.info('Saving SES collection with %d ruptures', nr)
            eid = 0
            for ebr in sescollection:
                eids = []
                for event in ebr.events:
                    event['eid'] = eid
                    eids.append(eid)
                    eid += 1
                self.datastore['sescollection/%s' % ebr.serial] = ebr
            self.datastore.set_nbytes('sescollection')
        for dset in self.rup_data.values():
            numsites = dset.dset['numsites']
            multiplicity = dset.dset['multiplicity']
            spr = numpy.average(numsites, weights=multiplicity)
            mul = numpy.average(multiplicity, weights=numsites)
            self.datastore.set_attrs(dset.name, sites_per_rupture=spr,
                                     multiplicity=mul)
        self.datastore.set_nbytes('rup_data')


# ######################## GMF calculator ############################ #

def make_gmfs(eb_ruptures, sitecol, imts, rlzs_assoc,
              trunc_level, correl_model, monitor=Monitor()):
    """
    :param eb_ruptures: a list of EBRuptures with the same trt_model_id
    :param sitecol: a SiteCollection instance
    :param imts: a list of Intensity Measure Types
    :param rlzs_assoc: a RlzsAssoc instance
    :param trunc_level: truncation level
    :param correl_model: correlation model instance
    :param monitor: a monitor instance
    :returns: a dictionary rlzi -> gmv_dt array
    """
    trt_id = eb_ruptures[0].trt_id
    gsims = rlzs_assoc.gsims_by_trt_id[trt_id]
    dic = collections.defaultdict(list)  # rlzi -> [gmfa, ...]
    ctx_mon = monitor('make contexts')
    gmf_mon = monitor('compute poes')
    sites = sitecol.complete
    for ebr in eb_ruptures:
        with ctx_mon:
            r_sites = site.FilteredSiteCollection(ebr.indices, sites)
            computer = calc.gmf.GmfComputer(
                ebr.rupture, r_sites, imts, gsims, trunc_level, correl_model)
        with gmf_mon:
            for gsim in gsims:
                for i, rlz in enumerate(rlzs_assoc[trt_id, str(gsim)]):
                    seed = ebr.rupture.seed + i
                    gmfa = computer.compute(seed, gsim, ebr.eids)
                    dic[rlz.ordinal].append(gmfa)
    res = {rlzi: numpy.concatenate(dic[rlzi]) for rlzi in dic}
    return res


@parallel.litetask
def compute_gmfs_and_curves(eb_ruptures, sitecol, imts, rlzs_assoc, monitor):
    """
    :param eb_ruptures:
        a list of blocks of EBRuptures of the same SESCollection
    :param sitecol:
        a :class:`openquake.hazardlib.site.SiteCollection` instance
    :param imts:
        a list of IMT string
    :param rlzs_assoc:
        a RlzsAssoc instance
    :param monitor:
        a Monitor instance
    :returns:
        a dictionary (rlzi, imt) -> [gmfarray, haz_curves]
   """
    oq = monitor.oqparam
    # NB: by construction each block is a non-empty list with
    # ruptures of the same trt_model_id
    trunc_level = oq.truncation_level
    correl_model = readinput.get_correl_model(oq)
    tot_sites = len(sitecol.complete)
    gmfadict = make_gmfs(
        eb_ruptures, sitecol, imts, rlzs_assoc, trunc_level, correl_model,
        monitor)
    result = {rlzi: [gmfadict[rlzi], None]
              if oq.ground_motion_fields else [None, None]
              for rlzi in gmfadict}
    if oq.hazard_curves_from_gmfs:
        with monitor('bulding hazard curves', measuremem=False):
            duration = oq.investigation_time * oq.ses_per_logic_tree_path
            for rlzi in gmfadict:
                gmvs_by_sid = get_gmvs_by_sid(gmfadict[rlzi])
                curves = zero_curves(tot_sites, oq.imtls)
                for imt in oq.imtls:
                    imls = numpy.array(oq.imtls[imt])
                    for sid in range(tot_sites):
                        try:
                            gmvs = gmvs_by_sid[sid]
                        except KeyError:
                            continue
                        curves[imt][sid] = gmvs_to_haz_curve(
                            gmvs[imt], imls, oq.investigation_time, duration)
                result[rlzi][HAZCURVES] = curves
    return result


@base.calculators.add('event_based')
class EventBasedCalculator(ClassicalCalculator):
    """
    Event based PSHA calculator generating the ground motion fields and
    the hazard curves from the ruptures, depending on the configuration
    parameters.
    """
    pre_calculator = 'event_based_rupture'
    core_task = compute_gmfs_and_curves
    is_stochastic = True

    def pre_execute(self):
        """
        Read the precomputed ruptures (or compute them on the fly) and
        prepare some empty files in the export directory to store the gmfs
        (if any). If there were pre-existing files, they will be erased.
        """
        super(EventBasedCalculator, self).pre_execute()
        self.sesruptures = []
        for serial in self.datastore['sescollection']:
            self.sesruptures.append(self.datastore['sescollection/' + serial])
        self.sesruptures.sort(key=operator.attrgetter('serial'))
        gmv_dt = calc.gmf.gmv_dt(self.oqparam.imtls)
        if self.oqparam.ground_motion_fields:
            for rlz in self.rlzs_assoc.realizations:
                self.datastore.create_dset(
                    'gmf_data/%04d' % rlz.ordinal, gmv_dt)

    def combine_curves_and_save_gmfs(self, acc, res):
        """
        Combine the hazard curves (if any) and save the gmfs (if any)
        sequentially; notice that the gmfs may come from
        different tasks in any order.

        :param acc: an accumulator for the hazard curves
        :param res: a dictionary rlzi, imt -> [gmf_array, curves_by_imt]
        :returns: a new accumulator
        """
        sav_mon = self.monitor('saving gmfs')
        agg_mon = self.monitor('aggregating hcurves')
        for rlzi in res:
            gmfa, curves = res[rlzi]
            if gmfa is not None:
                with sav_mon:
                    hdf5.extend(self.datastore['gmf_data/%04d' % rlzi], gmfa)
            if curves is not None:  # aggregate hcurves
                with agg_mon:
                    self.agg_dicts(acc, {rlzi: curves})
        sav_mon.flush()
        agg_mon.flush()
        return acc

    def execute(self):
        """
        Run in parallel `core_task(sources, sitecol, monitor)`, by
        parallelizing on the ruptures according to their weight and
        tectonic region type.
        """
        oq = self.oqparam
        if not oq.hazard_curves_from_gmfs and not oq.ground_motion_fields:
            return
        monitor = self.monitor(self.core_task.__name__)
        monitor.oqparam = oq
        zc = zero_curves(len(self.sitecol.complete), self.oqparam.imtls)
        zerodict = AccumDict({rlz.ordinal: zc
                              for rlz in self.rlzs_assoc.realizations})
        acc = parallel.apply_reduce(
            self.core_task.__func__,
            (self.sesruptures, self.sitecol, oq.imtls, self.rlzs_assoc,
             monitor),
            concurrent_tasks=self.oqparam.concurrent_tasks,
            acc=zerodict, agg=self.combine_curves_and_save_gmfs,
            key=operator.attrgetter('trt_id'),
            weight=operator.attrgetter('multiplicity'))
        if oq.ground_motion_fields:
            self.datastore.set_nbytes('gmf_data')
        return acc

    def post_execute(self, result):
        """
        :param result:
            a dictionary (trt_model_id, gsim) -> haz_curves or an empty
            dictionary if hazard_curves_from_gmfs is false
        """
        oq = self.oqparam
        if not oq.hazard_curves_from_gmfs and not oq.ground_motion_fields:
            return
        elif oq.hazard_curves_from_gmfs:
            rlzs = self.rlzs_assoc.realizations
            self.save_curves({rlzs[rlzi]: result[rlzi] for rlzi in result})
        if oq.compare_with_classical:  # compute classical curves
            export_dir = os.path.join(oq.export_dir, 'cl')
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            oq.export_dir = export_dir
            # use a different datastore
            self.cl = ClassicalCalculator(oq, self.monitor)
            # TODO: perhaps it is possible to avoid reprocessing the source
            # model, however usually this is quite fast and do not dominate
            # the computation
            self.cl.run(hazard_calculation_id=self.datastore.calc_id)
            for imt in self.mean_curves.dtype.fields:
                rdiff, index = max_rel_diff_index(
                    self.cl.mean_curves[imt], self.mean_curves[imt])
                logging.warn('Relative difference with the classical '
                             'mean curves for IMT=%s: %d%% at site index %d',
                             imt, rdiff * 100, index)
