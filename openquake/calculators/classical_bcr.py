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

import numpy

from openquake.commonlib import parallel
from openquake.calculators import base, classical_risk

F32 = numpy.float32

bcr_dt = numpy.dtype([('annual_loss_orig', F32), ('annual_loss_retro', F32),
                      ('bcr', F32)])


@parallel.litetask
def classical_bcr(riskinputs, riskmodel, rlzs_assoc, bcr_dt, monitor):
    """
    Compute and return the average losses for each asset.

    :param riskinputs:
        a list of :class:`openquake.risklib.riskinput.RiskInput` objects
    :param riskmodel:
        a :class:`openquake.risklib.riskinput.CompositeRiskModel` instance
    :param rlzs_assoc:
        associations (trt_id, gsim) -> realizations
    :param bcr_dt:
        data type with fields annual_loss_orig, annual_loss_retro, bcr
    :param monitor:
        :class:`openquake.baselib.performance.Monitor` instance
    """
    result = {}  # (N, R) -> data
    for out_by_lr in riskmodel.gen_outputs(riskinputs, rlzs_assoc, monitor):
        for (l, r), out in sorted(out_by_lr.items()):
            for asset, (eal_orig, eal_retro, bcr) in zip(out.assets, out.data):
                aval = asset.value(out.loss_type)
                result[asset.ordinal, out.loss_type, out.hid] = numpy.array([
                    (eal_orig * aval, eal_retro * aval, bcr)], bcr_dt)
    return result


@base.calculators.add('classical_bcr')
class ClassicalBCRCalculator(classical_risk.ClassicalRiskCalculator):
    """
    Classical BCR Risk calculator
    """
    core_task = classical_bcr

    def pre_execute(self):
        super(ClassicalBCRCalculator, self).pre_execute()
        self.extra_args = (bcr_dt,)

    def post_execute(self, result):
        bcr_data = numpy.zeros(
            (self.N, self.R), self.riskmodel.loss_type_dt(bcr_dt))
        for (aid, lt, r), data in result.items():
            bcr_data[lt][aid, r] = data
        self.datastore['bcr-rlzs'] = bcr_data
