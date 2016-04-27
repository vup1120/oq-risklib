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

"""
From Node objects to NRML files and viceversa
------------------------------------------------------

It is possible to save a Node object into a NRML file by using the
function ``write(nodes, output)`` where output is a file
object. If you want to make sure that the generated file is valid
according to the NRML schema just open it in 'w+' mode: immediately
after writing it will be read and validated. It is also possible to
convert a NRML file into a Node object with the routine
``read(node, input)`` where input is the path name of the
NRML file or a file object opened for reading. The file will be
validated as soon as opened.

For instance an exposure file like the following::

  <?xml version='1.0' encoding='utf-8'?>
  <nrml xmlns="http://openquake.org/xmlns/nrml/0.4"
        xmlns:gml="http://www.opengis.net/gml">
    <exposureModel
        id="my_exposure_model_for_population"
        category="population"
        taxonomySource="fake population datasource">

      <description>
        Sample population
      </description>

      <assets>
        <asset id="asset_01" number="7" taxonomy="IT-PV">
            <location lon="9.15000" lat="45.16667" />
        </asset>

        <asset id="asset_02" number="7" taxonomy="IT-CE">
            <location lon="9.15333" lat="45.12200" />
        </asset>
      </assets>
    </exposureModel>
  </nrml>

can be converted as follows:

>> nrml = read(<path_to_the_exposure_file.xml>)

Then subnodes and attributes can be conveniently accessed:

>> nrml.exposureModel.assets[0]['taxonomy']
'IT-PV'
>> nrml.exposureModel.assets[0]['id']
'asset_01'
>> nrml.exposureModel.assets[0].location['lon']
'9.15000'
>> nrml.exposureModel.assets[0].location['lat']
'45.16667'

The Node class provides no facility to cast strings into Python types;
this is a job for the LiteralNode class which can be subclassed and
supplemented by a dictionary of validators.
"""
from __future__ import print_function
import re
import sys
import logging
import itertools

import numpy

from openquake.baselib.general import CallableDict
from openquake.baselib.python3compat import unicode, raise_
from openquake.commonlib import valid, writers
from openquake.commonlib.node import (
    node_to_xml, Node, LiteralNode, node_from_elem, striptag,
    parse as xmlparse, iterparse, context)
from openquake.risklib import scientific
from openquake.commonlib import InvalidFile

F64 = numpy.float64
NAMESPACE = 'http://openquake.org/xmlns/nrml/0.4'
NRML05 = 'http://openquake.org/xmlns/nrml/0.5'
GML_NAMESPACE = 'http://www.opengis.net/gml'
SERIALIZE_NS_MAP = {None: NAMESPACE, 'gml': GML_NAMESPACE}
PARSE_NS_MAP = {'nrml': NAMESPACE, 'gml': GML_NAMESPACE}


class NRMLFile(object):
    """
    Context-managed output object which accepts either a path or a file-like
    object.

    Behaves like a file.
    """

    def __init__(self, dest, mode='r'):
        self._dest = dest
        self._mode = mode
        self._file = None

    def __enter__(self):
        if isinstance(self._dest, (unicode, bytes)):
            self._file = open(self._dest, self._mode)
        else:
            # assume it is a file-like; don't change anything
            self._file = self._dest
        return self._file

    def __exit__(self, *args):
        self._file.close()


def get_tag_version(nrml_node):
    """
    Extract from a node of kind NRML the tag and the version. For instance
    from '{http://openquake.org/xmlns/nrml/0.4}fragilityModel' one gets
    the pair ('fragilityModel', 'nrml/0.4').
    """
    version, tag = re.search(r'(nrml/[\d\.]+)\}(\w+)', nrml_node.tag).groups()
    return tag, version


def parse(fname, *args):
    """
    Parse a NRML file and return an associated Python object. It works by
    calling nrml.read() and build() in sequence.
    """
    [node] = read(fname)
    return build(node, fname, *args)


# ######################### build definitions ############################ #

build = CallableDict(keyfunc=get_tag_version)
# dictionary of functions with at least two arguments, node and fname


# TODO: add proper validation for exposureModel; this requires knowledge
# of the job.ini files
@build.add(('exposureModel', 'nrml/0.4'), ('exposureModel', 'nrml/0.5'),
           ('siteModel', 'nrml/0.4'), ('siteModel', 'nrml/0.5'),)
def build_exposure(node, fname):
    return node


@build.add(('vulnerabilityModel', 'nrml/0.4'))
def get_vulnerability_functions_04(node, fname):
    """
    :param node:
        a vulnerabilityModel node
    :param fname:
        path to the vulnerability file
    :returns:
        a dictionary imt, taxonomy -> vulnerability function
    """
    logging.warn('Please upgrade %s to NRML 0.5', fname)
    # NB: the IMTs can be duplicated and with different levels, each
    # vulnerability function in a set will get its own levels
    imts = set()
    taxonomies = set()
    # imt, taxonomy -> vulnerability function
    vmodel = scientific.VulnerabilityModel(**node.attrib)
    for vset in node:
        imt_str, imls, min_iml, max_iml, imlUnit = ~vset.IML
        imts.add(imt_str)
        for vfun in vset.getnodes('discreteVulnerability'):
            taxonomy = vfun['vulnerabilityFunctionID']
            if taxonomy in taxonomies:
                raise InvalidFile(
                    'Duplicated vulnerabilityFunctionID: %s: %s, line %d' %
                    (taxonomy, fname, vfun.lineno))
            taxonomies.add(taxonomy)
            with context(fname, vfun):
                loss_ratios = ~vfun.lossRatio
                coefficients = ~vfun.coefficientsVariation
            if len(loss_ratios) != len(imls):
                raise InvalidFile(
                    'There are %d loss ratios, but %d imls: %s, line %d' %
                    (len(loss_ratios), len(imls), fname,
                     vfun.lossRatio.lineno))
            if len(coefficients) != len(imls):
                raise InvalidFile(
                    'There are %d coefficients, but %d imls: %s, line %d' %
                    (len(coefficients), len(imls), fname,
                     vfun.coefficientsVariation.lineno))
            with context(fname, vfun):
                vmodel[imt_str, taxonomy] = scientific.VulnerabilityFunction(
                    taxonomy, imt_str, imls, loss_ratios, coefficients,
                    vfun['probabilisticDistribution'])
    return vmodel


@build.add(('vulnerabilityModel', 'nrml/0.5'))
def get_vulnerability_functions_05(node, fname):
    """
    :param node:
        a vulnerabilityModel node
    :param fname:
        path of the vulnerability filter
    :returns:
        a dictionary imt, taxonomy -> vulnerability function
    """
    # NB: the IMTs can be duplicated and with different levels, each
    # vulnerability function in a set will get its own levels
    taxonomies = set()
    vmodel = scientific.VulnerabilityModel(**node.attrib)
    # imt, taxonomy -> vulnerability function
    for vfun in node.getnodes('vulnerabilityFunction'):
        with context(fname, vfun):
            imt = vfun.imls['imt']
            imls = numpy.array(~vfun.imls)
            taxonomy = vfun['id']
        if taxonomy in taxonomies:
            raise InvalidFile(
                'Duplicated vulnerabilityFunctionID: %s: %s, line %d' %
                (taxonomy, fname, vfun.lineno))
        if vfun['dist'] == 'PM':
            loss_ratios, probs = [], []
            for probabilities in vfun[1:]:
                loss_ratios.append(probabilities['lr'])
                probs.append(valid.probabilities(~probabilities))
            probs = numpy.array(probs)
            assert probs.shape == (len(loss_ratios), len(imls))
            vmodel[imt, taxonomy] = (
                scientific.VulnerabilityFunctionWithPMF(
                    taxonomy, imt, imls, numpy.array(loss_ratios),
                    probs))  # the seed will be set by readinput.get_risk_model
        else:
            with context(fname, vfun):
                loss_ratios = ~vfun.meanLRs
                coefficients = ~vfun.covLRs
            if len(loss_ratios) != len(imls):
                raise InvalidFile(
                    'There are %d loss ratios, but %d imls: %s, line %d' %
                    (len(loss_ratios), len(imls), fname,
                     vfun.meanLRs.lineno))
            if len(coefficients) != len(imls):
                raise InvalidFile(
                    'There are %d coefficients, but %d imls: %s, '
                    'line %d' % (len(coefficients), len(imls), fname,
                                 vfun.covLRs.lineno))
            with context(fname, vfun):
                vmodel[imt, taxonomy] = scientific.VulnerabilityFunction(
                    taxonomy, imt, imls, loss_ratios, coefficients,
                    vfun['dist'])
    return vmodel


# ########################### fragility ############################### #


def ffconvert(fname, limit_states, ff, min_iml=1E-10):
    """
    Convert a fragility function into a numpy array plus a bunch
    of attributes.

    :param fname: path to the fragility model file
    :param limit_states: expected limit states
    :param ff: fragility function node
    :returns: a pair (array, dictionary)
    """
    with context(fname, ff):
        ffs = ff[1:]
        imls = ff.imls
    nodamage = imls.attrib.get('noDamageLimit')
    if nodamage == 0:
        # use a cutoff to avoid log(0) in GMPE.to_distribution_values
        logging.warn('Found a noDamageLimit=0 in %s, line %s, '
                     'using %g instead', fname, ff.lineno, min_iml)
        nodamage = min_iml
    with context(fname, imls):
        attrs = dict(format=ff['format'],
                     imt=imls['imt'],
                     nodamage=nodamage)

    LS = len(limit_states)
    if LS != len(ffs):
        with context(fname, ff):
            raise InvalidFile('expected %d limit states, found %d' %
                              (LS, len(ffs)))
    if ff['format'] == 'continuous':
        minIML = float(imls['minIML'])
        if minIML == 0:
            # use a cutoff to avoid log(0) in GMPE.to_distribution_values
            logging.warn('Found minIML=0 in %s, line %s, using %g instead',
                         fname, imls.lineno, min_iml)
            minIML = min_iml
        attrs['minIML'] = minIML
        attrs['maxIML'] = float(imls['maxIML'])
        array = numpy.zeros(LS, [('mean', F64), ('stddev', F64)])
        for i, ls, node in zip(range(LS), limit_states, ff[1:]):
            if ls != node['ls']:
                with context(fname, node):
                    raise InvalidFile('expected %s, found' %
                                      (ls, node['ls']))
            array['mean'][i] = node['mean']
            array['stddev'][i] = node['stddev']
    elif ff['format'] == 'discrete':
        attrs['imls'] = valid.positivefloats(~imls)
        valid.check_levels(attrs['imls'], attrs['imt'])
        num_poes = len(attrs['imls'])
        array = numpy.zeros((LS, num_poes))
        for i, ls, node in zip(range(LS), limit_states, ff[1:]):
            with context(fname, node):
                if ls != node['ls']:
                    raise InvalidFile('expected %s, found' %
                                      (ls, node['ls']))
                poes = (~node if isinstance(~node, list)
                        else valid.probabilities(~node))
                if len(poes) != num_poes:
                    raise InvalidFile('expected %s, found' %
                                      (num_poes, len(poes)))
                array[i, :] = poes
    # NB: the format is constrained in nrml.FragilityNode to be either
    # discrete or continuous, there is no third option
    return array, attrs


@build.add(('fragilityModel', 'nrml/0.5'))
def get_fragility_model(node, fname):
    """
    :param node:
        a vulnerabilityModel node
    :param fname:
        path to the vulnerability file
    :returns:
        a dictionary imt, taxonomy -> fragility function list
    """
    with context(fname, node):
        fid = node['id']
        asset_category = node['assetCategory']
        loss_type = node['lossCategory']
        description = ~node.description
        limit_states = ~node.limitStates
        ffs = node[2:]
    fmodel = scientific.FragilityModel(
        fid, asset_category, loss_type, description, limit_states)
    for ff in ffs:
        imt_taxo = ff.imls['imt'], ff['id']
        array, attrs = ffconvert(fname, limit_states, ff)
        ffl = scientific.FragilityFunctionList(array)
        vars(ffl).update(attrs)
        fmodel[imt_taxo] = ffl
    return fmodel


# ################################## consequences ########################## #

@build.add(('consequenceModel', 'nrml/0.5'))
def get_consequence_model(node, fname):
    with context(fname, node):
        description = ~node.description  # make sure it is there
        limitStates = ~node.limitStates  # make sure it is there
        # ASK: is the 'id' mandatory?
        node['assetCategory']  # make sure it is there
        node['lossCategory']  # make sure it is there
        cfs = node[2:]
    functions = {}
    for cf in cfs:
        with context(fname, cf):
            params = []
            if len(limitStates) != len(cf):
                raise ValueError(
                    'Expected %d limit states, got %d' %
                    (len(limitStates), len(cf)))
            for ls, param in zip(limitStates, cf):
                with context(fname, param):
                    if param['ls'] != ls:
                        raise ValueError('Expected %r, got %r' %
                                         (ls, param['ls']))
                    params.append((param['mean'], param['stddev']))
            functions[cf['id']] = scientific.ConsequenceFunction(
                cf['id'], cf['dist'], params)
    attrs = node.attrib.copy()
    attrs.update(description=description, limitStates=limitStates)
    cmodel = scientific.ConsequenceModel(**attrs)
    cmodel.update(functions)
    return cmodel


# utility to convert the old, deprecated format
def convert_fragility_model_04(node, fname, fmcounter=itertools.count(1)):
    """
    :param node:
        an :class:`openquake.commonib.node.LiteralNode` in NRML 0.4
    :param fname:
        path of the fragility file
    :returns:
        an :class:`openquake.commonib.node.LiteralNode` in NRML 0.5
    """
    convert_type = {"lognormal": "logncdf"}
    new = LiteralNode('fragilityModel',
                      dict(assetCategory='building',
                           lossCategory='structural',
                           id='fm_%d_converted_from_NRML_04' %
                           next(fmcounter)))
    with context(fname, node):
        fmt = node['format']
        descr = ~node.description
        limit_states = ~node.limitStates
    new.append(LiteralNode('description', {}, descr))
    new.append((LiteralNode('limitStates', {}, ' '.join(limit_states))))
    for ffs in node[2:]:
        IML = ffs.IML
        # NB: noDamageLimit = None is different than zero
        nodamage = ffs.attrib.get('noDamageLimit')
        ff = LiteralNode('fragilityFunction', {'format': fmt})
        ff['id'] = ~ffs.taxonomy
        ff['shape'] = convert_type[ffs.attrib.get('type', 'lognormal')]
        if fmt == 'continuous':
            with context(fname, IML):
                attr = dict(imt=IML['IMT'],
                            minIML=IML['minIML'],
                            maxIML=IML['maxIML'])
                if nodamage is not None:
                    attr['noDamageLimit'] = nodamage
                ff.append(LiteralNode('imls', attr))
            for ffc in ffs[2:]:
                with context(fname, ffc):
                    ls = ffc['ls']
                    param = ffc.params
                with context(fname, param):
                    m, s = param['mean'], param['stddev']
                ff.append(LiteralNode('params', dict(ls=ls, mean=m, stddev=s)))
        else:  # discrete
            with context(fname, IML):
                imls = ' '.join(map(str, (~IML)[1]))
                attr = dict(imt=IML['IMT'])
            if nodamage is not None:
                attr['noDamageLimit'] = nodamage
            ff.append(LiteralNode('imls', attr, imls))
            for ffd in ffs[2:]:
                ls = ffd['ls']
                with context(fname, ffd):
                    poes = ' '.join(map(str, ~ffd.poEs))
                ff.append(LiteralNode('poes', dict(ls=ls), poes))
        new.append(ff)
    return new


@build.add(('fragilityModel', 'nrml/0.4'))
def get_fragility_model_04(fmodel, fname):
    """
    :param fmodel:
        a fragilityModel node
    :param fname:
        path of the fragility file
    :returns:
        an :class:`openquake.risklib.scientific.FragilityModel` instance
    """
    logging.warn('Please upgrade %s to NRML 0.5', fname)
    node05 = convert_fragility_model_04(fmodel, fname)
    node05.limitStates.text = node05.limitStates.text.split()
    return get_fragility_model(node05, fname)

# ######################## nodefactory definitions ######################## #

nodefactory = CallableDict(keyfunc=striptag)


@nodefactory.add('sourceModel', 'simpleFaultRupture', 'complexFaultRupture',
                 'singlePlaneRupture', 'multiPlanesRupture')
class ValidNode(LiteralNode):
    """
    A subclass of :class:`LiteralNode` to be used when parsing sources
    and ruptures from NRML files.
    """
    validators = dict(
        strike=valid.strike_range,
        dip=valid.dip_range,
        rake=valid.rake_range,
        magnitude=valid.positivefloat,
        lon=valid.longitude,
        lat=valid.latitude,
        depth=valid.positivefloat,
        upperSeismoDepth=valid.positivefloat,
        lowerSeismoDepth=valid.positivefloat,
        posList=valid.posList,
        pos=valid.lon_lat,
        aValue=float,
        bValue=valid.positivefloat,
        magScaleRel=valid.mag_scale_rel,
        tectonicRegion=str,
        ruptAspectRatio=valid.positivefloat,
        maxMag=valid.positivefloat,
        minMag=valid.positivefloat,
        binWidth=valid.positivefloat,
        probability=valid.probability,
        hypoDepth=valid.probability_depth,
        occurRates=valid.positivefloats,
        probs_occur=valid.pmf,
        weight=valid.probability,
        alongStrike=valid.probability,
        downDip=valid.probability,
        totalMomentRate=valid.positivefloat,
        characteristicRate=valid.positivefloat,
        characteristicMag=valid.positivefloat,
        magnitudes=valid.positivefloats,
        id=valid.simple_id,
        discretization=valid.compose(valid.positivefloat, valid.nonzero),
        )


nodefactory.add('siteModel')(LiteralNode)


# insuranceLimit and deductible can be either tags or attributes!
def float_or_flag(value, isAbsolute=None):
    """
    Validate the attributes/tags insuranceLimit and deductible
    """
    if isAbsolute is None:  # considering the insuranceLimit attribute
        return valid.positivefloat(value)
    else:
        return valid.boolean(isAbsolute)


@nodefactory.add('exposureModel')
class ExposureDataNode(LiteralNode):
    validators = dict(
        id=valid.asset_id,
        description=valid.utf8_not_empty,
        name=valid.cost_type,
        type=valid.name,
        insuranceLimit=float_or_flag,
        deductible=float_or_flag,
        occupants=valid.positivefloat,
        value=valid.positivefloat,
        retrofitted=valid.positivefloat,
        number=valid.compose(valid.positivefloat, valid.nonzero),
        lon=valid.longitude,
        lat=valid.latitude,
    )


@nodefactory.add('vulnerabilityModel')
class VulnerabilityNode(LiteralNode):
    """
    Literal Node class used to validate discrete vulnerability functions
    """
    validators = dict(
        vulnerabilitySetID=str,  # any ASCII string is fine
        vulnerabilityFunctionID=str,  # any ASCII string is fine
        assetCategory=str,  # any ASCII string is fine
        # the assetCategory here has nothing to do with the category
        # in the exposure model and it is not used by the engine
        lossCategory=valid.utf8,  # a description field
        IML=valid.IML,
        imt=valid.intensity_measure_type,
        imls=lambda text, imt: valid.positivefloats(text),
        lr=valid.probability,
        lossRatio=valid.positivefloats,
        coefficientsVariation=valid.positivefloats,
        probabilisticDistribution=valid.Choice('LN', 'BT'),
        dist=valid.Choice('LN', 'BT', 'PM'),
        meanLRs=valid.positivefloats,
        covLRs=valid.positivefloats,
    )


@nodefactory.add('fragilityModel', 'consequenceModel')
class FragilityNode(LiteralNode):
    """
    Literal Node class used to validate fragility functions and consequence
    functions.
    """
    validators = dict(
        id=valid.utf8,  # no constraints on the taxonomy
        format=valid.ChoiceCI('discrete', 'continuous'),
        assetCategory=valid.utf8,
        dist=valid.Choice('LN'),
        mean=valid.positivefloat,
        stddev=valid.positivefloat,
        lossCategory=valid.name,
        poes=lambda text, **kw: valid.positivefloats(text),
        imt=valid.intensity_measure_type,
        IML=valid.IML,
        minIML=valid.positivefloat,
        maxIML=valid.positivefloat,
        limitStates=valid.namelist,
        description=valid.utf8_not_empty,
        type=valid.ChoiceCI('lognormal'),
        poEs=valid.probabilities,
        noDamageLimit=valid.NoneOr(valid.positivefloat),
    )

valid_loss_types = valid.Choice('structural', 'nonstructural', 'contents',
                                'business_interruption', 'occupants')


@nodefactory.add('aggregateLossCurve', 'hazardCurves', 'hazardMap')
class CurveNode(LiteralNode):
    validators = dict(
        investigationTime=valid.positivefloat,
        loss_type=valid_loss_types,
        unit=str,
        poEs=valid.probabilities,
        gsimTreePath=lambda v: v.split('_'),
        sourceModelTreePath=lambda v: v.split('_'),
        losses=valid.positivefloats,
        averageLoss=valid.positivefloat,
        stdDevLoss=valid.positivefloat,
        poE=valid.positivefloat,
        IMLs=valid.positivefloats,
        pos=valid.lon_lat,
        IMT=str,
        saPeriod=valid.positivefloat,
        saDamping=valid.positivefloat,
        node=valid.lon_lat_iml,
        quantileValue=valid.positivefloat,
    )


@nodefactory.add('bcrMap')
class BcrNode(LiteralNode):
    validators = dict(
        assetLifeExpectancy=valid.positivefloat,
        interestRate=valid.positivefloat,
        lossCategory=str,
        lossType=valid_loss_types,
        quantileValue=valid.positivefloat,
        statistics=valid.Choice('quantile'),
        unit=str,
        pos=valid.lon_lat,
        aalOrig=valid.positivefloat,
        aalRetr=valid.positivefloat,
        ratio=valid.positivefloat)


def asset_mean_stddev(value, assetRef, mean, stdDev):
    return assetRef, valid.positivefloat(mean), valid.positivefloat(stdDev)


@nodefactory.add('collapseMap')
class CollapseNode(LiteralNode):
    validators = dict(
        pos=valid.lon_lat,
        cf=asset_mean_stddev,
    )


def damage_triple(value, ds, mean, stddev):
    return ds, valid.positivefloat(mean), valid.positivefloat(stddev)


@nodefactory.add('totalDmgDist', 'dmgDistPerAsset', 'dmgDistPerTaxonomy')
class DamageNode(LiteralNode):
    validators = dict(
        damage=damage_triple,
        pos=valid.lon_lat,
        damageStates=valid.namelist,
    )


@nodefactory.add('gmfCollection')
class GmfNode(LiteralNode):
    """
    Class used to convert nodes such as::

     <gmf IMT="PGA" ruptureId="scenario-0000000001" >
        <node gmv="0.365662734506" lat="0.0" lon="0.0"/>
        <node gmv="0.256181251586" lat="0.1" lon="0.0"/>
        <node gmv="0.110685275111" lat="0.2" lon="0.0"/>
     </gmf>

    into LiteralNode objects.
    """
    validators = dict(
        gmv=valid.positivefloat,
        lon=valid.longitude,
        lat=valid.latitude)

# TODO: extend the validation to the following nodes
# see https://bugs.launchpad.net/oq-engine/+bug/1381066
nodefactory.add(
    'disaggMatrices',
    'logicTree',
    'lossCurves',
    'lossFraction',
    'lossMap',
    'stochasticEventSet',
    'stochasticEventSetCollection',
    'uniformHazardSpectra',
    )(LiteralNode)


def read(source, chatty=True):
    """
    Convert a NRML file into a validated LiteralNode object. Keeps
    the entire tree in memory.

    :param source:
        a file name or file object open for reading
    """
    nrml = xmlparse(source).getroot()
    assert striptag(nrml.tag) == 'nrml', nrml.tag
    # extract the XML namespace URL ('http://openquake.org/xmlns/nrml/0.5')
    xmlns = nrml.tag.split('}')[0][1:]
    if xmlns != NRML05 and chatty:
        # for the moment NRML04 is still supported, so we hide the warning
        logging.debug('%s is at an outdated version: %s', source, xmlns)
    subnodes = []
    for elem in nrml:
        nodecls = nodefactory[striptag(elem.tag)]
        try:
            subnodes.append(node_from_elem(elem, nodecls))
        except ValueError as exc:
            raise ValueError('%s of %s' % (exc, source))
    return LiteralNode(
        'nrml', {'xmlns': xmlns, 'xmlns:gml': GML_NAMESPACE},
        nodes=subnodes)


def read_lazy(source, lazytags):
    """
    Convert a NRML file into a validated LiteralNode object. The
    tree is lazy, i.e. you access nodes by iterating on them.

    :param source:
        a file name or file object open for reading
    :param lazytags:
       the name of nodes which subnodes must be read lazily
    :returns:
       a list of nodes; some of them will contain lazy subnodes
    """
    nodes = []
    try:
        for _, el in iterparse(source, remove_comments=True):
            tag = striptag(el.tag)
            if tag in nodefactory:  # NRML tag
                nodes.append(
                    node_from_elem(el, nodefactory[tag], lazy=lazytags))
                el.clear()  # save memory
    except:
        etype, exc, tb = sys.exc_info()
        msg = str(exc)
        if str(source) not in msg:
            msg = '%s in %s' % (msg, source)
        raise_(etype, msg, tb)
    return nodes


def write(nodes, output=sys.stdout, fmt='%10.7E', gml=True):
    """
    Convert nodes into a NRML file. output must be a file
    object open in write mode. If you want to perform a
    consistency check, open it in read-write mode, then it will
    be read after creation and validated.

    :params nodes: an iterable over Node objects
    :params output: a file-like object in write or read-write mode
    """
    root = Node('nrml', nodes=nodes)
    namespaces = {NRML05: ''}
    if gml:
        namespaces[GML_NAMESPACE] = 'gml:'
    with writers.floatformat(fmt):
        node_to_xml(root, output, namespaces)
    if hasattr(output, 'mode') and '+' in output.mode:  # read-write mode
        output.seek(0)
        read(output)  # validate the written file


if __name__ == '__main__':
    import sys
    for fname in sys.argv[1:]:
        print('****** %s ******' % fname)
        print(read(fname).to_str())
        print()
