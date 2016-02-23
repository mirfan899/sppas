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
from copy import deepcopy

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import collections
import json
import copy

from acmodelhtkio import HtkIO
from hmm import HMM, HMMInterpolation
from utils.type import compare_dictionaries

# ---------------------------------------------------------------------------

class AcModel:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Acoustic model representation.

    A model is made of:
       - 'macros' is an OrderedDict of options, transitions, states, ...
       - 'hmms' models (one per phone/biphone/triphone): list of HMM instances

    """

    def __init__(self):
        """
        Constructor.

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

    def create_model(self, macros, hmms):
        """
        Create an empty AcModel and return it.

        @param macros is an OrderedDict of options, transitions, states, ...
        @param hmms models (one per phone/biphone/triphone) is a list of HMM instances

        """
        model = AcModel()
        model.macros = macros
        model.hmms   = hmms
        return model

    # -----------------------------------------------------------------------

    def check_parameter_kind(self, other):
        """
        Check if other MFCC parameter kind is same as self.

        @param other (AcModel) the AcModel to be compared with.

        """
        return True
        #TODO
#         for macro in other.macros:
#             for m in self.macros:
#                 if macro.get('options',None) and m.get('options',None):
#                     # Check MFCC type.
#                     print
#                     print "------------------------------------------------"
#                     for sd in macro["options"]["definition"]:
#                         if 'parameter_kind' in sd:
#                             print " ----->>>>>>>",sd
#
#                     print "------------------------------------------------"
#                     print m["options"]["definition"][0]
#                     print "------------------------------------------------"
#                     print
#                     oparam = macro["options"]["definition"][0]["parameter_kind"]
#                     sparam = m["options"]["definition"][0]["parameter_kind"]
#
#                     res = compare_dictionaries( oparam,sparam,verbose=True )
#                     if res is False:
#                         raise TypeError('Can only merge models of identical MFCC parameter kind.')

    # -----------------------------------------------------------------------

    def merge_model(self, other, gamma=1.):
        """
        Merge another model with self.
        All new phones/biphones/triphones are added and the shared ones are
        combined using a static linear interpolation.

        @param other (AcModel) the AcModel to be merged with.
        @param gamma (float) coefficient to apply to the model: between 0.
        and 1. This means that a coefficient value of 1. indicates to keep
        the current version of each shared hmm.

        @raise TypeError, ValueError
        @return a tuple indicating the number of hmms that was
        appended, interpolated, keeped, changed.

        """
        # Check the given input data
        if gamma < 0. or gamma > 1.:
            raise ValueError('Gamma coefficient must be between 0. and 1. Got %f'%gamma)
        if isinstance(other, AcModel) is False:
            raise TypeError('Expected an AcModel instance.')

        # Check the MFCC parameter kind:
        # we can only interpolate identical models.
        if self.check_parameter_kind(other) is False:
            raise TypeError('Can only merge models of identical MFCC parameter kind.')

        # Fill HMM states and transitions, i.e.:
        #   - replace all the "ST_..." by the corresponding macro, for states.
        #   - replace all the "T_..." by the corresponding macro, for transitions.
        self.fill_hmms()
        othercopy = copy.deepcopy( other )
        othercopy.fill_hmms()

        # Merge the list of HMMs
        appended     = 0
        interpolated = 0
        keeped       = len(self.hmms)
        changed      = 0
        for hmm in othercopy.hmms:
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
                        selfhmm = self.get_hmm( hmm.name )
                        res = selfhmm.static_linear_interpolation(hmm, gamma)
                        if res is True:
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

    def fill_hmms(self):
        """
        Fill HMM states and transitions, i.e.:
           - replace all the "ST_..." by the corresponding macro, for states.
           - replace all the "T_..." by the corresponding macro, for transitions.
        """
        for hmm in self.hmms:

            states     = hmm.definition['states']
            transition = hmm.definition['transition']

            if all(isinstance(state['state'],collections.OrderedDict) for state in states) is False:
                newstates = self._fill_states( states )
                if all(s is not None for s in newstates):
                    hmm.definition['states'] = newstates
                else:
                    raise ValueError('No corresponding macro for states: %s'%states)

            if isinstance(transition, collections.OrderedDict) is False:
                newtrs = self._fill_transition( transition )
                if newtrs is not None:
                    hmm.definition['transition'] = newtrs
                else:
                    raise ValueError('No corresponding macro for transition: %s'%transition)

        # No more need of states and transitions in macros
        newmacros = []
        for m in self.macros:
            if m.get('transition',None) is None and m.get('state',None) is None:
                newmacros.append( m )
        self.macros = newmacros

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __str__(self):
        strmacros=json.dumps(self.macros,indent=2)
        strhmms="\n".join( [str(h) for h in self.hmms] )
        return "MACROS:"+strmacros+"\nHMMS:"+strhmms

    # ----------------------------------

    def _fill_states(self, states):
        newstates = []
        for state in states:
            if isinstance(state['state'], collections.OrderedDict) is True:
                newstates.append( state )
                continue
            news = copy.deepcopy(state)
            news['state'] = self._fill_state( state['state'] )
            newstates.append( news )
        return newstates

    # ----------------------------------

    def _fill_state(self, state):
        newstate = None
        for macro in self.macros:
            if macro.get('state', None):
                if macro['state']['name'] == state:
                    newstate = copy.deepcopy( macro['state']['definition'] )
        return newstate

    # ----------------------------------

    def _fill_transition(self, transition):
        newtransition = None
        for macro in self.macros:
            if macro.get('transition', None):
                if macro['transition']['name'] == transition:
                    newtransition = copy.deepcopy( macro['transition']['definition'] )
        return newtransition

    # ----------------------------------
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

# ---------------------------------------------------------------------------
