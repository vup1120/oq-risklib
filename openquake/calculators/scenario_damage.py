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

import itertools
import numpy

from openquake.commonlib import parallel, riskmodels, logictree
from openquake.risklib import scientific
from openquake.calculators import base

F32 = numpy.float32
F64 = numpy.float64


def dist_by_asset(data, multi_stat_dt):
    """
    :param data: array of shape (N, L, R, 2, ...)
    :param multi_stat_dt: numpy dtype for statistical outputs
    :returns: array of shape (N, R) with records of type multi_stat_dt
    """
    N, L, R = data.shape[:3]
    out = numpy.zeros((N, R), multi_stat_dt)
    for l, lt in enumerate(multi_stat_dt.names):
        out_lt = out[lt]
        for n, r in itertools.product(range(N), range(R)):
            out_lt[n, r] = data[n, l, r]
    return out


def dist_by_taxon(data, multi_stat_dt):
    """
    :param data: array of shape (T, L, R, ...)
    :param multi_stat_dt: numpy dtype for statistical outputs
    :returns: array of shape (T, R) with records of type multi_stat_dt
    """
    T, L, R = data.shape[:3]
    out = numpy.zeros((T, R), multi_stat_dt)
    for l, lt in enumerate(multi_stat_dt.names):
        out_lt = out[lt]
        for t, r in itertools.product(range(T), range(R)):
            out_lt[t, r] = scientific.mean_std(data[t, l, r])
    return out


def dist_total(data, multi_stat_dt):
    """
    :param data: array of shape (T, L, R, ...)
    :param multi_stat_dt: numpy dtype for statistical outputs
    :returns: array of shape (R,) with records of type multi_stat_dt
    """
    T, L, R = data.shape[:3]
    total = data.sum(axis=0)
    out = numpy.zeros(R, multi_stat_dt)
    for l, lt in enumerate(multi_stat_dt.names):
        out_lt = out[lt]
        for r in range(R):
            out_lt[r] = scientific.mean_std(total[l, r])
    return out


@parallel.litetask
def scenario_damage(riskinputs, riskmodel, rlzs_assoc, monitor):
    """
    Core function for a damage computation.

    :param riskinputs:
        a list of :class:`openquake.risklib.riskinput.RiskInput` objects
    :param riskmodel:
        a :class:`openquake.risklib.riskinput.CompositeRiskModel` instance
    :param rlzs_assoc:
        a class:`openquake.commonlib.source.RlzsAssoc` instance
    :param monitor:
        :class:`openquake.baselib.performance.Monitor` instance
    :returns:
        a dictionary {'d_asset': [(l, r, a, mean-stddev), ...],
                      'd_taxonomy': damage array of shape T, L, R, E, D,
                      'c_asset': [(l, r, a, mean-stddev), ...],
                      'c_taxonomy': damage array of shape T, L, R, E}

    `d_asset` and `d_taxonomy` are related to the damage distributions
    whereas `c_asset` and `c_taxonomy` are the consequence distributions.
    If there is no consequence model `c_asset` is an empty list and
    `c_taxonomy` is a zero-value array.
    """
    c_models = monitor.consequence_models
    L = len(riskmodel.loss_types)
    R = len(rlzs_assoc.realizations)
    D = len(riskmodel.damage_states)
    E = monitor.oqparam.number_of_ground_motion_fields
    T = len(monitor.taxonomies)
    taxo2idx = {taxo: i for i, taxo in enumerate(monitor.taxonomies)}
    result = dict(d_asset=[], d_taxon=numpy.zeros((T, L, R, E, D), F64),
                  c_asset=[], c_taxon=numpy.zeros((T, L, R, E), F64))
    for out_by_lr in riskmodel.gen_outputs(
            riskinputs, rlzs_assoc, monitor):
        for (l, r), out in sorted(out_by_lr.items()):
            c_model = c_models.get(out.loss_type)
            for asset, fraction in zip(out.assets, out.damages):
                t = taxo2idx[asset.taxonomy]
                damages = fraction * asset.number
                if c_model:  # compute consequences
                    means = [par[0] for par in c_model[asset.taxonomy].params]
                    # NB: we add a 0 in front for nodamage state
                    c_ratio = numpy.dot(fraction, [0] + means)
                    consequences = c_ratio * asset.value(out.loss_type)
                    result['c_asset'].append(
                        (l, r, asset.idx, scientific.mean_std(consequences)))
                    result['c_taxon'][t, l, r, :] += consequences
                    # TODO: consequences for the occupants
                result['d_asset'].append(
                    (l, r, asset.idx, scientific.mean_std(damages)))
                result['d_taxon'][t, l, r, :] += damages
    return result


@base.calculators.add('scenario_damage')
class ScenarioDamageCalculator(base.RiskCalculator):
    """
    Scenario damage calculator
    """
    pre_calculator = 'scenario'
    core_task = scenario_damage
    is_stochastic = True

    def pre_execute(self):
        if 'gmfs' in self.oqparam.inputs:
            self.pre_calculator = None
        base.RiskCalculator.pre_execute(self)
        self.monitor.consequence_models = riskmodels.get_risk_models(
            self.oqparam, 'consequence')
        if 'gmfs' in self.oqparam.inputs:
            self.rlzs_assoc = logictree.trivial_rlzs_assoc()
        self.etags, gmfs = base.get_gmfs(self.datastore)
        self.riskinputs = self.build_riskinputs(gmfs)
        self.monitor.taxonomies = sorted(self.taxonomies)

    def post_execute(self, result):
        """
        Compute stats for the aggregated distributions and save
        the results on the datastore.
        """
        dstates = self.riskmodel.damage_states
        ltypes = self.riskmodel.loss_types
        L = len(ltypes)
        R = len(self.rlzs_assoc.realizations)
        D = len(dstates)
        N = len(self.assetcol)

        # damage distributions
        dt_list = []
        for ltype in ltypes:
            dt_list.append((ltype, numpy.dtype([('mean', (F32, D)),
                                                ('stddev', (F32, D))])))
        multi_stat_dt = numpy.dtype(dt_list)
        d_asset = numpy.zeros((N, L, R, 2, D), F32)
        for (l, r, a, stat) in result['d_asset']:
            d_asset[a, l, r] = stat
        self.datastore['dmg_by_asset'] = dist_by_asset(
            d_asset, multi_stat_dt)
        self.datastore['dmg_by_taxon'] = dist_by_taxon(
            result['d_taxon'], multi_stat_dt)
        self.datastore['dmg_total'] = dist_total(
            result['d_taxon'], multi_stat_dt)

        # consequence distributions
        if result['c_asset']:
            c_asset = numpy.zeros((N, L, R, 2), F32)
            for (l, r, a, stat) in result['c_asset']:
                c_asset[a, l, r] = stat
            multi_stat_dt = numpy.dtype(
                [(lt, [('mean', F32), ('stddev', F32)]) for lt in ltypes])
            self.datastore['csq_by_asset'] = dist_by_asset(
                c_asset, multi_stat_dt)
            self.datastore['csq_by_taxon'] = dist_by_taxon(
                result['c_taxon'], multi_stat_dt)
            self.datastore['csq_total'] = dist_total(
                result['c_taxon'], multi_stat_dt)
