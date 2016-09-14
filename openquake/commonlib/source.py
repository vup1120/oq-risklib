# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2010-2016 GEM Foundation
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
import sys
import copy
import math
import logging
import operator
import collections
import random
from xml.etree import ElementTree as etree

import numpy

from openquake.baselib.python3compat import raise_
from openquake.baselib.general import (
    AccumDict, groupby, block_splitter, group_array)
from openquake.hazardlib.site import Tile
from openquake.hazardlib.probability_map import ProbabilityMap
from openquake.commonlib.node import read_nodes
from openquake.commonlib import logictree, sourceconverter, parallel, valid
from openquake.commonlib.nrml import nodefactory, PARSE_NS_MAP

MAX_INT = 2 ** 31 - 1
U16 = numpy.uint16
U32 = numpy.uint32
I32 = numpy.int32
F32 = numpy.float32


class DuplicatedID(Exception):
    """Raised when two sources with the same ID are found in a source model"""


class LtRealization(object):
    """
    Composite realization build on top of a source model realization and
    a GSIM realization.
    """
    def __init__(self, ordinal, sm_lt_path, gsim_rlz, weight, sampleid):
        self.ordinal = ordinal
        self.sm_lt_path = sm_lt_path
        self.gsim_rlz = gsim_rlz
        self.weight = weight
        self.sampleid = sampleid

    def __repr__(self):
        return '<%d,%s,w=%s>' % (self.ordinal, self.uid, self.weight)

    @property
    def gsim_lt_path(self):
        return self.gsim_rlz.lt_path

    @property
    def uid(self):
        """An unique identifier for effective realizations"""
        return '_'.join(self.sm_lt_path) + ',' + self.gsim_rlz.uid

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __ne__(self, other):
        return repr(self) != repr(other)

    def __hash__(self):
        return hash(repr(self))


class SourceModel(object):
    """
    A container of TrtModel instances with some additional attributes
    describing the source model in the logic tree.
    """
    def __init__(self, name, weight, path, trt_models, gsim_lt, ordinal,
                 samples):
        self.name = name
        self.weight = weight
        self.path = path
        self.trt_models = trt_models
        self.gsim_lt = gsim_lt
        self.ordinal = ordinal
        self.samples = samples

    @property
    def num_sources(self):
        return sum(len(tm) for tm in self.trt_models)

    def num_gsim_paths(self, number_of_logic_tree_samples=0):
        return (self.samples if number_of_logic_tree_samples
                else self.gsim_lt.get_num_paths())

    def get_skeleton(self):
        """
        Return an empty copy of the source model, i.e. without sources,
        but with the proper attributes for each TrtModel contained within.
        """
        trt_models = [TrtModel(tm.trt, [], tm.min_mag, tm.max_mag, tm.id)
                      for tm in self.trt_models]
        return self.__class__(self.name, self.weight, self.path, trt_models,
                              self.gsim_lt, self.ordinal, self.samples)


def capitalize(words):
    """
    Capitalize words separated by spaces.

    >>> capitalize('active shallow crust')
    'Active Shallow Crust'
    """
    return ' '.join(w.capitalize() for w in words.split(' '))


class TrtModel(collections.Sequence):
    """
    A container for the following parameters:

    :param str trt:
        the tectonic region type all the sources belong to
    :param list sources:
        a list of hazardlib source objects
    :param min_mag:
        the minimum magnitude among the given sources
    :param max_mag:
        the maximum magnitude among the given sources
    :param gsims:
        the GSIMs associated to tectonic region type
    :param id:
        an optional numeric ID (default None) useful to associate
        the model to a database object
    """
    @classmethod
    def collect(cls, sources):
        """
        :param sources: dictionaries with a key 'tectonicRegion'
        :returns: an ordered list of TrtModel instances
        """
        source_stats_dict = {}
        for src in sources:
            trt = src['tectonicRegion']
            if trt not in source_stats_dict:
                source_stats_dict[trt] = TrtModel(trt)
            tm = source_stats_dict[trt]
            if not tm.sources:
                # we append just one source per TRTModel, so that
                # the memory occupation is insignificant
                tm.sources.append(src)

        # return TrtModels, ordered by TRT string
        return sorted(source_stats_dict.values())

    def __init__(self, trt, sources=None,
                 min_mag=None, max_mag=None, id=0, eff_ruptures=-1):
        self.trt = trt
        self.sources = sources or []
        self.min_mag = min_mag
        self.max_mag = max_mag
        self.id = id
        for src in self.sources:
            self.update(src)
        self.source_model = None  # to be set later, in CompositionInfo
        self.weight = 1
        self.eff_ruptures = eff_ruptures  # set later nby get_rlzs_assoc

    def tot_ruptures(self):
        return sum(src.num_ruptures for src in self.sources)

    def update(self, src):
        """
        Update the attributes sources, min_mag, max_mag
        according to the given source.

        :param src:
            an instance of :class:
            `openquake.hazardlib.source.base.BaseSeismicSource`
        """
        assert src.tectonic_region_type == self.trt, (
            src.tectonic_region_type, self.trt)
        self.sources.append(src)
        min_mag, max_mag = src.get_min_max_mag()
        prev_min_mag = self.min_mag
        if prev_min_mag is None or min_mag < prev_min_mag:
            self.min_mag = min_mag
        prev_max_mag = self.max_mag
        if prev_max_mag is None or max_mag > prev_max_mag:
            self.max_mag = max_mag

    def __repr__(self):
        return '<%s #%d %s, %d source(s), %d effective rupture(s)>' % (
            self.__class__.__name__, self.id, self.trt,
            len(self.sources), self.eff_ruptures)

    def __lt__(self, other):
        """
        Make sure there is a precise ordering of TrtModel objects.
        Objects with less sources are put first; in case the number
        of sources is the same, use lexicographic ordering on the trts
        """
        num_sources = len(self.sources)
        other_sources = len(other.sources)
        if num_sources == other_sources:
            return self.trt < other.trt
        return num_sources < other_sources

    def __getitem__(self, i):
        return self.sources[i]

    def __iter__(self):
        return iter(self.sources)

    def __len__(self):
        return len(self.sources)


class SourceModelParser(object):
    """
    A source model parser featuring a cache.

    :param converter:
        :class:`openquake.commonlib.source.SourceConverter` instance
    """
    def __init__(self, converter):
        self.converter = converter
        self.sources = {}  # cache fname -> sources
        self.fname_hits = collections.Counter()  # fname -> number of calls

    def parse_trt_models(self, fname, apply_uncertainties=None):
        """
        :param fname:
            the full pathname of the source model file
        :param apply_uncertainties:
            a function modifying the sources (or None)
        """
        try:
            sources = self.sources[fname]
        except KeyError:
            sources = self.sources[fname] = self.parse_sources(fname)
        # NB: deepcopy is *essential* here
        sources = map(copy.deepcopy, sources)
        for src in sources:
            if apply_uncertainties:
                apply_uncertainties(src)
                src.num_ruptures = src.count_ruptures()
        self.fname_hits[fname] += 1

        # build ordered TrtModels
        trts = {}
        for src in sources:
            trt = src.tectonic_region_type
            if trt not in trts:
                trts[trt] = TrtModel(trt)
            trts[trt].update(src)
        return sorted(trts.values())

    def parse_sources(self, fname):
        """
        Parse all the sources and return them ordered by tectonic region type.
        It does not count the ruptures, so it is relatively fast.

        :param fname:
            the full pathname of the source model file
        """
        sources = []
        source_ids = set()
        self.converter.fname = fname
        src_nodes = read_nodes(fname, lambda elem: 'Source' in elem.tag,
                               nodefactory['sourceModel'])
        for no, src_node in enumerate(src_nodes, 1):
            src = self.converter.convert_node(src_node)
            if src.source_id in source_ids:
                raise DuplicatedID(
                    'The source ID %s is duplicated!' % src.source_id)
            sources.append(src)
            source_ids.add(src.source_id)
            if no % 10000 == 0:  # log every 10,000 sources parsed
                logging.info('Parsed %d sources from %s', no, fname)
        if no % 10000 != 0:
            logging.info('Parsed %d sources from %s', no, fname)
        return sorted(sources, key=operator.attrgetter('tectonic_region_type'))


def agg_prob(acc, prob):
    """Aggregation function for probabilities"""
    return 1. - (1. - acc) * (1. - prob)


class RlzsAssoc(collections.Mapping):
    """
    Realization association class. It should not be instantiated directly,
    but only via the method :meth:
    `openquake.commonlib.source.CompositeSourceModel.get_rlzs_assoc`.

    :attr realizations: list of LtRealization objects
    :attr gsim_by_trt: list of dictionaries {trt: gsim}
    :attr rlzs_assoc: dictionary {trt_model_id, gsim: rlzs}
    :attr rlzs_by_smodel: list of lists of realizations

    For instance, for the non-trivial logic tree in
    :mod:`openquake.qa_tests_data.classical.case_15`, which has 4 tectonic
    region types and 4 + 2 + 2 realizations, there are the following
    associations:

    (0, 'BooreAtkinson2008()') ['#0-SM1-BA2008_C2003', '#1-SM1-BA2008_T2002']
    (0, 'CampbellBozorgnia2008()') ['#2-SM1-CB2008_C2003', '#3-SM1-CB2008_T2002']
    (1, 'Campbell2003()') ['#0-SM1-BA2008_C2003', '#2-SM1-CB2008_C2003']
    (1, 'ToroEtAl2002()') ['#1-SM1-BA2008_T2002', '#3-SM1-CB2008_T2002']
    (2, 'BooreAtkinson2008()') ['#4-SM2_a3pt2b0pt8-BA2008']
    (2, 'CampbellBozorgnia2008()') ['#5-SM2_a3pt2b0pt8-CB2008']
    (3, 'BooreAtkinson2008()') ['#6-SM2_a3b1-BA2008']
    (3, 'CampbellBozorgnia2008()') ['#7-SM2_a3b1-CB2008']
    """
    def __init__(self, csm_info):
        self.seed = csm_info.seed
        self.num_samples = csm_info.num_samples
        self.rlzs_assoc = collections.defaultdict(list)
        self.gsim_by_trt = []  # rlz.ordinal -> {trt: gsim}
        self.rlzs_by_smodel = [[] for _ in range(len(csm_info.source_models))]
        self.gsims_by_trt_id = {}
        self.sm_ids = {}
        self.samples = {}
        for sm in csm_info.source_models:
            for tm in sm.trt_models:
                self.sm_ids[tm.id] = sm.ordinal
                self.samples[tm.id] = sm.samples

    def _init(self):
        """
        Finalize the initialization of the RlzsAssoc object by setting
        the (reduced) weights of the realizations and the attribute
        gsims_by_trt_id.
        """
        if self.num_samples:
            assert len(self.realizations) == self.num_samples
            for rlz in self.realizations:
                rlz.weight = 1. / self.num_samples
        else:
            tot_weight = sum(rlz.weight for rlz in self.realizations)
            if tot_weight == 0:
                raise ValueError('All realizations have zero weight??')
            elif abs(tot_weight - 1) > 1E-12:  # allow for rounding errors
                logging.warn('Some source models are not contributing, '
                             'weights are being rescaled')
            for rlz in self.realizations:
                rlz.weight = rlz.weight / tot_weight

        self.gsims_by_trt_id = groupby(
            self.rlzs_assoc, operator.itemgetter(0),
            lambda group: sorted(gsim for trt_id, gsim in group))

    @property
    def realizations(self):
        """Flat list with all the realizations"""
        return sum(self.rlzs_by_smodel, [])

    def get_rlzs_by_gsim(self, trt_id):
        """
        Returns a dictionary gsim -> rlzs
        """
        return {gsim: self[trt_id, str(gsim)]
                for gsim in self.gsims_by_trt_id[trt_id]}

    def get_rlzs_by_trt_id(self):
        """
        Returns a dictionary trt_id > [sorted rlzs]
        """
        rlzs_by_trt_id = collections.defaultdict(set)
        for (trt_id, gsim), rlzs in self.rlzs_assoc.items():
            rlzs_by_trt_id[trt_id].update(rlzs)
        return {trt_id: sorted(rlzs)
                for trt_id, rlzs in rlzs_by_trt_id.items()}

    def _add_realizations(self, idx, lt_model, realizations):
        gsim_lt = lt_model.gsim_lt
        trts = gsim_lt.tectonic_region_types
        rlzs = []
        for i, gsim_rlz in enumerate(realizations):
            weight = float(lt_model.weight) * float(gsim_rlz.weight)
            rlz = LtRealization(idx[i], lt_model.path, gsim_rlz, weight, i)
            self.gsim_by_trt.append(
                dict(zip(gsim_lt.all_trts, gsim_rlz.value)))
            for trt_model in lt_model.trt_models:
                if trt_model.trt in trts:
                    # ignore the associations to discarded TRTs
                    gs = gsim_lt.get_gsim_by_trt(gsim_rlz, trt_model.trt)
                    self.rlzs_assoc[trt_model.id, gs].append(rlz)
            rlzs.append(rlz)
        self.rlzs_by_smodel[lt_model.ordinal] = rlzs

    def extract(self, rlz_indices, csm_info):
        """
        Extract a RlzsAssoc instance containing only the given realizations.

        :param rlz_indices: a list of realization indices from 0 to R - 1
        """
        assoc = self.__class__(csm_info)
        if len(rlz_indices) == 1:
            realizations = [self.realizations[rlz_indices[0]]]
        else:
            realizations = operator.itemgetter(*rlz_indices)(self.realizations)
        rlzs_smpath = groupby(realizations, operator.attrgetter('sm_lt_path'))
        smodel_from = {sm.path: sm for sm in csm_info.source_models}
        for smpath, rlzs in rlzs_smpath.items():
            assoc._add_realizations(
                [r.ordinal for r in rlzs], smodel_from[smpath],
                [rlz.gsim_rlz for rlz in rlzs])
        assoc._init()
        return assoc

    # used in classical and event_based calculators
    def combine_curves(self, results):
        """
        :param results: dictionary (trt_model_id, gsim) -> curves
        :returns: a dictionary rlz -> aggregate curves
        """
        acc = {rlz: ProbabilityMap() for rlz in self.realizations}
        for key in results:
            for rlz in self.rlzs_assoc[key]:
                acc[rlz] |= results[key]
        return acc

    # used in riskinput
    def combine(self, results, agg=agg_prob):
        """
        :param results: a dictionary (trt_model_id, gsim) -> floats
        :param agg: an aggregation function
        :returns: a dictionary rlz -> aggregated floats

        Example: a case with tectonic region type T1 with GSIMS A, B, C
        and tectonic region type T2 with GSIMS D, E.

        >> assoc = RlzsAssoc(CompositionInfo([], []))
        >> assoc.rlzs_assoc = {
        ... ('T1', 'A'): ['r0', 'r1'],
        ... ('T1', 'B'): ['r2', 'r3'],
        ... ('T1', 'C'): ['r4', 'r5'],
        ... ('T2', 'D'): ['r0', 'r2', 'r4'],
        ... ('T2', 'E'): ['r1', 'r3', 'r5']}
        ...
        >> results = {
        ... ('T1', 'A'): 0.01,
        ... ('T1', 'B'): 0.02,
        ... ('T1', 'C'): 0.03,
        ... ('T2', 'D'): 0.04,
        ... ('T2', 'E'): 0.05,}
        ...
        >> combinations = assoc.combine(results, operator.add)
        >> for key, value in sorted(combinations.items()): print key, value
        r0 0.05
        r1 0.06
        r2 0.06
        r3 0.07
        r4 0.07
        r5 0.08

        You can check that all the possible sums are performed:

        r0: 0.01 + 0.04 (T1A + T2D)
        r1: 0.01 + 0.05 (T1A + T2E)
        r2: 0.02 + 0.04 (T1B + T2D)
        r3: 0.02 + 0.05 (T1B + T2E)
        r4: 0.03 + 0.04 (T1C + T2D)
        r5: 0.03 + 0.05 (T1C + T2E)

        In reality, the `combine_curves` method is used with hazard_curves and
        the aggregation function is the `agg_curves` function, a composition of
        probability, which however is close to the sum for small probabilities.
        """
        ad = {rlz: 0 for rlz in self.realizations}
        for key, value in results.items():
            for rlz in self.rlzs_assoc[key]:
                ad[rlz] = agg(ad[rlz], value)
        return ad

    def __iter__(self):
        return iter(self.rlzs_assoc)

    def __getitem__(self, key):
        return self.rlzs_assoc[key]

    def __len__(self):
        return len(self.rlzs_assoc)

    def __repr__(self):
        pairs = []
        for key in sorted(self.rlzs_assoc):
            rlzs = list(map(str, self.rlzs_assoc[key]))
            if len(rlzs) > 10:  # short representation
                rlzs = ['%d realizations' % len(rlzs)]
            pairs.append(('%s,%s' % key, rlzs))
        return '<%s(size=%d, rlzs=%d)\n%s>' % (
            self.__class__.__name__, len(self), len(self.realizations),
            '\n'.join('%s: %s' % pair for pair in pairs))

LENGTH = 256

source_model_dt = numpy.dtype([
    ('name', (bytes, LENGTH)),
    ('weight', F32),
    ('path', (bytes, LENGTH)),
    ('num_rlzs', U32),
    ('samples', U32),
])

trt_model_dt = numpy.dtype(
    [('trt_id', U32),
     ('trti', U16),
     ('effrup', I32),
     ('sm_id', U32)])


class CompositionInfo(object):
    """
    An object to collect information about the composition of
    a composite source model.

    :param source_model_lt: a SourceModelLogicTree object
    :param source_models: a list of SourceModel instances
    """
    @classmethod
    def fake(cls, gsimlt=None):
        """
        :returns:
            a fake `CompositionInfo` instance with the given gsim logic tree
            object; if None, builds automatically a fake gsim logic tree
        """
        weight = 1
        fakeSM = SourceModel(
            'fake', weight,  'b1', [TrtModel('*', eff_ruptures=1)],
            gsimlt or logictree.GsimLogicTree.from_('FromFile'),
            ordinal=0, samples=1)
        return cls(seed=0, num_samples=0, source_models=[fakeSM])

    def __init__(self, seed, num_samples, source_models):
        self.seed = seed
        self.num_samples = num_samples
        self.source_models = source_models

    def __getnewargs__(self):
        # with this CompositionInfo instances will be unpickled correctly
        return self.seed, self.num_samples, self.source_models

    def __toh5__(self):
        trts = sorted(set(trt_model.trt for sm in self.source_models
                          for trt_model in sm.trt_models))
        trti = {trt: i for i, trt in enumerate(trts)}
        data = []
        for sm in self.source_models:
            for trt_model in sm.trt_models:
                # the number of effective realizations is set by get_rlzs_assoc
                data.append((trt_model.id, trti[trt_model.trt],
                             trt_model.eff_ruptures, sm.ordinal))
        lst = [(sm.name, sm.weight, '_'.join(sm.path),
                sm.gsim_lt.get_num_paths(), sm.samples)
               for i, sm in enumerate(self.source_models)]
        gsim_lt = self.source_models[0].gsim_lt
        return (dict(
            tm_data=numpy.array(data, trt_model_dt),
            sm_data=numpy.array(lst, source_model_dt)),
                dict(seed=self.seed, num_samples=self.num_samples,
                     trts=trts, gsim_lt_xml=str(gsim_lt),
                     gsim_fname=gsim_lt.fname))

    def __fromh5__(self, dic, attrs):
        tm_data = group_array(dic['tm_data'], 'sm_id')
        sm_data = dic['sm_data']
        vars(self).update(attrs)
        self.source_models = []
        for sm_id, rec in enumerate(sm_data):
            tdata = tm_data[sm_id]
            trtmodels = [
                TrtModel(self.trts[trti], id=trt_id, eff_ruptures=effrup)
                for trt_id, trti, effrup, sm_id in tdata if effrup > 0]
            path = tuple(rec['path'].split('_'))
            trts = set(tm.trt for tm in trtmodels)
            if self.gsim_fname.endswith('.xml'):
                gsim_lt = logictree.GsimLogicTree(self.gsim_fname, trts)
            else:  # fake file with the name of the GSIM
                gsim_lt = logictree.GsimLogicTree.from_(self.gsim_fname)
            sm = SourceModel(rec['name'], rec['weight'], path, trtmodels,
                             gsim_lt, sm_id, rec['samples'])
            self.source_models.append(sm)

    def get_num_rlzs(self, source_model=None):
        """
        :param source_model: a SourceModel instance (or None)
        :returns: the number of realizations per source model (or all)
        """
        if source_model is None:
            return sum(self.get_num_rlzs(sm) for sm in self.source_models)
        if self.num_samples:
            return source_model.samples
        return source_model.gsim_lt.get_num_paths()

    def get_rlzs_assoc(self, count_ruptures=None):
        """
        Return a RlzsAssoc with fields realizations, gsim_by_trt,
        rlz_idx and trt_gsims.

        :param count_ruptures: a function trt_model -> num_ruptures
        """
        assoc = RlzsAssoc(self)
        random_seed = self.seed
        idx = 0
        for i, smodel in enumerate(self.source_models):
            # collect the effective tectonic region types and ruptures
            trts = set()
            for tm in smodel.trt_models:
                if count_ruptures:
                    tm.eff_ruptures = count_ruptures(tm)
                if tm.eff_ruptures:
                    trts.add(tm.trt)
            # recompute the GSIM logic tree if needed
            if trts != set(smodel.gsim_lt.tectonic_region_types):
                before = smodel.gsim_lt.get_num_paths()
                smodel.gsim_lt.reduce(trts)
                after = smodel.gsim_lt.get_num_paths()
                logging.warn('Reducing the logic tree of %s from %d to %d '
                             'realizations', smodel.name, before, after)
            if self.num_samples:  # sampling
                rnd = random.Random(random_seed + idx)
                rlzs = logictree.sample(smodel.gsim_lt, smodel.samples, rnd)
            else:  # full enumeration
                rlzs = logictree.get_effective_rlzs(smodel.gsim_lt)
            if rlzs:
                indices = numpy.arange(idx, idx + len(rlzs))
                idx += len(indices)
                assoc._add_realizations(indices, smodel, rlzs)
            elif trts:
                logging.warn('No realizations for %s, %s',
                             '_'.join(smodel.path), smodel.name)
        # NB: realizations could be filtered away by logic tree reduction
        if assoc.realizations:
            assoc._init()
        return assoc

    def get_source_model(self, trt_model_id):
        """
        Return the source model for the given trt_model_id
        """
        for smodel in self.source_models:
            for trt_model in smodel.trt_models:
                if trt_model.id == trt_model_id:
                    return smodel

    def get_trt(self, trt_model_id):
        """
        Return the TRT string for the given trt_model_id
        """
        for smodel in self.source_models:
            for trt_model in smodel.trt_models:
                if trt_model.id == trt_model_id:
                    return trt_model.trt

    def __repr__(self):
        info_by_model = collections.OrderedDict(
            (sm.path, ('_'.join(sm.path), sm.name,
                       [tm.id for tm in sm.trt_models],
                       sm.weight, self.get_num_rlzs(sm)))
            for sm in self.source_models)
        summary = ['%s, %s, trt=%s, weight=%s: %d realization(s)' % ibm
                   for ibm in info_by_model.values()]
        return '<%s\n%s>' % (
            self.__class__.__name__, '\n'.join(summary))


class CompositeSourceModel(collections.Sequence):
    """
    :param source_model_lt:
        a :class:`openquake.commonlib.logictree.SourceModelLogicTree` instance
    :param source_models:
        a list of :class:`openquake.commonlib.source.SourceModel` tuples
    """
    def __init__(self, source_model_lt, source_models, set_weight=True):
        self.source_model_lt = source_model_lt
        self.source_models = source_models
        self.source_info = ()  # set by the SourceFilterSplitter
        self.split_map = {}
        if set_weight:
            self.set_weights()
        # must go after set_weights to have the correct .num_ruptures
        self.info = CompositionInfo(
            self.source_model_lt.seed,
            self.source_model_lt.num_samples,
            [sm.get_skeleton() for sm in self.source_models])

    @property
    def trt_models(self):
        """
        Yields the TrtModels inside each source model.
        """
        for sm in self.source_models:
            for trt_model in sm.trt_models:
                yield trt_model

    def get_sources(self, kind='all'):
        """
        Extract the sources contained in the source models by optionally
        filtering and splitting them, depending on the passed parameters.
        """
        sources = []
        maxweight = self.maxweight
        for trt_model in self.trt_models:
            for src in trt_model:
                if kind == 'all':
                    sources.append(src)
                elif kind == 'light' and src.weight <= maxweight:
                    sources.append(src)
                elif kind == 'heavy' and src.weight > maxweight:
                    sources.append(src)
        return sources

    def get_num_sources(self):
        """
        :returns: the total number of sources in the model
        """
        return sum(len(trt_model) for trt_model in self.trt_models)

    def set_weights(self):
        """
        Update the attributes .weight and src.num_ruptures for each TRT model
        .weight of the CompositeSourceModel.
        """
        self.weight = self.filtered_weight = 0
        for trt_model in self.trt_models:
            weight = 0
            num_ruptures = 0
            for src in trt_model:
                weight += src.weight
                num_ruptures += src.num_ruptures
            trt_model.weight = weight
            trt_model.sources = sorted(
                trt_model, key=operator.attrgetter('source_id'))
            self.weight += weight

    def __repr__(self):
        """
        Return a string representation of the composite model
        """
        models = ['%d-%s-%s,w=%s [%d trt_model(s)]' % (
            sm.ordinal, sm.name, '_'.join(sm.path), sm.weight,
            len(sm.trt_models)) for sm in self.source_models]
        return '<%s\n%s>' % (self.__class__.__name__, '\n'.join(models))

    def __getitem__(self, i):
        """Return the i-th source model"""
        return self.source_models[i]

    def __iter__(self):
        """Return an iterator over the underlying source models"""
        return iter(self.source_models)

    def __len__(self):
        """Return the number of underlying source models"""
        return len(self.source_models)


def collect_source_model_paths(smlt):
    """
    Given a path to a source model logic tree or a file-like, collect all of
    the soft-linked path names to the source models it contains and return them
    as a uniquified list (no duplicates).

    :param smlt: source model logic tree file
    """
    src_paths = []
    try:
        tree = etree.parse(smlt)
        for branch_set in tree.findall('.//nrml:logicTreeBranchSet',
                                       namespaces=PARSE_NS_MAP):

            if branch_set.get('uncertaintyType') == 'sourceModel':
                for branch in branch_set.findall(
                        './nrml:logicTreeBranch/nrml:uncertaintyModel',
                        namespaces=PARSE_NS_MAP):
                    src_paths.append(branch.text)
    except Exception as exc:
        raise Exception('%s: %s in %s' % (exc.__class__.__name__, exc, smlt))
    return sorted(set(src_paths))


# ########################## SourceManager ########################### #

def source_info_iadd(self, other):
    assert self.trt_model_id == other.trt_model_id
    assert self.source_id == other.source_id
    return self.__class__(
        self.trt_model_id, self.source_id, self.source_class, self.weight,
        self.sources, self.filter_time + other.filter_time,
        self.split_time + other.split_time, self.calc_time + other.calc_time)

SourceInfo = collections.namedtuple(
    'SourceInfo', 'trt_model_id source_id source_class weight sources '
    'filter_time split_time calc_time')
SourceInfo.__iadd__ = source_info_iadd

source_info_dt = numpy.dtype([
    ('trt_model_id', numpy.uint32),  # 0
    ('source_id', (bytes, valid.MAX_ID_LENGTH)),  # 1
    ('source_class', (bytes, 30)),   # 2
    ('weight', numpy.float32),       # 3
    ('split_num', numpy.uint32),     # 4
    ('filter_time', numpy.float32),  # 5
    ('split_time', numpy.float32),   # 6
    ('calc_time', numpy.float32),    # 7
])


source_chunk_dt = numpy.dtype([
    ('num_sources', numpy.uint32),
    ('weight', numpy.float32),
    ('sent', numpy.int32)])


class SourceManager(object):
    """
    Manager associated to a CompositeSourceModel instance.
    Filter and split sources and send them to the worker tasks.
    """
    def __init__(self, csm, taskfunc, maximum_distance,
                 dstore, monitor, random_seed=None,
                 filter_sources=True, num_tiles=1):
        self.tm = parallel.TaskManager(taskfunc)
        self.csm = csm
        self.maximum_distance = maximum_distance
        self.random_seed = random_seed
        self.dstore = dstore
        self.monitor = monitor
        self.filter_sources = filter_sources
        self.num_tiles = num_tiles
        self.rlzs_assoc = csm.info.get_rlzs_assoc()
        self.split_map = {}  # trt_model_id, source_id -> split sources
        self.source_chunks = []
        self.infos = {}  # trt_model_id, source_id -> SourceInfo tuple
        if random_seed is not None:
            # generate unique seeds for each rupture with numpy.arange
            self.src_serial = {}
            n = sum(trtmod.tot_ruptures() for trtmod in self.csm.trt_models)
            rup_serial = numpy.arange(n, dtype=numpy.uint32)
            start = 0
            for src in self.csm.get_sources('all'):
                nr = src.num_ruptures
                self.src_serial[src.id] = rup_serial[start:start + nr]
                start += nr
        # decrease the weight with the number of tiles, to increase
        # the number of generated tasks; this is an heuristic trick
        self.maxweight = self.csm.maxweight * math.sqrt(num_tiles) / 2.
        logging.info('Instantiated SourceManager with maxweight=%.1f',
                     self.maxweight)

    def get_sources(self, kind, tile):
        """
        :param kind: a string 'light', 'heavy' or 'all'
        :param tile: a :class:`openquake.hazardlib.site.Tile` instance
        :returns: the sources of the given kind affecting the given tile
        """
        filter_mon = self.monitor('filtering sources')
        split_mon = self.monitor('splitting sources')
        for src in self.csm.get_sources(kind):
            filter_time = split_time = 0
            if self.filter_sources:
                with filter_mon:
                    try:
                        if src not in tile:
                            continue
                    except:
                        etype, err, tb = sys.exc_info()
                        msg = 'An error occurred with source id=%s: %s'
                        msg %= (src.source_id, err)
                        raise_(etype, msg, tb)
                filter_time = filter_mon.dt
            if kind == 'heavy':
                if (src.trt_model_id, src.id) not in self.split_map:
                    logging.info('splitting %s of weight %s',
                                 src, src.weight)
                    with split_mon:
                        sources = list(sourceconverter.split_source(src))
                        self.split_map[src.trt_model_id, src.id] = sources
                    split_time = split_mon.dt
                    self.set_serial(src, sources)
                for ss in self.split_map[src.trt_model_id, src.id]:
                    ss.id = src.id
                    yield ss
            else:
                self.set_serial(src)
                yield src
            split_sources = self.split_map.get(
                (src.trt_model_id, src.id), [src])
            info = SourceInfo(src.trt_model_id, src.source_id,
                              src.__class__.__name__,
                              src.weight, len(split_sources),
                              filter_time, split_time, 0)
            key = (src.trt_model_id, src.source_id)
            if key in self.infos:
                self.infos[key] += info
            else:
                self.infos[key] = info

        filter_mon.flush()
        split_mon.flush()

    def set_serial(self, src, split_sources=()):
        """
        Set a serial number per each rupture in a source, managing also the
        case of split sources, if any.
        """
        if self.random_seed is not None:
            src.serial = self.src_serial[src.id]
            if split_sources:
                start = 0
                for ss in split_sources:
                    nr = ss.num_ruptures
                    ss.serial = src.serial[start:start + nr]
                    start += nr

    def submit_sources(self, sitecol, siteidx=0):
        """
        Submit the light sources and then the (split) heavy sources.
        Only the sources affecting the sitecol as considered.
        """
        tile = Tile(sitecol, self.maximum_distance)
        for kind in ('light', 'heavy'):
            if self.filter_sources:
                logging.info('Filtering %s sources', kind)
            sources = list(self.get_sources(kind, tile))
            if not sources:
                continue
            for src in sources:
                self.csm.filtered_weight += src.weight
            nblocks = 0
            for block in block_splitter(
                    sources, self.maxweight,
                    operator.attrgetter('weight'),
                    operator.attrgetter('trt_model_id')):
                sent = self.tm.submit(block, sitecol, siteidx,
                                      self.rlzs_assoc, self.monitor.new())
                self.source_chunks.append(
                    (len(block), block.weight, sum(sent.values())))
                nblocks += 1
            logging.info('Sent %d sources in %d block(s)',
                         len(sources), nblocks)

    def store_source_info(self, dstore):
        """
        Save the `source_info` array and its attributes in the datastore.

        :param dstore: the datastore
        """
        if self.infos:
            values = self.infos.values()
            values.sort(
                key=lambda info: info.filter_time + info.split_time,
                reverse=True)
            dstore['source_info'] = numpy.array(values, source_info_dt)
            attrs = dstore['source_info'].attrs
            attrs['maxweight'] = self.csm.maxweight
            self.infos.clear()
        if self.source_chunks:
            dstore['source_chunks'] = sc = numpy.array(
                self.source_chunks, source_chunk_dt)
            attrs = dstore['source_chunks'].attrs
            attrs['nbytes'] = sc.nbytes
            attrs['sent'] = sc['sent'].sum()
            attrs['task_name'] = self.tm.name
            del self.source_chunks


@parallel.litetask
def count_eff_ruptures(sources, sitecol, siteidx, rlzs_assoc, monitor):
    """
    Count the number of ruptures contained in the given sources and return
    a dictionary trt_model_id -> num_ruptures. All sources belong to the
    same tectonic region type.
    """
    acc = AccumDict()
    acc.eff_ruptures = {sources[0].trt_model_id:
                        sum(src.num_ruptures for src in sources)}
    return acc
