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
# File: hmm.py
# ---------------------------------------------------------------------------

import collections
import json
import copy

import acmodelhtkio

# ---------------------------------------------------------------------------


class BaseModel(object):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Base for a model representation: a name and a definition.

    This BaseModel instance is used by HMM.
    It could also be used to define transitions, etc...

    """
    def __init__(self):
        """
        Constructor.
        """
        self.name = ""
        self.definition = None

    # -----------------------------------------------------------------------

    def set(self, name, definition):
        """
        Set the model.

        @param name (str)
        @param definition (OrderedDict)

        """
        self.set_name( name )
        self.set_definition( definition )

    # -----------------------------------------------------------------------

    def set_name(self, name):
        """
        Set the name of the model.

        @param name (str)

        """
        if isinstance(name, (str,unicode)) is False:
            raise TypeError('Expected a name of type string. Got: %s'%type(name))
        self.name = name

    # -----------------------------------------------------------------------

    def set_definition(self, definition):
        """
        Set the definition of the model.

        @param definition (OrderedDict)

        """
        if isinstance(definition, collections.OrderedDict) is False:
            raise TypeError('Expected a definition of type collections.OrderedDict. Got: %s'%type(definition))
        self.definition = definition

# ---------------------------------------------------------------------------


class HMM( BaseModel ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: HMM representation for one phone.

    Hidden Markov Models (HMMs) provide a simple and effective framework for
    modeling time-varying spectral vector sequences. As a consequence, most
    of speech technology systems are based on HMMs.
    Each base phone is represented by a continuous density HMM, with transition
    probability parameters and output observation distributions.
    One of the most commonly used extensions to standard HMMs is to model the
    state-output distribution as a mixture model, a mixture of Gaussians is a
    highly flexible distribution able to model, for example, asymmetric and
    multi-modal distributed data.

    Each hmm model is made of:
       - a 'name': str or unicode
       - a 'definition': OrderedDict

    An HMM-definition is made of:
        - state_count: int
        - states: list of OrderedDict with "index" and "state" as keys.
        - transition: OrderedDict with "dim" and "matrix" as keys.
        - options
        - regression_tree
        - duration

    """
    def __init__(self):
        """
        Constructor.

        """
        BaseModel.__init__(self)

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

    def create_proto(self, protosize, nbmix=1):
        """
        Create the hmm `proto` and set it.
        The proto is based on a 5-states HMM.

        @param protosize (int) Number of mean and variance values.
        It's commonly either 25 or 39, it depends on the MFCC parameters.
        @param nbmix (int) Number of mixtures (i.e. the number of times means and variances occur)

        """
        self.name = "proto"
        self.definition = self._create_default()

        means     = [0.0]*protosize
        variances = [1.0]*protosize

        # Define states
        self.definition['state_count'] = 5
        self.definition['states'] = []
        for i in range(3):
            hmm_state = self._create_default()
            hmm_state['index'] = i + 2
            hmm_state['state'] = self._create_gmm( [means]*nbmix, [variances]*nbmix )
            self.definition['states'].append(hmm_state)

        # Define transitions
        self.definition['transition'] = self._create_transition()

    # -----------------------------------------------------------------------

    def create_sp(self):
        """
        Create the hmm `sp` and set it.

        The sp is based on a 3-state HMM with string "silst" as state 2, and
        a 3x3 transition matrix as follow:
           0.0 1.0 0.0
           0.0 0.9 0.1
           0.0 0.0 0.0

        """
        self.name = "sp"
        self.definition = self._create_default()

        # Define states
        self.definition['state_count'] = 3
        self.definition['states'] = []
        hmm_state = self._create_default()
        hmm_state['index'] = 2
        hmm_state['state'] = "silst"
        self.definition['states'].append(hmm_state)

        # Define transitions
        self.definition['transition'] = self._create_transition([0.9])

    # -----------------------------------------------------------------------

    def load(self, filename):
        """
        Return the (first) HMM described into the given filename.

        @return filename (str) File to read.

        """
        htkmodel = acmodelhtkio.HtkIO( filename  )
        hmms = htkmodel.hmms
        if len(hmms) < 1:
            raise IOError('HMM not loaded.')

        htkhmm = hmms[0]
        self.name = htkhmm.name
        self.definition = htkhmm.definition

    # -----------------------------------------------------------------------

    def save(self, filename):
        """
        Save the hmm into the given filename.

        @return filename (str) File to write.

        """
        htkio = acmodelhtkio.HtkIO()
        htkio.set_hmms([self])
        result = htkio.serialize_hmms()
        with open(filename, 'w') as f:
            f.write( result )

    # -----------------------------------------------------------------------

    def get_state(self, index):
        """
        Return the state of a given index or None if index is not found.

        @param index (int) State index (commonly between 1 and 5)
        @return collections.OrderedDict or None

        """
        states = self.definition['states']
        for item in states:
            if int(item['index']) == index:
                return item['state']

        return None

    # -----------------------------------------------------------------------

    def get_vecsize(self):
        """
        Return the number of means and variance of each state.

        """
        return  self.definition['states'][0]['state']['streams'][0]['mixtures'][0]['pdf']['mean']['dim']

    # -----------------------------------------------------------------------

    def static_linear_interpolation(self, hmm, gamma):
        """
        Static Linear Interpolation is perhaps one of the most straightforward
        manner to combine models. This is an efficient way for merging the GMMs
        of the component models.

        Gamma coefficient is applied to self and (1-Gamma) to the other hmm.

        @param hmm (HMM) the hmm to be interpolated with.
        @param gamma (float) coefficient to apply to self.
        @return Boolean representing the status of the interpolation.

        """
        lin = HMMInterpolation()

        sstates = self.definition['states']
        ostates = hmm.definition['states']
        intsts  = lin.linear_states([sstates,ostates], [gamma,1.-gamma])
        if intsts is None:
            return False

        stransition = self.definition['transition']
        otransition = hmm.definition['transition']
        inttrs = lin.linear_transitions([stransition,otransition], [gamma,1.-gamma])
        if inttrs is None:
            return False

        self.definition['states']     = intsts
        self.definition['transition'] = inttrs

        return True

    # -----------------------------------------------------------------------

    def _create_default(self):
        return collections.defaultdict(lambda: None)
        #return collections.OrderedDict()

    # ----------------------------------

    def _create_vector(self, vector):
        d = self._create_default()
        d['dim'] = len(vector)
        d['vector'] = vector
        return d

    # ----------------------------------

    def _create_square_matrix(self, mat):
        d = self._create_default()
        d['dim'] = len(mat[0])
        d['matrix'] = mat
        return d

    # ----------------------------------

    def _create_transition(self, state_stay_probabilites=[0.6, 0.6, 0.7]):
        n_states = len(state_stay_probabilites) + 2
        transitions = []
        for i in range(n_states):
            transitions.append([ 0.]*n_states)
        transitions[0][1] = 1.
        for i, p in enumerate(state_stay_probabilites):
            transitions[i+1][i+1] = p
            transitions[i+1][i+2] = 1 - p

        return self._create_square_matrix(transitions)

    # ----------------------------------

    def _create_gmm(self, means, variances, gconsts=None, weights=None):

        mixtures = []

        if len(means[0]) == 1:
            means = means[None, :]
            variances = variances[None, :]

        gmm = self._create_default()

        for i in range( len(means) ):
            mixture = self._create_default()
            mixture['pdf'] = self._create_default()
            mixture['pdf']['mean'] = self._create_vector(means[i])
            mixture['pdf']['covariance'] = self._create_default()
            mixture['pdf']['covariance']['variance'] = self._create_vector(variances[i])

            if gconsts is not None:
                mixture['pdf']['gconst'] = gconsts[i]
            if weights is not None:
                mixture['weight'] = weights[i]
            else:
                mixture['weight'] = 1.0/len(means)
            mixture['index'] = i+1

            mixtures.append( mixture )

        stream = self._create_default()
        stream['mixtures'] = mixtures
        gmm['streams'] = [ stream ]
        gmm['streams_mixcount'] = [ len(means) ]

        return gmm

    # -----------------------------------------------------------------------

    def __repr__(self):
        return "Name:"+self.name+"\n"+json.dumps(self.definition,indent=2)

# ---------------------------------------------------------------------------
# Interpolation of HMMs.
# ---------------------------------------------------------------------------


class HMMInterpolation(object):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: HMM interpolation.

    """
    def __init__(self):
        pass

    # -----------------------------------------------------------------------

    def linear_states(self, states, coefficients):
        """
        Linear interpolation of a set of states.

        @param states (OrderedDict)
        @param coefficients: List of coefficients (must sum to 1.)

        @return state (OrderedDict)

        """
        if all( type(s)==list for s in states ) is False:
            return None
        if len(states) != len(coefficients):
            return None
        if len(states)==0:
            return None
        if len(states)==1:
            return states[0]

        intsts = []
        for i in range(len(states[0])):
            indexstates = [ v[i] for v in states ]
            intsts.append( self._linear_interpolate_states( indexstates,coefficients ) )

        return intsts

    # -----------------------------------------------------------------------

    def linear_transitions(self, transitions, coefficients):
        """
        Linear interpolation of a set of transitions.

        @param transitions (OrderedDict): with key='dim' and key='matrix'
        @param coefficients: List of coefficients (must sum to 1.)

        @return transition (OrderedDict)

        """
        if all( type(t)==collections.OrderedDict for t in transitions ) is False:
            return None
        if len(transitions) != len(coefficients):
            return None
        if len(transitions)==0:
            return []
        if len(transitions)==1:
            return transitions[0]

        return self._linear_interpolate_transitions(transitions, coefficients)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _linear_interpolate_values(self, values, gammas):
        """
        Interpolate linearly values with gamma coefficients.

        @param values: List of values
        @param gammas: List of coefficients (must sum to 1.)
        """
        intval = [ v*g for (v,g) in zip(values,gammas) ]
        return sum( intval )


    def _linear_interpolate_vectors(self, vectors, gammas):
        """
        Interpolate linearly vectors with gamma coefficients.

        @param values: List of vectors
        @param gammas: List of coefficients (must sum to 1.)
        """
        intvec = []
        for i in range(len(vectors[0])):
            values = [ v[i] for v in vectors ]
            intvec.append( self._linear_interpolate_values(values, gammas) )
        return intvec


    def _linear_interpolate_matrix(self, matrices, gammas):
        """
        Interpolate linearly matrix with gamma coefficients.

        @param values: List of matrix
        @param gammas: List of coefficients (must sum to 1.)
        """
        intmat = []
        for i in range(len(matrices[0])):
            vectors = [ m[i] for m in matrices ]
            intmat.append( self._linear_interpolate_vectors(vectors,gammas) )
        return intmat


    def _linear_interpolate_transitions(self, transitions, gammas):
        """
        Linear interpolation of a set of transitions, of an hmm.

        @param transitions (OrderedDict): with key='dim' and key='matrix'
        @param coefficients: List of coefficients (must sum to 1.)

        @return transition (OrderedDict)

        """
        if all( t['dim']==transitions[0]['dim'] for t in transitions ) is False:
            return None

        transmatrix = [ t['matrix'] for t in transitions ]
        if len(transmatrix) != len(gammas):
            return None

        matrix = self._linear_interpolate_matrix(transmatrix, gammas)

        t = collections.OrderedDict
        t = copy.deepcopy(transitions[0])
        t['matrix']=matrix
        return t


    def _linear_interpolate_states(self, states, gammas):
        """
        Linear interpolation of a set of states, of one index only.

        @param states (OrderedDict)
        @param coefficients: List of coefficients (must sum to 1.)

        @return state (OrderedDict)

        """
        intstate = copy.deepcopy(states[0])

        state = [ s['state'] for s in states ]
        if all( type(item)==collections.OrderedDict for item in state) is False:
            return None
        # Keys of state are: 'streams', 'streams_mixcount', 'weights', 'duration'
        # streams / weights are lists.
        streams = [ s['streams'] for s in state ]
        for i in range(len(streams[0])):
            values = [ v[i] for v in streams ]
            intstate['state']['streams'][i] = self._linear_interpolate_streams(values, gammas)

        weights = [ w['weights'] for w in state ]
        if all( type(item)==collections.OrderedDict for item in weights) is True:
            for i in range(len(weights[0])):
                values = [ v[i] for v in weights ]
                intstate['state']['weights'][i] = self._linear_interpolate_vectors(values, gammas)

        return intstate


    def _linear_interpolate_streams(self, streams, gammas):
        """
        Linear interpolation of a set of streams, of one state only.

        @param streams (OrderedDict)
        @param coefficients: List of coefficients (must sum to 1.)

        @return stream (OrderedDict)

        """
        intmix = copy.deepcopy(streams[0])
        mixtures = [ item['mixtures'] for item in streams ]
        for i in range(len(mixtures[0])):
            values = [ v[i] for v in mixtures ]
            intmix['mixtures'][i] = self._linear_interpolate_mixtures(values, gammas)
        return intmix


    def _linear_interpolate_mixtures(self, mixtures, gammas):
        """
        Linear interpolation of a set of mixtures, of one stream only.

        @param mixtures (OrderedDict)
        @param coefficients: List of coefficients (must sum to 1.)

        @return mixture (OrderedDict)

        """
        pdfs      = [ item['pdf'] for item in mixtures ]
        means     = [ item['mean']['vector'] for item in pdfs ]
        variances = [ item['covariance']['variance']['vector'] for item in pdfs ]
        gconsts   = [ item['gconst'] for item in pdfs ]

        dim = pdfs[0]['mean']['dim']
        if all( item['mean']['dim']==dim for item in pdfs) is False:
            return None
        dim = pdfs[0]['covariance']['variance']['dim']
        if all( item['covariance']['variance']['dim']==dim for item in pdfs) is False:
            return None

        # interpolate weights
        intwgt = None
        w = []
        for m in mixtures:
            if m['weight'] is not None:
                w.append(m['weight'])
        if len(w)==len(mixtures[0]):
            intwgt = self._linear_interpolate_values( w,gammas )

        # interpolate means, variance and gconsts
        intmean = self._linear_interpolate_vectors( means,gammas )
        intvari = self._linear_interpolate_vectors( variances,gammas )
        intgcst = self._linear_interpolate_values( gconsts,gammas )

        # Assign to a new state
        if intmean is None or intvari is None or intgcst is None:
            return None

        intmixt = copy.deepcopy(mixtures[0])
        intmixt['weight'] = intwgt
        intmixt['pdf']['mean']['vector'] = intmean
        intmixt['pdf']['covariance']['variance']['vector'] = intvari
        intmixt['pdf']['gconst'] = intgcst

        return intmixt

# ---------------------------------------------------------------------------
