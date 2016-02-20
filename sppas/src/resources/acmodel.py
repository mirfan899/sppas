#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: acmodel.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import codecs
import logging
import rutils
import collections
import json

from dependencies.grako.parsing import graken, Parser

__all__ = [
    'HMM',
    'AcModel',
    'HtkIO',
    'HtkModelSemantics',
    'HtkModelParser'
]

# ---------------------------------------------------------------------------

class HtkIO:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: HTK-ASCII acoustic models reader/writer.

    This class is able to load and save HMM-based acoustic models from
    an HTK-ASCII file.

    """
    def __init__(self, *args):
        """
        Create an HtkIO instance and eventually,
        load a model from one or more files.

        @param args: Filenames of the model (e.g. macros and/or hmmdefs)

        """
        self.macros = None
        self.hmms   = None
        if args:
            self.load(*args)

    # -----------------------------------------------------------------------

    def load(self, *args):
        """
        Load an HTK model from one or more files.

        @param args: Filenames of the model (e.g. macros and/or hmmdefs)

        """
        text = ''
        for fnm in args:
            text += open(fnm).read()
            text += '\n'

        parser   = HtkModelParser()
        htkmodel = HtkModelSemantics()  # OrderedDict()
        model = parser.parse(text,
                    rule_name='model',
                    ignorecase=True,
                    semantics=htkmodel,
                    comments_re="\(\*.*?\*\)",
                    trace=False)
        self.macros = model['macros']
        self.hmms   = []
        for hmm in model['hmms']:
            newhmm = HMM()
            newhmm.set_name(hmm['name'])
            newhmm.set_definition(hmm['definition'])
            self.hmms.append(newhmm)

    # -----------------------------------------------------------------------

    def save(self, filename):
        """
        Save the model into a file, in HTK-ASCII standard format.

        @param filename: File where to save the model.

        """
        with open(filename, 'w') as f:
            if self.macros: f.write(self.serialize_macros())
            if self.hmms:   f.write(self.serialize_hmms())

    # -----------------------------------------------------------------------

    def set(self,macros,hmms):
        self.macros = macros
        self.hmms = hmms

    def set_macros(self,macros):
        self.macros = macros

    def set_hmms(self,hmms):
        self.hmms = hmms

    # -----------------------------------------------------------------------

    def serialize_macros(self):
        """
        Serialize macros into a string, in HTK-ASCII standard format.

        @return The HTK-ASCII macros as a string.

        """
        result = ''

        # First serialize the macros
        for macro in self.macros:
            if macro.get('options', None):
                result += '~o '
                for option in macro['options']['definition']:
                    result += self._serialize_option(option)

            elif macro.get('transition', None):
                result += '~t "{}"\n'.format(macro['transition']['name'])
                result += self._serialize_transp(macro['transition']['definition'])

            elif macro.get('variance', None):
                result += '~v "{}"\n'.format(macro['variance']['name'])
                result += self._serialize_variance(macro['variance']['definition'])

            elif macro.get('state', None):
                result += '~s "{}"\n'.format(macro['state']['name'])
                result += self._serialize_stateinfo(macro['state']['definition'])

            elif macro.get('mean', None):
                result += '~u "{}"\n'.format(macro['mean']['name'])
                result += self._serialize_mean(macro['mean']['definition'])

            elif macro.get('duration', None):
                result += '~d "{}"\n'.format(macro['duration']['name'])
                result += self._serialize_duration(macro['duration']['definition'])

            else:
                raise NotImplementedError('Cannot serialize {}'.format(macro))

        return result


    def serialize_hmms(self):
        """
        Serialize macros into a string, in HTK-ASCII standard format.

        @return The HTK-ASCII model as a string.

        """
        result= ''
        for hmm in self.hmms:
            if hmm.name is not None:
                result += self._serialize_name( hmm.name )
            result += self._serialize_definition( hmm.definition )

        return result

    # -----------------------------------------------------------------------

    def _serialize_name(self,name):
        return '~h "{}"\n'.format( name )


    def _serialize_definition(self,definition):
        result = ''

        result += '<BeginHMM>\n'
        if definition.get('options', None):
            for option in definition['options']:
                result += self._serialize_option(option)

        result += '<NumStates> {}\n'.format(definition['state_count'])

        for state in definition['states']:
            result += self._serialize_state(state)

        if definition.get('regression_tree', None) is not None:
            raise NotImplementedError('Cannot serialize {}'.format(definition['regression_tree']))

        result += self._serialize_transp(definition['transition'])

        if definition.get('duration', None) is not None:
            result += self._serialize_duration(definition['duration'])

        result += '<EndHMM>\n'

        return result


    def _serialize_option(self, option):
        result = ''
        if option.get('hmm_set_id', None) is not None:
            result += '<HmmSetId> {}'.format(option['hmm_set_id'])

        if option.get('stream_info', None) is not None:
            result += '<StreamInfo> {}'.format(option['stream_info']['count'])

            if option['stream_info'].get('sizes', None) is not None:
                result += ' {}'.format(' '.join(['{:d}'.format(v) for v in option['stream_info']['sizes']]))

        if option.get('vector_size', None) is not None:
            result += '<VecSize> {:d}'.format(option['vector_size'])

        if option.get('input_transform', None) is not None:
            raise NotImplementedError('Serialization of {} '
                                      'is not implemented.'.format(option['input_transform']))

        if option.get('covariance_kind', None) is not None:
            result += '<{}>'.format(option['covariance_kind'])

        if option.get('duration_kind', None) is not None:
            result += '<{}>'.format(option['duration_kind'])

        if option.get('parameter_kind', None) is not None:
            result += '<{}{}>'.format(option['parameter_kind']['base'],
                                      ''.join(option['parameter_kind']['options']))

        result += '\n'
        return result


    def _serialize_transp(self, definition):
        if isinstance(definition, basestring):
            return '~t "{}"\n'.format(definition)

        result = ''
        result += '<TransP> {}\n'.format(definition['dim'])
        result += '{}'.format(self._matrix_to_htk(definition['matrix']))
        return result


    def _serialize_variance(self, definition):
        if isinstance(definition, basestring):
            return '~v {}\n'.format(definition)

        result = ''
        result += '<Variance> {}\n'.format(definition['dim'])
        result += '{}'.format(self._array_to_htk(definition['vector']))
        return result


    def _serialize_mean(self, definition):
        if isinstance(definition, basestring):
            return '~u "{}"\n'.format(definition)

        result = ''
        result += '<Mean> {}\n'.format(definition['dim'])
        result += '{}'.format(self._array_to_htk(definition['vector']))
        return result


    def _serialize_duration(self, definition):
        if isinstance(definition, basestring):
            return '~d "{}"\n'.format(definition)

        result = ''
        result += '<Duration> {}\n'.format(definition['dim'])
        result += '{}'.format(self._array_to_htk(definition['vector']))
        return result


    def _serialize_weights(self, definition):
        if isinstance(definition, basestring):
            return '~w "{}"\n'.format(definition)

        result = ''
        result += '<SWeights> {}\n'.format(definition['dim'])
        result += '{}'.format(self._array_to_htk(definition['vector']))
        return result


    def _serialize_covariance(self, definition):
        result = ''
        if definition['variance'] is not None:
            result += self._serialize_variance(definition['variance'])

        else:
            raise NotImplementedError('Cannot serialize {}'.format(definition))

        return result


    def _serialize_mixpdf(self, definition):
        if isinstance(definition, basestring):
            return '~m "{}"\n'.format(definition)

        result = ''
        if definition.get('regression_class', None) is not None:
            result += '<RClass> {}\n'.format(definition['regression_class'])

        result += self._serialize_mean(definition['mean'])
        result += self._serialize_covariance(definition['covariance'])

        if definition.get('gconst', None) is not None:
            result += '<GConst> {:.6e}\n'.format(definition['gconst'])

        return result


    def _serialize_mixture(self, definition):
        result = ''

        if definition.get('index', None) is not None:
            result += '<Mixture> {} {:.6e}\n'.format(definition['index'], definition['weight'])

        result += self._serialize_mixpdf(definition['pdf'])
        return result


    def _serialize_stream(self, definition):
        result = ''

        if definition.get('dim', None) is not None:
            result += '<Stream> {}\n'.format(definition['dim'])

        if definition.get('mixtures', None) is not None:
            for mixture in definition['mixtures']:
                result += self._serialize_mixture(mixture)

        else:
            raise NotImplementedError('Cannot serialize {}'.format(definition))

        return result


    def _serialize_stateinfo(self, definition):
        if isinstance(definition, basestring):
            return '~s "{}"\n'.format(definition)

        result = ''
        if definition.get('streams_mixcount', None):
            result += '<NumMixes> {}\n'.format(' '.join(['{}'.format(v) for v in definition['streams_mixcount']]))

        if definition.get('weights', None) is not None:
            result += self._serialize_weights(definition['weights'])

        for stream in definition['streams']:
            result += self._serialize_stream(stream)

        if definition.get('duration', None) is not None:
            result += self._serialize_duration(definition['duration'])

        return result


    def _serialize_state(self, definition):
        result = ''

        result += '<State> {}\n'.format(definition['index'])
        result += self._serialize_stateinfo(definition['state'])

        return result


    def _array_to_htk(self, arr):
        return ' {}\n'.format(' '.join(['{:2.6e}'.format(value) for value in arr]))


    def _matrix_to_htk(self, mat):
        result = ''
        for arr in mat:
            result = result + self._array_to_htk(arr)
        return result


# ---------------------------------------------------------------------------

class HMM:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: HMM representation for one phone.

    Each hmm model of a phoneme is made of:
       - a 'name': str
       - a 'definition': OrderedDict

    Each definition is made of:
        - state_count: int
        - states: list
        - transition: OrderedDict
        - options
        - regression_tree
        - duration

    Each element of the states list is:
        - an index: int
        - a state: OrderedDict

    ... and so on!

    """
    def __init__(self):
        self.name = ""
        self.definition = None

    # -----------------------------------------------------------------------

    def set_name(self, name):
        self.name = name

    def set_definition(self, definition):
        self.definition = definition

    # -----------------------------------------------------------------------

    def create(self, states, transition, name=None):
        """
        Create the hmm and set it.

        @param states (OrderedDict)
        @param transition (OrderedDict)
        @param name (string)

        """
        self.name = name
        self.definition = self._create_default()

        self.definition['state_count'] = len(states) + 2
        self.definition['states'] = []
        for i, state in enumerate(states):
            hmm_state = self._create_default()
            hmm_state['index'] = i + 2
            hmm_state['state'] = state
            self.definition['states'].append(hmm_state)

        self.definition['transition'] = transition

    # -----------------------------------------------------------------------

    def load(self, filename):
        """
        Return the hmm described into the given filename.

        @return filename (str) File to read.

        """
        htkmodel = HtkIO( filename  )
        hmms = htkmodel.hmms
        if len(hmms) != 1:
            raise IOError

        htkhmm = hmms[0]
        self.name = htkhmm.name
        self.definition = htkhmm.definition

    # -----------------------------------------------------------------------

    def save(self, filename):
        """
        Save the hmm into the given filename.

        @return filename (str) File to write.

        """
        htkio = HtkIO()
        htkio.set_hmms([self])
        result = htkio.serialize_hmms()
        with open(filename, 'w') as f:
            f.write( result )

    # -----------------------------------------------------------------------

    def _create_default(self):
        return collections.defaultdict(lambda: None)


# ---------------------------------------------------------------------------

class AcModel:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Acoustic model representation.

    Hidden Markov Models (HMMs) provide a simple and effective framework for
    modeling time-varying spectral vector sequences. As a consequence, most
    of speech technology systems are based on HMMs.
    Each base phone is represented by a continuous density HMM, with transition
    probability parameters and output observation distributions.
    One of the most commonly used extensions to standard HMMs is to model the
    state-output distribution as a mixture model, a mixture of Gaussians is a
    highly flexible distribution able to model, for example, asymmetric and
    multi-modal distributed data.

    A model is made of:
       - a 'macro'.
       - 'hmms' models (one per phoneme): OrderedDict of HMM instances

    """

    def __init__(self):
        """
        Load an HTK model from one or more files.

        @param args: Filenames of the model (e.g. macros and/or hmmdefs)

        """
        self.macros = None
        self.hmms   = []

    # -----------------------------------------------------------------------

    def load_htk(self, *args):
        """
        Load an HTK model from one or more files.

        @param args: Filenames of the model (e.g. macros and/or hmmdefs)

        """
        htkmodel = HtkIO( *args )
        self.macros = htkmodel.macros
        self.hmms   = htkmodel.hmms

    # -----------------------------------------------------------------------

    def get_hmm(self, phone):
        """
        Return the hmm corresponding to the given phoneme.

        @param phone (str) the phoneme name to get hmm
        @raise ValueError if phoneme is not in the model

        """
        hmms = [h for h in self.hmms if h.name==phone]
        if len(hmms) == 1:
            return hmms[0]
        raise ValueError('%s not in the model'%phone)

    # -----------------------------------------------------------------------

    def append_hmm(self, hmm):
        """
        Append an HMM to the model.

        @param hmm (OrderedDict)
        @raise TypeError, ValueError

        """
        if isinstance(hmm,HMM) is False:
            raise TypeError('Expected an HMM instance. Got %s'%type(hmm))

        if hmm.name is None:
            raise TypeError('Expected an hmm with a name as key.')
        for h in self.hmms:
            if h.name == hmm.name:
                raise ValueError('Duplicate HMM is forbidden. %s already in the model.'%hmm.name)

        if hmm.definition is None:
            raise TypeError('Expected an hmm with a definition as key.')
        if hmm.definition.get('states',None) is None or hmm.definition.get('transition',None) is None:
            raise TypeError('Expected an hmm with a definition including states and transitions.')

        self.hmms.append(hmm)

    # -----------------------------------------------------------------------

    def pop_hmm(self, phone):
        """
        Remove an HMM of the model.

        @param phone (str) the phoneme name to get hmm
        @raise ValueError if phoneme is not in the model

        """
        hmm = self.get_hmm(phone)
        idx = self.hmms.index(hmm)
        self.hmms.pop(idx)

    # -----------------------------------------------------------------------

    def _interpolate_values(self, value1, value2, gamma):
        p1 = gamma * value1
        p2 = (1.-gamma) * value2
        return p1 + p2

    def _interpolate_vectors(self, vector1, vector2, gamma):
        v = []
        for v1,v2 in zip(vector1,vector2):
            v.append( self._interpolate_values(v1, v2, gamma) )
        return v


    def static_linear_interpolation_hmm(self, phone, hmm, gamma):
        """
        Static Linear Interpolation is perhaps one of the most straightforward
        manner to combine models. This is an efficient way for merging the GMMs
        of the component models.

        Gamma coefficient is applied to self and (1-Gamma) to the other hmm.

        @param phone (str) the name of the phoneme to interpolate.
        @param hmm (HMM) the hmm to be interpolated with.
        @param gamma (float) coefficient to apply to the model of phoneme.

        """
        # TODO: MUST COMPARE DICT STRUCTURES HERE

        shmm = self.get_hmm(phone)

        sstates = shmm.definition['states']
        ostates = hmm.definition['states']

        for sitem,oitem in zip(sstates,ostates): # a dict
            sstate = sitem['state']
            ostate = oitem['state']
            if type(sstate) != collections.OrderedDict or type(ostate) != collections.OrderedDict:
                continue
            sstreams = sstate['streams']
            ostreams = ostate['streams']

            for ss,os in zip(sstreams,ostreams): # a list
                smixtures = ss['mixtures']
                omixtures = os['mixtures']

                for smixture,omixture in zip(smixtures,omixtures): # a list of dict

                    if smixture['weight'] is not None:
                        smixture['weight'] = self._interpolate_values(smixture['weight'],omixture['weight'],gamma)

                    spdf = smixture['pdf']
                    opdf = omixture['pdf']

                    if spdf['mean']['dim'] != opdf['mean']['dim']:
                        raise TypeError
                    if spdf['covariance']['variance']['dim'] != opdf['covariance']['variance']['dim']:
                        raise TypeError

                    svector = spdf['mean']['vector']
                    ovector = opdf['mean']['vector']
                    spdf['mean']['vector'] = self._interpolate_vectors(svector,ovector,gamma)

                    svector = spdf['covariance']['variance']['vector']
                    ovector = opdf['covariance']['variance']['vector']
                    spdf['covariance']['variance']['vector'] = self._interpolate_vectors(svector,ovector,gamma)

                    spdf['gconst'] = self._interpolate_values(spdf['gconst'], opdf['gconst'], gamma)

        stransition = shmm.definition['transition']
        otransition = hmm.definition['transition']
        if type(stransition) != collections.OrderedDict or type(otransition) != collections.OrderedDict:
            return
        if stransition['dim'] != otransition['dim']:
            raise TypeError
        smatrix = stransition['matrix']
        omatrix = otransition['matrix']
        matrix = []
        for svector,ovector in zip(smatrix,omatrix):
            matrix.append( self._interpolate_vectors(svector,ovector,gamma) )
        stransition['matrix'] = matrix

    # -----------------------------------------------------------------------

    def create_model(self, macros, hmms):
        """
        Create an empty AcModel and return it.

        """
        model = AcModel()
        model.macros = macros
        model.hmms   = hmms
        return model

    # -----------------------------------------------------------------------

    def merge_model(self, other, gamma=1.):
        """
        Merge another model with self.
        All new phonemes are added and the shared ones are merged, using
        a static linear interpolation.

        Efficient ONLY on MONOPHONES models.

        @param other (AcModel) the AcModel to be merged with.
        @param gamma (float) coefficient to apply to the model: between 0.
        and 1. This means that a coefficient value of 1. indicates to keep
        the current version of each shared hmm.
        @return a tuple indicating the number of hmms: (appended,interpolated,keeped,changed)

        """
        if gamma < 0. or gamma > 1.:
            raise ValueError('Gamma coefficient must be between 0. and 1. Got %f'%gamma)
        if isinstance(other, AcModel) is False:
            raise TypeError('Expected an AcModel instance.')

        appended = 0
        interpolated = 0
        keeped = len(self.hmms)
        changed = 0
        for hmm in other.hmms:
            got = False
            for h in self.hmms:
                if h.name == hmm.name:
                    got = True
                    if gamma == 1.0:
                        pass
                    elif gamma == 0.:
                        self.pop_hmm( hmm.name )
                        self.append_hmm( hmm )
                        changed = changed + 1
                        keeped  = keeped  - 1
                    else:
                        self.static_linear_interpolation_hmm(hmm.name, hmm, gamma)
                        interpolated = interpolated + 1
                        keeped       = keeped       - 1
                    break
            if got is False:
                self.append_hmm(hmm)
                appended = appended + 1

        return (appended,interpolated,keeped,changed)

    # -----------------------------------------------------------------------

    def save_htk(self, filename):
        """
        Save the model into a file, in HTK-ASCII standard format.

        @param filename: File where to save the model.

        """
        htkmodel = HtkIO()
        htkmodel.set(self.macros,self.hmms)
        htkmodel.save( filename )

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------
    # TODO: Test all the create methods

    def _create_default(self):
        return collections.defaultdict(lambda: None)


    def _create_vector(self, vector):
        return {'dim': len(vector), 'vector': vector}


    def _create_square_matrix(self, mat):
        return {'dim': len(mat[0]), 'matrix': mat}


    def _create_transition(self, state_stay_probabilites=[0.6, 0.6, 0.7]):
        n_states = len(state_stay_probabilites) + 2
        transitions = []
        for i in range(n_states):
            transitions.append([ 0.]*n_states)
        transitions[0][1] = 1.
        for i, p in enumerate(state_stay_probabilites):
            transitions[i+1][i+1] = p
            transitions[i+1][i+2] = 1 - p

        return self.create_square_matrix(transitions)


    def _create_parameter_kind(self, base=None, options=[]):
        result = self.create_default()
        result['base'] = base
        result['options'] = options
        return result


    def _create_options(self, vector_size=None, parameter_kind=None):
        macro = self.create_default()
        options = []

        if vector_size:
            option = self.create_default()
            option['vector_size'] = vector_size
            options.append(option)
        if parameter_kind:
            option = self.create_default()
            option['parameter_kind'] = parameter_kind
            options.append(option)

        macro['options'] = {'definition': options}

        return macro


    def _create_gmm(self, means, variances, gconsts=None, weights=None):
        mixtures = []

        if means.ndim == 1:
            means = means[None, :]
            variances = variances[None, :]

        gmm = self.create_default()

        for i in range(means.shape[0]):
            mixture = self.create_default()
            mixture['pdf'] = self.create_default()
            mixture['pdf']['mean'] = self.create_vector(means[i])
            mixture['pdf']['covariance'] = self.create_default()
            mixture['pdf']['covariance']['variance'] = self.create_vector(variances[i])

            if gconsts is not None:
                mixture['pdf']['gconst'] = gconsts[i]
            if weights is not None:
                mixture['weight'] = weights[i]

            mixtures.append(mixture)

        stream = self.create_default()
        stream['mixtures'] = mixtures
        gmm['streams'] = [stream]

        return gmm

    # ----------------------------------

    def __repr__(self):
        return json.dumps(self.model,indent=2)

# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------

def _to_ordered_dict(ast):
    result = collections.OrderedDict()
    for k, v in ast.items():
        result[k] = v

    return result


class HtkModelSemantics(object):
    """
    @authors: Ricard Marxer.
    @license: GPL, v2
    @summary: Part of the Inspire package: https://github.com/rikrd/inspire.
    """

    def __init__(self):
        pass

    def matrix(self, ast):
        return [float(v) for v in ast.split(' ')]

    def vector(self, ast):
        return [float(v) for v in ast.split(' ')]

    def short(self, ast):
        return int(ast)

    def float(self, ast):
        return float(ast)

    def transPdef(self, ast):
        d = _to_ordered_dict(ast)
        d['matrix'] = []
        aarray = []
        d['array'].append(None)# for the last serie to be appended!
        for a in d['array']:
            if len(aarray) == ast['dim']:
                d['matrix'].append(aarray)
                aarray = [a]
            else:
                aarray.append(a)
        #numpy solution:
        #d['matrix'] = d['array'].reshape((ast['dim'], ast['dim']))
        d.pop('array')
        return d

    def _default(self, ast):
        if isinstance(ast, collections.Mapping):
            return _to_ordered_dict(ast)

        return ast

    def _unquote(self, txt):
        if txt.startswith('"') and txt.endswith('"'):
            return txt[1:-1]

        return txt

    def string(self, ast):
        return self._unquote(ast)

    def __repr__(self):
        return ''


# ---------------------------------------------------------------------------
# HTK-ASCII Acoustic Model: Set of rules for the parser
# ---------------------------------------------------------------------------

class HtkModelParser(Parser):

    def __init__(self, whitespace=None, nameguard=True, **kwargs):
        super(HtkModelParser, self).__init__(
            whitespace=whitespace,
            nameguard=nameguard,
            **kwargs
        )

    @graken()
    def _model_(self):
        def block0():
            self._macrodef_()
            self.ast.setlist('macros', self.last_node)
        self._closure(block0)

        def block2():
            self._hmmmacro_()
            self.ast.setlist('hmms', self.last_node)
        self._closure(block2)

        self.ast._define(
            [],
            ['macros', 'hmms']
        )

    @graken()
    def _macrodef_(self):
        with self._choice():
            with self._option():
                self._transPmacro_()
                self.ast['transition'] = self.last_node
            with self._option():
                self._stateinfomacro_()
                self.ast['state'] = self.last_node
            with self._option():
                self._optmacro_()
                self.ast['options'] = self.last_node
            with self._option():
                self._varmacro_()
                self.ast['variance'] = self.last_node
            with self._option():
                self._meanmacro_()
                self.ast['mean'] = self.last_node
            with self._option():
                self._durationmacro_()
                self.ast['duration'] = self.last_node
            self._error('no available options')

        self.ast._define(
            ['transition', 'state', 'options', 'variance', 'mean', 'duration'],
            []
        )

    @graken()
    def _hmmmacro_(self):
        with self._optional():
            self._hmmref_()
            self.ast['name'] = self.last_node
        self._hmmdef_()
        self.ast['definition'] = self.last_node

        self.ast._define(
            ['name', 'definition'],
            []
        )

    @graken()
    def _optmacro_(self):
        self._token('~o')
        self._cut()
        self._globalOpts_()
        self.ast['definition'] = self.last_node

        self.ast._define(
            ['definition'],
            []
        )

    @graken()
    def _transPmacro_(self):
        self._transPref_()
        self.ast['name'] = self.last_node
        self._transPdef_()
        self.ast['definition'] = self.last_node

        self.ast._define(
            ['name', 'definition'],
            []
        )

    @graken()
    def _stateinfomacro_(self):
        self._stateinforef_()
        self.ast['name'] = self.last_node
        self._stateinfodef_()
        self.ast['definition'] = self.last_node

        self.ast._define(
            ['name', 'definition'],
            []
        )

    @graken()
    def _varmacro_(self):
        self._varref_()
        self.ast['name'] = self.last_node
        self._vardef_()
        self.ast['definition'] = self.last_node

        self.ast._define(
            ['name', 'definition'],
            []
        )

    @graken()
    def _meanmacro_(self):
        self._meanref_()
        self.ast['name'] = self.last_node
        self._meandef_()
        self.ast['definition'] = self.last_node

        self.ast._define(
            ['name', 'definition'],
            []
        )

    @graken()
    def _durationmacro_(self):
        self._durationref_()
        self.ast['name'] = self.last_node
        self._durationdef_()
        self.ast['definition'] = self.last_node

        self.ast._define(
            ['name', 'definition'],
            []
        )

    @graken()
    def _varref_(self):
        self._token('~v')
        self._cut()
        self._macro_()
        self.ast['@'] = self.last_node

    @graken()
    def _transPref_(self):
        self._token('~t')
        self._cut()
        self._macro_()
        self.ast['@'] = self.last_node

    @graken()
    def _stateinforef_(self):
        self._token('~s')
        self._cut()
        self._macro_()
        self.ast['@'] = self.last_node

    @graken()
    def _hmmref_(self):
        self._token('~h')
        self._cut()
        self._macro_()
        self.ast['@'] = self.last_node

    @graken()
    def _weightsref_(self):
        self._token('~w')
        self._cut()
        self._macro_()
        self.ast['@'] = self.last_node

    @graken()
    def _mixpdfref_(self):
        self._token('~m')
        self._cut()
        self._macro_()
        self.ast['@'] = self.last_node

    @graken()
    def _meanref_(self):
        self._token('~u')
        self._cut()
        self._macro_()
        self.ast['@'] = self.last_node

    @graken()
    def _durationref_(self):
        self._token('~d')
        self._cut()
        self._macro_()
        self.ast['@'] = self.last_node

    @graken()
    def _invref_(self):
        self._token('~i')
        self._cut()
        self._macro_()
        self.ast['@'] = self.last_node

    @graken()
    def _xformref_(self):
        self._token('~x')
        self._cut()
        self._macro_()
        self.ast['@'] = self.last_node

    @graken()
    def _inputXformref_(self):
        self._token('~j')
        self._cut()
        self._macro_()
        self.ast['@'] = self.last_node

    @graken()
    def _macro_(self):
        self._string_()

    @graken()
    def _hmmdef_(self):
        self._token('<BeginHMM>')
        self._cut()
        with self._optional():
            self._globalOpts_()
            self.ast['options'] = self.last_node
        self._token('<NumStates>')
        self._cut()
        self._short_()
        self.ast['state_count'] = self.last_node

        def block2():
            self._state_()
            self.ast.setlist('states', self.last_node)
        self._positive_closure(block2)

        with self._optional():
            self._regTree_()
            self.ast['regression_tree'] = self.last_node
        self._transP_()
        self.ast['transition'] = self.last_node
        with self._optional():
            self._duration_()
            self.ast['duration'] = self.last_node
        self._token('<EndHMM>')

        self.ast._define(
            ['options', 'state_count', 'regression_tree', 'transition', 'duration'],
            ['states']
        )

    @graken()
    def _globalOpts_(self):

        def block1():
            self._option_()
        self._positive_closure(block1)

        self.ast['@'] = self.last_node

    @graken()
    def _option_(self):
        with self._choice():
            with self._option():
                self._token('<HmmSetId>')
                self._cut()
                self._string_()
                self.ast['hmm_set_id'] = self.last_node
            with self._option():
                self._token('<StreamInfo>')
                self._cut()
                self._streaminfo_()
                self.ast['stream_info'] = self.last_node
            with self._option():
                self._token('<VecSize>')
                self._cut()
                self._short_()
                self.ast['vector_size'] = self.last_node
            with self._option():
                self._token('<InputXform>')
                self._cut()
                self._inputXform_()
                self.ast['input_transform'] = self.last_node
            with self._option():
                self._covkind_()
                self.ast['covariance_kind'] = self.last_node
            with self._option():
                self._durkind_()
                self.ast['duration_kind'] = self.last_node
            with self._option():
                self._parmkind_()
                self.ast['parameter_kind'] = self.last_node
            self._error('no available options')

        self.ast._define(
            ['hmm_set_id', 'stream_info', 'vector_size', 'input_transform', 'covariance_kind', 'duration_kind', 'parameter_kind'],
            []
        )

    @graken()
    def _streaminfo_(self):
        self._short_()
        self.ast['count'] = self.last_node

        def block2():
            self._short_()
        self._closure(block2)
        self.ast['sizes'] = self.last_node

        self.ast._define(
            ['count', 'sizes'],
            []
        )

    @graken()
    def _covkind_(self):
        self._token('<')
        with self._group():
            with self._choice():
                with self._option():
                    self._token('diagc')
                with self._option():
                    self._token('invdiagc')
                with self._option():
                    self._token('fullc')
                with self._option():
                    self._token('lltc')
                with self._option():
                    self._token('xformc')
                self._error('expecting one of: diagc fullc invdiagc lltc xformc')
        self.ast['@'] = self.last_node
        self._token('>')

    @graken()
    def _durkind_(self):
        self._token('<')
        with self._group():
            with self._choice():
                with self._option():
                    self._token('nulld')
                with self._option():
                    self._token('poissond')
                with self._option():
                    self._token('gammad')
                with self._option():
                    self._token('gen')
                self._error('expecting one of: gammad gen nulld poissond')
        self.ast['@'] = self.last_node
        self._token('>')

    @graken()
    def _parmkind_(self):
        self._token('<')
        self._basekind_()
        self.ast['base'] = self.last_node

        def block2():
            with self._choice():
                with self._option():
                    self._token('_D')
                with self._option():
                    self._token('_A')
                with self._option():
                    self._token('_T')
                with self._option():
                    self._token('_E')
                with self._option():
                    self._token('_N')
                with self._option():
                    self._token('_Z')
                with self._option():
                    self._token('_O')
                with self._option():
                    self._token('_0')
                with self._option():
                    self._token('_V')
                with self._option():
                    self._token('_C')
                with self._option():
                    self._token('_K')
                self._error('expecting one of: _A _C _D _E _K _N _O _0 _T _V _Z')
        self._closure(block2)
        self.ast['options'] = self.last_node
        self._token('>')

        self.ast._define(
            ['base', 'options'],
            []
        )

    @graken()
    def _basekind_(self):
        with self._choice():
            with self._option():
                self._token('discrete')
            with self._option():
                self._token('lpc')
            with self._option():
                self._token('lpcepstra')
            with self._option():
                self._token('mfcc')
            with self._option():
                self._token('fbank')
            with self._option():
                self._token('melspec')
            with self._option():
                self._token('lprefc')
            with self._option():
                self._token('lpdelcep')
            with self._option():
                self._token('user')
            self._error('expecting one of: discrete fbank lpc lpcepstra lpdelcep lprefc melspec mfcc user')

    @graken()
    def _state_(self):
        self._token('<State>')
        self._cut()
        self._short_()
        self.ast['index'] = self.last_node
        self._stateinfo_()
        self.ast['state'] = self.last_node

        self.ast._define(
            ['index', 'state'],
            []
        )

    @graken()
    def _stateinfo_(self):
        with self._choice():
            with self._option():
                self._stateinforef_()
                self.ast['@'] = self.last_node
            with self._option():
                self._stateinfodef_()
                self.ast['@'] = self.last_node
            self._error('no available options')

    @graken()
    def _stateinfodef_(self):
        with self._optional():
            self._mixes_()
            self.ast['streams_mixcount'] = self.last_node
        with self._optional():
            self._weights_()
            self.ast['weights'] = self.last_node

        def block2():
            self._stream_()
            self.ast.setlist('streams', self.last_node)
        self._positive_closure(block2)

        with self._optional():
            self._duration_()
            self.ast['duration'] = self.last_node

        self.ast._define(
            ['streams_mixcount', 'weights', 'duration'],
            ['streams']
        )

    @graken()
    def _mixes_(self):
        self._token('<NumMixes>')
        self._cut()

        def block1():
            self._short_()
        self._positive_closure(block1)

        self.ast['@'] = self.last_node

    @graken()
    def _weights_(self):
        with self._choice():
            with self._option():
                self._weightsref_()
                self.ast['@'] = self.last_node
            with self._option():
                self._weightsdef_()
                self.ast['@'] = self.last_node
            self._error('no available options')

    @graken()
    def _weightsdef_(self):
        self._token('<SWeights>')
        self._cut()
        self._short_()
        self.ast['dim'] = self.last_node
        self._vector_()
        self.ast['vector'] = self.last_node

        self.ast._define(
            ['dim', 'vector'],
            []
        )

    @graken()
    def _stream_(self):
        with self._optional():
            self._token('<Stream>')
            self._cut()
            self._short_()
            self.ast['dim'] = self.last_node
        with self._group():
            with self._choice():
                with self._option():

                    def block1():
                        self._mixture_()
                        self.ast.setlist('mixtures', self.last_node)
                    self._positive_closure(block1)
                with self._option():
                    self._tmixpdf_()
                    self.ast['tmixpdf'] = self.last_node
                with self._option():
                    self._discpdf_()
                    self.ast['discpdf'] = self.last_node
                self._error('no available options')

        self.ast._define(
            ['dim', 'tmixpdf', 'discpdf'],
            ['mixtures']
        )

    @graken()
    def _mixture_(self):
        with self._optional():
            self._token('<Mixture>')
            self._cut()
            self._short_()
            self.ast['index'] = self.last_node
            self._float_()
            self.ast['weight'] = self.last_node
        self._mixpdf_()
        self.ast['pdf'] = self.last_node

        self.ast._define(
            ['index', 'weight', 'pdf'],
            []
        )

    @graken()
    def _tmixpdf_(self):
        self._token('<TMix>')
        self._cut()
        self._macro_()
        self._weightList_()

    @graken()
    def _weightList_(self):

        def block0():
            self._repShort_()
        self._positive_closure(block0)

    @graken()
    def _repShort_(self):
        self._short_()
        with self._optional():
            self._token('*')
            self._cut()
            self._char_()

    @graken()
    def _discpdf_(self):
        self._token('<DProb>')
        self._cut()
        self._weightList_()

    @graken()
    def _mixpdf_(self):
        with self._choice():
            with self._option():
                self._mixpdfref_()
                self.ast['@'] = self.last_node
            with self._option():
                self._mixpdfdef_()
                self.ast['@'] = self.last_node
            self._error('no available options')

    @graken()
    def _mixpdfdef_(self):
        with self._optional():
            self._rclass_()
            self.ast['regression_class'] = self.last_node
        self._mean_()
        self.ast['mean'] = self.last_node
        self._cov_()
        self.ast['covariance'] = self.last_node
        with self._optional():
            self._token('<GConst>')
            self._cut()
            self._float_()
            self.ast['gconst'] = self.last_node

        self.ast._define(
            ['regression_class', 'mean', 'covariance', 'gconst'],
            []
        )

    @graken()
    def _rclass_(self):
        self._token('<RClass>')
        self._cut()
        self._short_()
        self.ast['@'] = self.last_node

    @graken()
    def _mean_(self):
        with self._choice():
            with self._option():
                self._meanref_()
                self.ast['@'] = self.last_node
            with self._option():
                self._meandef_()
                self.ast['@'] = self.last_node
            self._error('no available options')

    @graken()
    def _meandef_(self):
        self._token('<Mean>')
        self._cut()
        self._short_()
        self.ast['dim'] = self.last_node
        self._vector_()
        self.ast['vector'] = self.last_node

        self.ast._define(
            ['dim', 'vector'],
            []
        )

    @graken()
    def _cov_(self):
        with self._choice():
            with self._option():
                self._var_()
                self.ast['variance'] = self.last_node
            with self._option():
                self._inv_()
            with self._option():
                self._xform_()
            self._error('no available options')

        self.ast._define(
            ['variance'],
            []
        )

    @graken()
    def _var_(self):
        with self._choice():
            with self._option():
                self._varref_()
                self.ast['@'] = self.last_node
            with self._option():
                self._vardef_()
                self.ast['@'] = self.last_node
            self._error('no available options')

    @graken()
    def _vardef_(self):
        self._token('<Variance>')
        self._cut()
        self._short_()
        self.ast['dim'] = self.last_node
        self._vector_()
        self.ast['vector'] = self.last_node

        self.ast._define(
            ['dim', 'vector'],
            []
        )

    @graken()
    def _inv_(self):
        with self._choice():
            with self._option():
                self._invref_()
                self.ast['@'] = self.last_node
            with self._option():
                self._invdef_()
                self.ast['@'] = self.last_node
            self._error('no available options')

    @graken()
    def _invdef_(self):
        with self._group():
            with self._choice():
                with self._option():
                    self._token('<InvCovar>')
                with self._option():
                    self._token('<LLTCovar>')
                self._error('expecting one of: <InvCovar> <LLTCovar>')
        self.ast['type'] = self.last_node
        self._cut()
        self._short_()
        self.ast['dim'] = self.last_node
        self._tmatrix_()
        self.ast['matrix'] = self.last_node

        self.ast._define(
            ['type', 'dim', 'matrix'],
            []
        )

    @graken()
    def _xform_(self):
        with self._choice():
            with self._option():
                self._xformref_()
                self.ast['@'] = self.last_node
            with self._option():
                self._xformdef_()
                self.ast['@'] = self.last_node
            self._error('no available options')

    @graken()
    def _xformdef_(self):
        self._token('<Xform>')
        self._cut()
        self._short_()
        self.ast['dim1'] = self.last_node
        self._short_()
        self.ast['dim2'] = self.last_node
        self._matrix_()
        self.ast['matrix'] = self.last_node

        self.ast._define(
            ['dim1', 'dim2', 'matrix'],
            []
        )

    @graken()
    def _tmatrix_(self):
        self._matrix_()

    @graken()
    def _duration_(self):
        with self._choice():
            with self._option():
                self._durationref_()
                self.ast['@'] = self.last_node
            with self._option():
                self._durationdef_()
                self.ast['@'] = self.last_node
            self._error('no available options')

    @graken()
    def _durationdef_(self):
        self._token('<Duration>')
        self._cut()
        self._short_()
        self.ast['dim'] = self.last_node
        self._vector_()
        self.ast['vector'] = self.last_node

        self.ast._define(
            ['dim', 'vector'],
            []
        )

    @graken()
    def _regTree_(self):
        self._token('~r')
        self._cut()
        self._macro_()
        self.ast['@'] = self.last_node
        self._tree_()
        self.ast['tree'] = self.last_node

        self.ast._define(
            ['tree'],
            []
        )

    @graken()
    def _tree_(self):
        self._token('<RegTree>')
        self._cut()
        self._short_()
        self._nodes_()

    @graken()
    def _nodes_(self):
        with self._group():
            with self._choice():
                with self._option():
                    self._token('<Node>')
                    self._cut()
                    self._short_()
                    self._short_()
                    self._short_()
                with self._option():
                    self._token('<TNode>')
                    self._cut()
                    self._short_()
                    self._int_()
                self._error('no available options')
        with self._optional():
            self._nodes_()

    @graken()
    def _transP_(self):
        with self._choice():
            with self._option():
                self._transPref_()
                self.ast['@'] = self.last_node
            with self._option():
                self._transPdef_()
                self.ast['@'] = self.last_node
            self._error('no available options')

    @graken()
    def _transPdef_(self):
        self._token('<TransP>')
        self._cut()
        self._short_()
        self.ast['dim'] = self.last_node
        self._matrix_()
        self.ast['array'] = self.last_node

        self.ast._define(
            ['dim', 'array'],
            []
        )

    @graken()
    def _inputXform_(self):
        with self._choice():
            with self._option():
                self._inputXformref_()
                self.ast['@'] = self.last_node
            with self._option():
                self._inhead_()
                self._inmatrix_()
            self._error('no available options')

    @graken()
    def _inhead_(self):
        self._token('<MMFIdMask>')
        self._cut()
        self._string_()
        self._parmkind_()
        with self._optional():
            self._token('<PreQual>')

    @graken()
    def _inmatrix_(self):
        self._token('<LinXform>')
        self._token('<VecSize>')
        self._cut()
        self._short_()
        self._token('<BlockInfo>')
        self._cut()
        self._short_()

        def block0():
            self._short_()
        self._positive_closure(block0)


        def block1():
            self._block_()
        self._positive_closure(block1)

    @graken()
    def _block_(self):
        self._token('<Block>')
        self._cut()
        self._short_()
        self._xform_()

    @graken()
    def _string_(self):
        self._pattern(r'.*')

    @graken()
    def _vector_(self):
        self._pattern(r'[\d.\-\+eE \n]+')

    @graken()
    def _matrix_(self):
        self._pattern(r'[\d.\-\+eE \n]+')

    @graken()
    def _short_(self):
        self._pattern(r'\d+')

    @graken()
    def _float_(self):
        self._pattern(r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?')

    @graken()
    def _char_(self):
        self._pattern(r'.')

    @graken()
    def _int_(self):
        self._pattern(r'[-+]?(0[xX][\dA-Fa-f]+|0[0-7]*|\d+)')

# ---------------------------------------------------------------------------
