#!/usr/bin/env python
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
import importlib

from openquake.commonlib import commands, sap, __version__


def oq_lite():
    modnames = ['openquake.commonlib.commands.%s' % mod[:-3]
                for mod in os.listdir(commands.__path__[0])
                if mod.endswith('.py') and not mod.startswith('_')]
    parsers = [importlib.import_module(modname).parser for modname in modnames]
    parser = sap.compose(parsers, prog='oq-lite', version=__version__)
    parser.callfunc()

if __name__ == '__main__':
    oq_lite()
