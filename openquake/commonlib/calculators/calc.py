#  -*- coding: utf-8 -*-
#  vim: tabstop=4 shiftwidth=4 softtabstop=4

#  Copyright (c) 2014, GEM Foundation

#  OpenQuake is free software: you can redistribute it and/or modify it
#  under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  OpenQuake is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with OpenQuake.  If not, see <http://www.gnu.org/licenses/>.

import collections
import itertools
import operator
import random

import numpy

from openquake.hazardlib.calc import gmf, filters
from openquake.hazardlib.site import SiteCollection
from openquake.baselib.general import AccumDict
from openquake.commonlib.readinput import \
    get_gsim, get_rupture, get_correl_model, get_imts


MAX_INT = 2 ** 31 - 1  # this is used in the random number generator
# in this way even on 32 bit machines Python will not have to convert
# the generated seed into a long integer

############### utilities for the classical calculator ################

SourceRuptureSites = collections.namedtuple(
    'SourceRuptureSites',
    'source rupture sites')


def gen_ruptures(sources, site_coll, maximum_distance, monitor):
    """
    Yield (source, rupture, affected_sites) for each rupture
    generated by the given sources.

    :param sources: a sequence of sources
    :param site_coll: a SiteCollection instance
    :param maximum_distance: the maximum distance
    :param monitor: a Monitor object
    """
    filtsources_mon = monitor.copy('filtering sources')
    genruptures_mon = monitor.copy('generating ruptures')
    filtruptures_mon = monitor.copy('filtering ruptures')
    for src in sources:
        with filtsources_mon:
            s_sites = src.filter_sites_by_distance_to_source(
                maximum_distance, site_coll)
            if s_sites is None:
                continue

        with genruptures_mon:
            ruptures = list(src.iter_ruptures())
        if not ruptures:
            continue

        for rupture in ruptures:
            with filtruptures_mon:
                r_sites = filters.filter_sites_by_distance_to_rupture(
                    rupture, maximum_distance, s_sites)
                if r_sites is None:
                    continue
            yield SourceRuptureSites(src, rupture, r_sites)
    filtsources_mon.flush()
    genruptures_mon.flush()
    filtruptures_mon.flush()


def gen_ruptures_for_site(site, sources, maximum_distance, monitor):
    """
    Yield source, <ruptures close to site>

    :param site: a Site object
    :param sources: a sequence of sources
    :param monitor: a Monitor object
    """
    source_rupture_sites = gen_ruptures(
        sources, SiteCollection([site]), maximum_distance, monitor)
    for src, rows in itertools.groupby(
            source_rupture_sites, key=operator.attrgetter('source')):
        yield src, [row.rupture for row in rows]


############### utilities for the scenario calculators ################


def calc_gmfs_fast(oqparam, sitecol):
    """
    Build all the ground motion fields for the whole site collection in
    a single step.
    """
    max_dist = oqparam.maximum_distance
    correl_model = get_correl_model(oqparam)
    seed = getattr(oqparam, 'random_seed', 42)
    imts = get_imts(oqparam)
    gsim = get_gsim(oqparam)
    trunc_level = getattr(oqparam, 'truncation_level', None)
    n_gmfs = getattr(oqparam, 'number_of_ground_motion_fields', 1)
    rupture = get_rupture(oqparam)
    res = gmf.ground_motion_fields(
        rupture, sitecol, imts, gsim,
        trunc_level, n_gmfs, correl_model,
        filters.rupture_site_distance_filter(max_dist), seed)
    return {str(imt): matrix for imt, matrix in res.iteritems()}


def calc_gmfs(oqparam, sitecol):
    """
    Build all the ground motion fields for the whole site collection
    """
    correl_model = get_correl_model(oqparam)
    rnd = random.Random()
    rnd.seed(getattr(oqparam, 'random_seed', 42))
    imts = get_imts(oqparam)
    gsim = get_gsim(oqparam)
    trunc_level = getattr(oqparam, 'truncation_level', None)
    n_gmfs = getattr(oqparam, 'number_of_ground_motion_fields', 1)
    rupture = get_rupture(oqparam)
    computer = gmf.GmfComputer(rupture, sitecol, imts, gsim, trunc_level,
                               correl_model)
    seeds = [rnd.randint(0, MAX_INT) for _ in xrange(n_gmfs)]
    res = AccumDict()  # imt -> gmf
    for seed in seeds:
        for imt, gmfield in computer.compute(seed):
            res += {imt: [gmfield]}
    # res[imt] is a matrix R x N
    return {imt: numpy.array(matrix).T for imt, matrix in res.iteritems()}

########################### hazard maps #######################################

# cutoff value for the poe
EPSILON = 1E-30


def compute_hazard_maps(curves, imls, poes):
    """
    Given a set of hazard curve poes, interpolate a hazard map at the specified
    ``poe``.

    :param curves:
        2D array of floats. Each row represents a curve, where the values
        in the row are the PoEs (Probabilities of Exceedance) corresponding to
        ``imls``. Each curve corresponds to a geographical location.
    :param imls:
        Intensity Measure Levels associated with these hazard ``curves``. Type
        should be an array-like of floats.
    :param float poes:
        Value(s) on which to interpolate a hazard map from the input
        ``curves``. Can be an array-like or scalar value (for a single PoE).

    :returns:
        A 2D numpy array of hazard map data. Each element/row in the resulting
        array represents the interpolated map for each ``poes`` value
        specified. If ``poes`` is just a single scalar value, the result array
        will have a length of 1.

        The results are structured this way so that it is easy to iterate over
        the hazard map results in a consistent way, no matter how many
        ``poes`` values are specified.
    """
    poes = numpy.array(poes)

    if len(poes.shape) == 0:
        # ``poes`` was passed in as a scalar;
        # convert it to 1D array of 1 element
        poes = poes.reshape(1)

    result = []
    imls = numpy.log(numpy.array(imls[::-1]))

    for curve in curves:
        # the hazard curve, having replaced the too small poes with EPSILON
        curve_cutoff = [max(poe, EPSILON) for poe in curve[::-1]]
        hmap_val = []
        for poe in poes:
            # special case when the interpolation poe is bigger than the
            # maximum, i.e the iml must be smaller than the minumum
            if poe > curve_cutoff[-1]:  # the greatest poes in the curve
                # extrapolate the iml to zero as per
                # https://bugs.launchpad.net/oq-engine/+bug/1292093
                # a consequence is that if all poes are zero any poe > 0
                # is big and the hmap goes automatically to zero
                hmap_val.append(0)
            else:
                # exp-log interpolation, to reduce numerical errors
                # see https://bugs.launchpad.net/oq-engine/+bug/1252770
                val = numpy.exp(
                    numpy.interp(
                        numpy.log(poe), numpy.log(curve_cutoff), imls))
                hmap_val.append(val)

        result.append(hmap_val)
    return numpy.array(result).transpose()


def compute_hazard_maps_by_imt(curves_by_imt, imtls, poes):
    """
    Compute the hazard maps for all the IMTs.
    """
    return AccumDict({imt: compute_hazard_maps(curves_by_imt[imt], imls, poes)
                      for imt, imls in imtls.iteritems()})


def mean_curve(curves, weights=None):
    """
    Compute the mean or weighted average of a set of curves.

    :param curves:
        2D array-like collection of hazard curve PoE values. Each element
        should be a sequence of PoE `float` values. Example::

            [[0.5, 0.4, 0.3], [0.6, 0.59, 0.1]]

        .. note::
            This data represents the curves for all realizations for a given
            site and IMT.

    :param weights:
        List or numpy array of weights, 1 weight value for each of the input
        ``curves``. This is only used for weighted averages.

    :returns:
        A curve representing the mean/average (or weighted average, in case
        ``weights`` are specified) of all the input ``curves``.
    """
    if weights is not None:
        # If all of the weights are None, don't compute a weighted average
        none_weights = [x is None for x in weights]
        if all(none_weights):
            weights = None
        elif any(none_weights):
            # some weights are defined, but some are none;
            # this is invalid input
            raise ValueError('`None` value found in weights: %s' % weights)

    return numpy.average(curves, weights=weights, axis=0)


def weighted_quantile_curve(curves, weights, quantile):
    """
    Compute the weighted quantile aggregate of a set of curves. This method is
    used in the case where hazard curves are computed using the logic tree
    end-branch enumeration approach. In this case, the weights are explicit.

    :param curves:
        2D array-like of curve PoEs. Each row represents the PoEs for a single
        curve
    :param weights:
        Array-like of weights, 1 for each input curve.
    :param quantile:
        Quantile value to calculate. Should in the range [0.0, 1.0].

    :returns:
        A numpy array representing the quantile aggregate of the input
        ``curves`` and ``quantile``, weighting each curve with the specified
        ``weights``.
    """
    # Each curve needs to be associated with a weight:
    assert len(weights) == len(curves)
    # NOTE(LB): Weights might be passed as a list of `decimal.Decimal`
    # types, and numpy.interp can't handle this (it throws TypeErrors).
    # So we explicitly cast to floats here before doing interpolation.
    weights = numpy.array(weights, dtype=numpy.float64)

    result_curve = []

    np_curves = numpy.array(curves)
    np_weights = numpy.array(weights)

    for poes in np_curves.transpose():
        sorted_poe_idxs = numpy.argsort(poes)
        sorted_weights = np_weights[sorted_poe_idxs]
        sorted_poes = poes[sorted_poe_idxs]

        # cumulative sum of weights:
        cum_weights = numpy.cumsum(sorted_weights)

        result_curve.append(numpy.interp(quantile, cum_weights, sorted_poes))

    return numpy.array(result_curve)


def quantile_curve(curves, quantile):
    """
    Compute the quantile aggregate of a set of curves. This method is used in
    the case where hazard curves are computed using the Monte-Carlo logic tree
    sampling approach. In this case, the weights are implicit.

    :param curves:
        2D array-like collection of hazard curve PoE values. Each element
        should be a sequence of PoE `float` values. Example::

            [[0.5, 0.4, 0.3], [0.6, 0.59, 0.1]]
    :param float quantile:
        The quantile value. We expected a value in the range [0.0, 1.0].

    :returns:
        A numpy array representing the quantile aggregate of the input
        ``curves`` and ``quantile``.
    """
    # this implementation is an alternative to:
    # return numpy.array(mstats.mquantiles(curves, prob=quantile, axis=0))[0]

    # more or less copied from the scipy mquantiles function, just special
    # cased for what we need (and a lot faster)

    arr = numpy.array(curves)

    p = numpy.array(quantile)
    m = 0.4 + p * 0.2

    n = len(arr)
    aleph = n * p + m
    k = numpy.floor(aleph.clip(1, n - 1)).astype(int)
    gamma = (aleph - k).clip(0, 1)

    data = numpy.sort(arr, axis=0).transpose()
    return (1.0 - gamma) * data[:, k - 1] + gamma * data[:, k]
