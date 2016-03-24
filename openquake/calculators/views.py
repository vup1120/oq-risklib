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
import io
import ast
import os.path
import numbers
import operator
import decimal
import functools
import itertools
import numpy

from openquake.baselib.general import humansize, groupby
from openquake.baselib.performance import perf_dt
from openquake.hazardlib.gsim.base import ContextMaker
from openquake.commonlib import util, source
from openquake.commonlib.oqvalidation import OqParam
from openquake.commonlib.datastore import view
from openquake.commonlib.writers import (
    build_header, scientificformat, write_csv)

# ########################## utility functions ############################## #

FLOAT = (float, numpy.float32, numpy.float64, decimal.Decimal)
INT = (int, numpy.uint32, numpy.int64)


def form(value):
    """
    Format numbers in a nice way.

    >>> form(0)
    '0'
    >>> form(0.0)
    '0.0'
    >>> form(0.0001)
    '1.000E-04'
    >>> form(1003.4)
    '1,003'
    >>> form(103.4)
    '103'
    >>> form(9.3)
    '9.300'
    >>> form(-1.2)
    '-1.2'
    """
    if isinstance(value, FLOAT + INT):
        if value <= 0:
            return str(value)
        elif value < .001:
            return '%.3E' % value
        elif value < 10 and isinstance(value, FLOAT):
            return '%.3f' % value
        elif value > 1000:
            return '{:,d}'.format(int(round(value)))
        else:  # in the range 10-1000
            return str(int(value))
    elif hasattr(value, '__iter__'):
        return ' '.join(map(form, value))
    return str(value)


def rst_table(data, header=None, fmt=None):
    """
    Build a .rst table from a matrix.
    
    >>> tbl = [['a', 1], ['b', 2]]
    >>> print rst_table(tbl, header=['Name', 'Value'])
    ==== =====
    Name Value
    ==== =====
    a    1    
    b    2    
    ==== =====
    """
    try:
        # see if data is a composite numpy array
        data.dtype.fields
    except AttributeError:
        # not a composite array
        header = header or ()
    else:
        if not header:
            header = [col.split(':')[0] for col in build_header(data.dtype)]
    if header:
        col_sizes = [len(col) for col in header]
    else:
        col_sizes = [len(str(col)) for col in data[0]]
    body = []
    fmt = functools.partial(scientificformat, fmt=fmt) if fmt else form
    for row in data:
        tup = tuple(fmt(c) for c in row)
        for (i, col) in enumerate(tup):
            col_sizes[i] = max(col_sizes[i], len(col))
        body.append(tup)

    sepline = ' '.join(('=' * size for size in col_sizes))
    templ = ' '.join(('%-{}s'.format(size) for size in col_sizes))
    if header:
        lines = [sepline, templ % tuple(header), sepline]
    else:
        lines = [sepline]
    for row in body:
        lines.append(templ % row)
    lines.append(sepline)
    return '\n'.join(lines)


def classify_gsim_lt(gsim_lt):
    """
    :returns: "trivial", "simple" or "complex"
    """
    num_branches = list(gsim_lt.get_num_branches().values())
    num_gsims = '(%s)' % ','.join(map(str, num_branches))
    multi_gsim_trts = sum(1 for num_gsim in num_branches if num_gsim > 1)
    if multi_gsim_trts == 0:
        return "trivial" + num_gsims
    elif multi_gsim_trts == 1:
        return "simple" + num_gsims
    else:
        return "complex" + num_gsims


@view.add('contents')
def view_contents(token, dstore):
    """
    Returns the size of the contents of the datastore and its total size
    """
    oq = OqParam.from_(dstore.attrs)
    data = sorted((dstore.getsize(key), key) for key in dstore)
    rows = [(key, humansize(nbytes)) for nbytes, key in data]
    total = '\n%s : %s' % (
        dstore.hdf5path, humansize(os.path.getsize(dstore.hdf5path)))
    return rst_table(rows, header=(oq.description, '')) + total


@view.add('csm_info')
def view_csm_info(token, dstore):
    rlzs_assoc = dstore['rlzs_assoc']
    csm_info = rlzs_assoc.csm_info
    header = ['smlt_path', 'weight', 'source_model_file',
              'gsim_logic_tree', 'num_realizations']
    rows = []
    for sm in csm_info.source_models:
        num_rlzs = len(rlzs_assoc.rlzs_by_smodel[sm.ordinal])
        num_paths = sm.num_gsim_paths(csm_info.num_samples)
        link = "`%s <%s>`_" % (sm.name, sm.name)
        row = ('_'.join(sm.path), sm.weight, link,
               classify_gsim_lt(sm.gsim_lt), '%d/%d' % (num_rlzs, num_paths))
        rows.append(row)
    return rst_table(rows, header)


@view.add('rupture_collections')
def view_rupture_collections(token, dstore):
    rlzs_assoc = dstore['rlzs_assoc']
    num_ruptures = dstore['num_ruptures']
    csm_info = rlzs_assoc.csm_info
    rows = []
    col_id = 0
    for sm in csm_info.source_models:
        for tm in sm.trt_models:
            for idx in range(sm.samples):
                nr = num_ruptures[col_id]
                if nr:
                    rows.append((col_id, '_'.join(sm.path), tm.trt, nr))
                col_id += 1
    return rst_table(rows, ['col', 'smlt_path', 'TRT', 'num_ruptures'])


@view.add('ruptures_per_trt')
def view_ruptures_per_trt(token, dstore):
    tbl = []
    header = ('source_model trt_id trt num_sources '
              'eff_ruptures weight'.split())
    num_trts = 0
    tot_sources = 0
    eff_ruptures = 0
    tot_weight = 0
    source_info = dstore['source_info'].value
    csm_info = dstore['rlzs_assoc'].csm_info
    w = groupby(source_info, operator.itemgetter('trt_model_id'),
                lambda rows: sum(r['weight'] for r in rows))
    n = groupby(source_info, operator.itemgetter('trt_model_id'),
                lambda rows: sum(1 for r in rows))
    for i, sm in enumerate(csm_info.source_models):
        # NB: the number of effective ruptures per tectonic region model
        # is stored in the array eff_ruptures as a literal string describing
        # an array {trt_model_id: num_ruptures}; see the method
        # CompositionInfo.get_rlzs_assoc
        erdict = ast.literal_eval(csm_info.eff_ruptures[i])
        for trt_model in sm.trt_models:
            trt = source.capitalize(trt_model.trt)
            er = erdict.get(trt, 0)  # effective ruptures
            if er:
                num_trts += 1
                num_sources = n.get(trt_model.id, 0)
                tot_sources += num_sources
                eff_ruptures += er
                weight = w.get(trt_model.id, 0)
                tot_weight += weight
                tbl.append((sm.name, trt_model.id, trt,
                            num_sources, er, weight))
    rows = [('#TRT models', num_trts),
            ('#sources', tot_sources),
            ('#eff_ruptures', eff_ruptures),
            ('filtered_weight', tot_weight)]
    if len(tbl) > 1:
        summary = '\n\n' + rst_table(rows)
    else:
        summary = ''
    return rst_table(tbl, header=header) + summary


@view.add('short_source_info')
def view_short_source_info(token, dstore, maxrows=20):
    return rst_table(dstore['source_info'][:maxrows])


@view.add('params')
def view_params(token, dstore):
    oq = OqParam.from_(dstore.attrs)
    params = ['calculation_mode', 'number_of_logic_tree_samples',
              'maximum_distance', 'investigation_time',
              'ses_per_logic_tree_path', 'truncation_level',
              'rupture_mesh_spacing', 'complex_fault_mesh_spacing',
              'width_of_mfd_bin', 'area_source_discretization',
              'random_seed', 'master_seed', 'concurrent_tasks']
    if 'risk' in oq.calculation_mode:
        params.append('avg_losses')
    if 'classical' in oq.calculation_mode:
        params.append('sites_per_tile')
    return rst_table([(param, repr(getattr(oq, param, None)))
                      for param in params])


def build_links(items):
    out = []
    for key, fname in items:
        bname = os.path.basename(fname)
        link = "`%s <%s>`_" % (bname, bname)
        out.append((key, link))
    return sorted(out)


@view.add('inputs')
def view_inputs(token, dstore):
    inputs = OqParam.from_(dstore.attrs).inputs.copy()
    try:
        source_models = [('source', fname) for fname in inputs['source']]
        del inputs['source']
    except KeyError:  # there is no 'source' in scenario calculations
        source_models = []
    return rst_table(
        build_links(list(inputs.items()) + source_models),
        header=['Name', 'File'])


@view.add('source_data_transfer')
def source_data_transfer(token, dstore):
    """
    Determine the amount of data transferred from the controller node
    to the workers and back in a classical calculation.
    """
    sc = dstore['source_chunks']
    tbl = [
        ('Number of tasks to generate', len(sc)),
        ('Sent data', humansize(sc.attrs['sent']))]
    # NB: when called from `oq-lite info --report` the task name is
    # count_eff_ruptures; then tot_received and max_received are bogus
    if sc.attrs['task_name'] != 'count_eff_ruptures':
        tbl.extend([
            ('Total received data', humansize(sc.attrs['tot_received'])),
            ('Maximum received per task', humansize(sc.attrs['max_received'])),
        ])
    return rst_table(tbl)


@view.add('avglosses_data_transfer')
def avglosses_data_transfer(token, dstore):
    """
    Determine the amount of average losses transferred from the workers to the
    controller node in a risk calculation.
    """
    oq = OqParam.from_(dstore.attrs)
    N = len(dstore['assetcol'])
    R = len(dstore['rlzs_assoc'].realizations)
    L = len(dstore.get_attr('composite_risk_model', 'loss_types'))
    I = ast.literal_eval(dstore.attrs.get('insured_losses', 'False')) + 1
    ct = oq.concurrent_tasks
    size_bytes = N * R * L * I * 8 * ct  # 8 byte floats
    return (
        '%d asset(s) x %d realization(s) x %d loss type(s) x %d losses x '
        '8 bytes x %d tasks = %s' % (N, R, L, I, ct, humansize(size_bytes)))


@view.add('ebr_data_transfer')
def ebr_data_transfer(token, dstore):
    """
    Display the data transferred in an event based risk calculation
    """
    attrs = dstore['agg_loss_table'].attrs
    sent = humansize(attrs['sent'])
    received = humansize(attrs['tot_received'])
    return 'Event Based Risk: sent %s, received %s' % (sent, received)


# for scenario_risk
@view.add('totlosses')
def view_totlosses(token, dstore):
    """
    This is a debugging view. You can use it to check that the total
    losses, i.e. the losses obtained by summing the average losses on
    all assets are indeed equal to the aggregate losses. This is a
    sanity check for the correctness of the implementation.
    """
    if dstore.attrs['insured_losses'] == 'True':
        stats = ('mean', 'mean_ins')
    else:
        stats = ('mean',)
    avglosses = dstore['losses_by_asset'].value
    dtlist = [('%s-%s' % (name, stat), numpy.float32)
              for name in avglosses.dtype.names for stat in stats]
    zero = numpy.zeros(avglosses.shape[1:], numpy.dtype(dtlist))
    for name in avglosses.dtype.names:
        for stat in stats:
            for rec in avglosses:
                zero['%s-%s' % (name, stat)] += rec[name][stat]
    return rst_table(zero, fmt='%.6E')


def sum_table(records):
    """
    Used to compute summaries. The records are assumed to have numeric
    fields, except the first field which is ignored, since it typically
    contains a label. Here is an example:

    >>> sum_table([('a', 1), ('b', 2)])
    ['total', 3]
    """
    size = len(records[0])
    result = [None] * size
    firstrec = records[0]
    for i in range(size):
        if isinstance(firstrec[i], (numbers.Number, numpy.ndarray)):
            result[i] = sum(rec[i] for rec in records)
        else:
            result[i] = 'total'
    return result


# this is used by the ebr calculator
@view.add('mean_avg_losses')
def view_mean_avg_losses(token, dstore):
    try:
        array = dstore['avg_losses-stats']  # shape (N, S)
        data = array[:, 0]
    except KeyError:
        array = dstore['avg_losses-rlzs']  # shape (N, R)
        data = array[:, 0]
    assets = util.get_assets(dstore)
    losses = util.compose_arrays(assets, data)
    losses.sort()
    return rst_table(losses, fmt='%8.6E')


# this is used by the classical calculator
@view.add('loss_curves_avg')
def view_loss_curves_avg(token, dstore):
    """
    Returns the average losses computed from the loss curves; for each
    asset shows all realizations.
    """
    array = dstore['loss_curves-rlzs'].value  # shape (N, R)
    n, r = array.shape
    lt_dt = numpy.dtype([(lt, numpy.float32, r) for lt in array.dtype.names])
    avg = numpy.zeros(n, lt_dt)
    for lt in array.dtype.names:
        array_lt = array[lt]
        for i, row in enumerate(array_lt):
            avg[lt][i] = row['avg']
    assets = util.get_assets(dstore)
    losses = util.compose_arrays(assets, avg)
    return rst_table(losses, fmt='%8.6E')


@view.add('exposure_info')
def view_exposure_info(token, dstore):
    """
    Display info about the exposure model
    """
    assetcol = dstore['assetcol'][:]
    taxonomies = dstore['taxonomies'][:]
    counts = numpy.zeros(len(taxonomies), numpy.uint32)
    for ass in assetcol:
        tax_idx = ass['taxonomy']
        counts[tax_idx] += 1
    tbl = zip(taxonomies, counts)
    data = [('#assets', len(assetcol)),
            ('#taxonomies', len(taxonomies))]
    return rst_table(data) + '\n\n' + rst_table(
        tbl, header=['Taxonomy', '#Assets'])


@view.add('assetcol')
def view_assetcol(token, dstore):
    """
    Display the exposure in CSV format
    """
    assetcol = dstore['assetcol'].value
    taxonomies = dstore['taxonomies'].value
    header = list(assetcol.dtype.names)
    columns = [None] * len(header)
    for i, field in enumerate(header):
        if field == 'taxonomy':
            columns[i] = taxonomies[assetcol[field]]
        else:
            columns[i] = assetcol[field]
    return write_csv(io.StringIO(), [header] + list(zip(*columns)))


def get_max_gmf_size(dstore):
    """
    Extract info about the largest GMF
    """
    oq = OqParam.from_(dstore.attrs)
    n_sites = len(dstore['sitecol'].complete)
    rlzs_assoc = dstore['rlzs_assoc']
    num_ruptures = dstore.get_attr('etags', 'num_ruptures')
    col = num_ruptures.argmax()
    n_ruptures = num_ruptures[col]
    trt_id = rlzs_assoc.csm_info.get_trt_id(col)
    gsims = rlzs_assoc.gsims_by_trt_id[trt_id]
    n_imts = len(oq.imtls)
    n_rlzs = max(len(rlzs_assoc[trt_id, gsim]) for gsim in gsims)
    size = n_sites * n_rlzs * n_ruptures * n_imts * 4  # 4 bytes per float
    return dict(n_rlzs=n_rlzs, n_imts=n_imts, n_sites=n_sites, size=size,
                n_ruptures=n_ruptures, humansize=humansize(size), col=col,
                trt=rlzs_assoc.csm_info.tmdict[trt_id].trt)


@view.add('biggest_ebr_gmf')
def view_biggest_ebr_gmf(token, dstore):
    """
    Returns the size of the biggest GMF in an event based risk calculation
    """
    msg = ('The largest GMF block is for collection #%(col)d of type %(trt)r,'
           '\ncontains %(n_imts)d IMT(s), %(n_sites)d site(s), %(n_rlzs)d '
           'realization(s), and has a size of %(humansize)s / num_tasks')
    return msg % get_max_gmf_size(dstore)


@view.add('fullreport')
def view_fullreport(token, dstore):
    """
    Display an .rst report about the computation
    """
    # avoid circular imports
    from openquake.commonlib.reportwriter import ReportWriter
    return ReportWriter(dstore).make_report()


def performance_view(dstore):
    """
    Returns the performance view as a numpy array.
    """
    data = sorted(dstore['performance_data'], key=operator.itemgetter(0))
    out = []
    for operation, group in itertools.groupby(data, operator.itemgetter(0)):
        counts = 0
        time = 0
        mem = 0
        for _operation, time_sec, memory_mb, counts_ in group:
            counts += counts_
            time += time_sec
            mem = max(mem, memory_mb)
        out.append((operation, time, mem, counts))
    out.sort(key=operator.itemgetter(1), reverse=True)  # sort by time
    return numpy.array(out, perf_dt)


@view.add('performance')
def view_performance(token, dstore):
    """
    Display performance information
    """
    return rst_table(performance_view(dstore))


@view.add('required_params_per_trt')
def view_required_params_per_trt(token, dstore):
    """
    Display the parameters needed by each tectonic region type
    """
    gsims_per_trt_id = sorted(dstore['rlzs_assoc'].gsims_by_trt_id.items())
    tbl = []
    for trt_id, gsims in gsims_per_trt_id:
        maker = ContextMaker(gsims)
        distances = maker.REQUIRES_DISTANCES
        siteparams = maker.REQUIRES_SITES_PARAMETERS
        ruptparams = maker.REQUIRES_RUPTURE_PARAMETERS
        tbl.append((trt_id, gsims, distances, siteparams, ruptparams))
    return rst_table(
        tbl, header='trt_id gsims distances siteparams ruptparams'.split())
