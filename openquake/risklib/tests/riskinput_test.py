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

import mock
import unittest
import numpy
from openquake.baselib.general import writetmp
from openquake.commonlib import readinput, writers, riskmodels
from openquake.risklib import riskinput
from openquake.calculators import event_based
from openquake.calculators.tests import get_datastore
from openquake.qa_tests_data.event_based_risk import case_2


class MockAssoc(object):
    csm_info = mock.Mock()
    csm_info.get_trt_id.return_value = 0

    def __iter__(self):
        return iter([])

    def combine(self, dicts):
        return []

    def __getitem__(self, key):
        return []

rlzs_assoc = MockAssoc()


class RiskInputTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oqparam = readinput.get_oqparam('job_loss.ini', pkg=case_2)
        cls.oqparam.insured_losses = True
        cls.sitecol, cls.assets_by_site = readinput.get_sitecol_assets(
            cls.oqparam, readinput.get_exposure(cls.oqparam))
        rmdict = riskmodels.get_risk_models(cls.oqparam)
        cls.riskmodel = readinput.get_risk_model(cls.oqparam, rmdict)

    def test_assetcol(self):
        expected = writetmp('''\
asset_ref:|S100,lon,lat,site_id:uint32,taxonomy:uint32:,number,area,occupants:float64:,structural:float64:,deductible~structural:float64:,insurance_limit~structural:float64:
a0,8.12985001E+01,2.91098003E+01,0,1,3.00000000E+00,1.00000000E+01,1.00000000E+01,1.00000000E+02,2.50000000E+01,1.00000000E+02
a1,8.30822983E+01,2.79006004E+01,1,0,5.00000000E+02,1.00000000E+01,2.00000000E+01,4.00000000E-01,1.00000000E-01,2.00000000E-01
''')
        assetcol = riskinput.build_asset_collection(self.assets_by_site)
        numpy.testing.assert_equal(
            assetcol, writers.read_composite_array(expected))

    def test_get_hazard(self):
        self.assertEqual(
            list(self.riskmodel.get_imt_taxonomies()),
            [('PGA', set(['RM'])), ('SA(0.2)', set(['RC'])),
             ('SA(0.5)', set(['W']))])
        self.assertEqual(len(self.sitecol), 2)
        hazard_by_site = [{}] * 2

        ri_PGA = self.riskmodel.build_input(
            'PGA', hazard_by_site, self.assets_by_site, {})
        haz = ri_PGA.get_hazard(rlzs_assoc)
        self.assertEqual(len(haz), 2)

        ri_SA_02 = self.riskmodel.build_input(
            'SA(0.2)', hazard_by_site, self.assets_by_site, {})
        haz = ri_SA_02.get_hazard(rlzs_assoc)
        self.assertEqual(len(haz), 2)

        ri_SA_05 = self.riskmodel.build_input(
            'SA(0.5)', hazard_by_site, self.assets_by_site, {})
        haz = ri_SA_05.get_hazard(rlzs_assoc)
        self.assertEqual(len(haz), 2)
