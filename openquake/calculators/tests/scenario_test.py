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

from __future__ import division
import numpy
import unittest
from numpy.testing import assert_almost_equal as aae
from nose.plugins.attrib import attr

from openquake.qa_tests_data.scenario import (
    case_1, case_2, case_3, case_4, case_5, case_6, case_7, case_8, case_9)

from openquake.commonlib import writers
from openquake.calculators.event_based import get_gmvs_by_sid
from openquake.calculators.tests import CalculatorTestCase


def count_close(gmf_value, gmvs_site_one, gmvs_site_two, delta=0.1):
    """
    Count the number of pairs of gmf values
    within the specified range.
    See https://bugs.launchpad.net/openquake/+bug/1097646
    attached Scenario Hazard script.
    """
    lower_bound = gmf_value - delta / 2.
    upper_bound = gmf_value + delta / 2.
    return sum((lower_bound <= v1 <= upper_bound) and
               (lower_bound <= v2 <= upper_bound)
               for v1, v2 in zip(gmvs_site_one, gmvs_site_two))


class ScenarioHazardTestCase(CalculatorTestCase):

    def frequencies(self, case, fst_value, snd_value):
        [gmfa] = self.execute(case.__file__, 'job.ini').values()
        [imt] = self.calc.oqparam.imtls
        gmvs_by_sid = get_gmvs_by_sid(gmfa)
        gmvs0 = gmvs_by_sid[0][imt]
        gmvs1 = gmvs_by_sid[1][imt]
        realizations = float(self.calc.oqparam.number_of_ground_motion_fields)
        gmvs_within_range_fst = count_close(fst_value, gmvs0, gmvs1)
        gmvs_within_range_snd = count_close(snd_value, gmvs0, gmvs1)
        return (gmvs_within_range_fst / realizations,
                gmvs_within_range_snd / realizations)

    def medians(self, case):
        [gmfa] = self.execute(case.__file__, 'job.ini').values()
        median = self.calc.oqparam.imtls.copy()
        gmvs_by_sid = get_gmvs_by_sid(gmfa)
        for imt in median:
            gmf = [gmvs_by_sid[sid][imt] for sid in sorted(gmvs_by_sid)]
            median[imt] = numpy.median(gmf, axis=1)  # shape N
        return median

    @attr('qa', 'hazard', 'scenario')
    def test_case_1(self):
        # ROUNDING ERROR WARNING (MS): numbers such as 2.5 and 2.4999999999
        # are extremely close (up to 4E-11) however they must be rounded to
        # a single digit to compare equal in their string representation; for
        # this reason the precision here has to be reduced a lot, even it the
        # numbers are very close. It comes down to the known fact that
        # comparing the XMLs is not a good idea; suboptimal choises
        # sometimes have to be made, since we want this test to
        # to run both on Ubuntu 12.04 and Ubuntu 14.04.
        # Incidentally, when the approach of comparing the XML was taken,
        # the idea of supporting at the same time different versions of the
        # libraries was out of question, so it made a lot of sense to check
        # the XMLs, since the numbers had to be exactly identical.
        with writers.floatformat('%5.1E'):
            out = self.run_calc(case_1.__file__, 'job.ini', exports='xml')
        raise unittest.SkipTest  # because of the rounding errors
        self.assertEqualFiles('expected.xml', out['gmf_data', 'xml'][0])

    @attr('qa', 'hazard', 'scenario')
    def test_case_1bis(self):
        # 2 out of 3 sites were filtered out
        out = self.run_calc(case_1.__file__, 'job.ini',
                            maximum_distance='0.1', exports='txt')
        self.assertEqualFiles(
            'BooreAtkinson2008_gmf.txt', out['gmf_data', 'txt'][0])

    @attr('qa', 'hazard', 'scenario')
    def test_case_2(self):
        medians = self.medians(case_2)['PGA']
        aae(medians, [0.37412136, 0.19021782, 0.1365383], decimal=2)

    @attr('qa', 'hazard', 'scenario')
    def test_case_3(self):
        medians_dict = self.medians(case_3)
        medians_pga = medians_dict['PGA']
        medians_sa = medians_dict['SA(0.1)']
        aae(medians_pga, [0.48155582, 0.21123045, 0.14484586], decimal=2)
        aae(medians_sa, [0.93913177, 0.40880148, 0.2692668], decimal=2)

    @attr('qa', 'hazard', 'scenario')
    def test_case_4(self):
        medians = self.medians(case_4)['PGA']
        aae(medians, [0.41615372, 0.22797466, 0.1936226], decimal=2)

    @attr('qa', 'hazard', 'scenario')
    def test_case_5(self):
        f1, f2 = self.frequencies(case_5, 0.5, 1.0)
        self.assertAlmostEqual(f1, 0.03, places=2)
        self.assertAlmostEqual(f2, 0.003, places=3)

    @attr('qa', 'hazard', 'scenario')
    def test_case_6(self):
        f1, f2 = self.frequencies(case_6, 0.5, 1.0)
        self.assertAlmostEqual(f1, 0.05, places=2)
        self.assertAlmostEqual(f2, 0.006, places=3)

    @attr('qa', 'hazard', 'scenario')
    def test_case_7(self):
        f1, f2 = self.frequencies(case_7, 0.5, 1.0)
        self.assertAlmostEqual(f1, 0.02, places=2)
        self.assertAlmostEqual(f2, 0.002, places=3)

    @attr('qa', 'hazard', 'scenario')
    def test_case_8(self):
        # test for a GMPE requiring hypocentral depth, since it was
        # broken: https://bugs.launchpad.net/oq-engine/+bug/1334524
        # I am not really checking anything, only that it runs
        f1, f2 = self.frequencies(case_8, 0.5, 1.0)
        self.assertAlmostEqual(f1, 0)
        self.assertAlmostEqual(f2, 0)

    @attr('qa', 'hazard', 'scenario')
    def test_case_9(self):
        with writers.floatformat('%10.6E'):
            out = self.run_calc(case_9.__file__, 'job.ini', exports='xml')
        f1, f2 = out['gmf_data', 'xml']
        self.assertEqualFiles('LinLee2008SSlab_gmf.xml', f1)
        self.assertEqualFiles('YoungsEtAl1997SSlab_gmf.xml', f2)

        out = self.run_calc(case_9.__file__, 'job.ini', exports='txt,csv')
        f1, f2 = out['gmf_data', 'txt']
        self.assertEqualFiles('LinLee2008SSlab_gmf.txt', f1)
        self.assertEqualFiles('YoungsEtAl1997SSlab_gmf.txt', f2)

        f1, f2 = out['gmf_data', 'csv']
        self.assertEqualFiles('gmf-LinLee2008SSlab-PGA.csv', f1)
        self.assertEqualFiles('gmf-YoungsEtAl1997SSlab-PGA.csv', f2)
