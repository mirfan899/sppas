"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.models.acm.hmm.py
    ~~~~~~~~~~~~~~~~~~~~~

"""
import collections
import copy
import json

import acmodelhtkio

# ---------------------------------------------------------------------------


class sppasBaseModel(object):
    """
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      brigitte.bigi@gmail.com
    :summary:      Base for a model representation: a name and a definition.

    This sppasBaseModel instance is used by HMM.
    It could also be used to define transitions, etc...
    A model is made of a name (str) and a definition (OrderedDict).

    """
    def __init__(self):
        """ Create a sppasBaseModel instance. """
        
        self.name = ""
        self.definition = sppasBaseModel.create_default()

    # -----------------------------------------------------------------------

    def set(self, name, definition):
        """ Set the model.

        :param name: (str) Name of the HMM
        :param definition: (OrderedDict) Definition of the HMM (states and transitions)

        """
        self.set_name(name)
        self.set_definition(definition)

    # -----------------------------------------------------------------------

    def set_name(self, name):
        """ Set the name of the model.

        :param name: (str) Name of the HMM

        """
        if isinstance(name, (str, unicode)) is False:
            raise TypeError('Expected a name of type string. '
                            'Got: %s' % type(name))
        
        self.name = name

    # -----------------------------------------------------------------------

    def set_definition(self, definition):
        """ Set the definition of the model.

        :param definition: (OrderedDict) Definition of the HMM (states and transitions)

        """
        if isinstance(definition, collections.OrderedDict) is False:
            raise TypeError('Expected a definition of type collections.OrderedDict. '
                            'Got: %s' % type(definition))
        
        self.definition = definition

    # -----------------------------------------------------------------------

    @staticmethod
    def create_default():
        return collections.defaultdict(lambda: None)
        # return collections.OrderedDict()

    # ----------------------------------

    @staticmethod
    def create_vector(vector):
        v = sppasBaseModel.create_default()
        v['dim'] = len(vector)
        v['vector'] = vector
        return v

    # ----------------------------------

    @staticmethod
    def create_square_matrix(matrix):
        m = sppasBaseModel.create_default()
        m['dim'] = len(matrix[0])
        m['matrix'] = matrix
        return m

# ---------------------------------------------------------------------------


class sppasHMM(sppasBaseModel):
    """
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      brigitte.bigi@gmail.com
    :summary:      HMM representation for one phone.

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
        """ Create a HMM instance. """

        sppasBaseModel.__init__(self)

    # -----------------------------------------------------------------------

    def create(self, states, transition, name=None):
        """ Create the hmm and set it.

        :param states: (OrderedDict)
        :param transition: (OrderedDict)
        :param name: (string)

        """
        self.set_name(name)
        self.definition = sppasBaseModel.create_default()

        self.definition['state_count'] = len(states) + 2
        self.definition['states'] = []
        for i, state in enumerate(states):
            hmm_state = sppasBaseModel.create_default()
            hmm_state['index'] = i + 2
            hmm_state['state'] = state
            self.definition['states'].append(hmm_state)

        self.definition['transition'] = transition

    # -----------------------------------------------------------------------

    def create_proto(self, protosize, nbmix=1):
        """ Create the 5-states HMM `proto` and set it.

        :param protosize (int) Number of mean and variance values.
        It's commonly either 25 or 39, it depends on the MFCC parameters.
        :param nbmix: (int) Number of mixtures (i.e. the number of times means and variances occur)

        """
        self.name = "proto"
        self.definition = sppasBaseModel.create_default()

        means = [0.0]*protosize
        variances = [1.0]*protosize

        # Define states
        self.definition['state_count'] = 5
        self.definition['states'] = []
        for i in range(3):
            hmm_state = sppasBaseModel.create_default()
            hmm_state['index'] = i + 2
            hmm_state['state'] = sppasHMM.create_gmm([means]*nbmix, [variances]*nbmix)
            self.definition['states'].append(hmm_state)

        # Define transitions
        self.definition['transition'] = sppasHMM.create_transition()

    # -----------------------------------------------------------------------

    def create_sp(self):
        """ Create the 3-states HMM `sp` and set it.

        The `sp` model is based on a 3-state HMM with string "silst" as state 2,
        and a 3x3 transition matrix as follow:
           0.0 1.0 0.0
           0.0 0.9 0.1
           0.0 0.0 0.0

        """
        self.name = "sp"
        self.definition = sppasBaseModel.create_default()

        # Define states
        self.definition['state_count'] = 3
        self.definition['states'] = []
        hmm_state = sppasBaseModel.create_default()
        hmm_state['index'] = 2
        hmm_state['state'] = "silst"
        self.definition['states'].append(hmm_state)

        # Define transitions
        self.definition['transition'] = sppasHMM.create_transition([0.9])

    # -----------------------------------------------------------------------

    def load(self, filename):
        """ Return the (first) HMM described into the given filename.

        :returns: filename (str) File to read.

        """
        htk_model = acmodelhtkio.sppasHtkIO(filename)
        hmms = htk_model.get_hmms()
        if len(hmms) < 1:
            raise IOError('HMM not loaded.')

        htk_hmm = hmms[0]
        self.name = htk_hmm.name
        self.definition = htk_hmm.definition

    # -----------------------------------------------------------------------

    def save(self, filename):
        """ Save the hmm into the given filename.

        :param filename: (str) File to write.

        """
        htk_io = acmodelhtkio.sppasHtkIO()
        htk_io.set_hmms([self])
        result = htk_io.serialize_hmms()
        with open(filename, 'w') as f:
            f.write(result)

    # -----------------------------------------------------------------------

    def get_state(self, index):
        """ Return the state of a given index or None if index is not found.

        :param index: (int) State index (commonly between 1 and 5)
        :returns: collections.OrderedDict or None

        """
        states = self.definition['states']
        for item in states:
            if int(item['index']) == index:
                return item['state']

        return None

    # -----------------------------------------------------------------------

    def get_vecsize(self):
        """ Return the number of means and variance of each state. """

        return self.definition['states'][0]['state']['streams'][0]['mixtures'][0]['pdf']['mean']['dim']

    # -----------------------------------------------------------------------

    def static_linear_interpolation(self, hmm, gamma):
        """ Static Linear Interpolation is perhaps one of the most straightforward
        manner to combine models. This is an efficient way for merging the GMMs
        of the component models.

        Gamma coefficient is applied to self and (1-Gamma) to the other hmm.

        :param hmm: (HMM) the hmm to be interpolated with.
        :param gamma: (float) coefficient to apply to self.
        :returns: (bool) Status of the interpolation.

        """
        lin = HMMInterpolation()

        sstates = self.definition['states']
        ostates = hmm.definition['states']
        intsts = lin.linear_states([sstates, ostates], [gamma, 1.-gamma])
        if intsts is None:
            return False

        stransition = self.definition['transition']
        otransition = hmm.definition['transition']
        inttrs = lin.linear_transitions([stransition, otransition], [gamma, 1.-gamma])
        if inttrs is None:
            return False

        self.definition['states'] = intsts
        self.definition['transition'] = inttrs

        return True

    # -----------------------------------------------------------------------

    @staticmethod
    def create_transition(state_stay_probabilites=[0.6, 0.6, 0.7]):
        n_states = len(state_stay_probabilites) + 2
        transitions = []
        for i in range(n_states):
            transitions.append([0.]*n_states)
        transitions[0][1] = 1.
        for i, p in enumerate(state_stay_probabilites):
            transitions[i+1][i+1] = p
            transitions[i+1][i+2] = 1 - p

        return sppasBaseModel.create_square_matrix(transitions)

    # ----------------------------------

    @staticmethod
    def create_gmm(means, variances, gconsts=None, weights=None):

        mixtures = []

        if len(means[0]) == 1:
            means = means[None, :]
            variances = variances[None, :]

        gmm = sppasBaseModel.create_default()

        for i in range(len(means)):
            mixture = sppasBaseModel.create_default()
            mixture['pdf'] = sppasBaseModel.create_default()
            mixture['pdf']['mean'] = sppasBaseModel.create_vector(means[i])
            mixture['pdf']['covariance'] = sppasBaseModel.create_default()
            mixture['pdf']['covariance']['variance'] = sppasBaseModel.create_vector(variances[i])

            if gconsts is not None:
                mixture['pdf']['gconst'] = gconsts[i]
            if weights is not None:
                mixture['weight'] = weights[i]
            else:
                mixture['weight'] = 1.0/len(means)
            mixture['index'] = i+1

            mixtures.append(mixture)

        stream = sppasBaseModel.create_default()
        stream['mixtures'] = mixtures
        gmm['streams'] = [stream]
        gmm['streams_mixcount'] = [len(means)]

        return gmm

    # -----------------------------------------------------------------------

    def __repr__(self):
        return "Name:"+self.name+"\n"+json.dumps(self.definition, indent=2)

# ---------------------------------------------------------------------------
# Interpolation of HMMs.
# ---------------------------------------------------------------------------


class HMMInterpolation(object):
    """
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      brigitte.bigi@gmail.com
    :summary:      HMM interpolation.

    """
    def __init__(self):
        pass

    # -----------------------------------------------------------------------

    @staticmethod
    def linear_states(states, coefficients):
        """ Linear interpolation of a set of states.

        :param states: (OrderedDict)
        :param coefficients: List of coefficients (must sum to 1.)

        :returns: state (OrderedDict)

        """
        if all(type(s) == list for s in states) is False:
            return None
        if len(states) != len(coefficients):
            return None
        if len(states) == 0:
            return None
        if len(states) == 1:
            return states[0]

        intsts = []
        for i in range(len(states[0])):
            indexstates = [v[i] for v in states]
            intsts.append(HMMInterpolation.linear_interpolate_states(indexstates, coefficients))

        return intsts

    # -----------------------------------------------------------------------

    @staticmethod
    def linear_transitions(transitions, coefficients):
        """ Linear interpolation of a set of transitions.

        :param transitions: (OrderedDict): with key='dim' and key='matrix'
        :param coefficients: List of coefficients (must sum to 1.)

        :returns: transition (OrderedDict)

        """
        if all(type(t) == collections.OrderedDict for t in transitions) is False:
            return None
        if len(transitions) != len(coefficients):
            return None
        if len(transitions) == 0:
            return []
        if len(transitions) == 1:
            return transitions[0]

        return HMMInterpolation.linear_interpolate_transitions(transitions, coefficients)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def linear_interpolate_values(values, gammas):
        """ Interpolate linearly values with gamma coefficients.

        :param values: List of values
        :param gammas: List of coefficients (must sum to 1.)

        """
        intval = [v*g for (v, g) in zip(values, gammas)]
        return sum(intval)

    # -----------------------------------------------------------------------

    @staticmethod
    def linear_interpolate_vectors(vectors, gammas):
        """ Interpolate linearly vectors with gamma coefficients.

        :param vectors: List of vectors
        :param gammas: List of coefficients (must sum to 1.)

        """
        intvec = []
        for i in range(len(vectors[0])):
            values = [v[i] for v in vectors]
            intvec.append(HMMInterpolation.linear_interpolate_values(values, gammas))
        return intvec

    # -----------------------------------------------------------------------

    @staticmethod
    def linear_interpolate_matrix(matrices, gammas):
        """ Interpolate linearly matrix with gamma coefficients.

        :param matrices: List of matrix
        :param gammas: List of coefficients (must sum to 1.)

        """
        intmat = []
        for i in range(len(matrices[0])):
            vectors = [m[i] for m in matrices]
            intmat.append(HMMInterpolation.linear_interpolate_vectors(vectors, gammas))
        return intmat

    # -----------------------------------------------------------------------

    @staticmethod
    def linear_interpolate_transitions(transitions, gammas):
        """ Linear interpolation of a set of transitions, of an hmm.

        :param transitions: (OrderedDict): with key='dim' and key='matrix'
        :param gammas: List of coefficients (must sum to 1.)

        :returns: transition (OrderedDict)

        """
        if all(t['dim'] == transitions[0]['dim'] for t in transitions) is False:
            return None

        transmatrix = [t['matrix'] for t in transitions]
        if len(transmatrix) != len(gammas):
            return None

        matrix = HMMInterpolation.linear_interpolate_matrix(transmatrix, gammas)

        # t = collections.OrderedDict()
        t = copy.deepcopy(transitions[0])
        t['matrix'] = matrix
        return t

    # -----------------------------------------------------------------------

    @staticmethod
    def linear_interpolate_states(states, gammas):
        """ Linear interpolation of a set of states, of one index only.

        :param states: (OrderedDict)
        :param gammas: List of coefficients (must sum to 1.)

        :returns: state (OrderedDict)

        """
        intstate = copy.deepcopy(states[0])

        state = [s['state'] for s in states]
        if all(type(item) == collections.OrderedDict for item in state) is False:
            return None
        # Keys of state are: 'streams', 'streams_mixcount', 'weights', 'duration'
        # streams / weights are lists.
        streams = [s['streams'] for s in state]
        for i in range(len(streams[0])):
            values = [v[i] for v in streams]
            intstate['state']['streams'][i] = HMMInterpolation.linear_interpolate_streams(values, gammas)

        weights = [w['weights'] for w in state]
        if all(type(item) == collections.OrderedDict for item in weights) is True:
            for i in range(len(weights[0])):
                values = [v[i] for v in weights]
                intstate['state']['weights'][i] = HMMInterpolation.linear_interpolate_vectors(values, gammas)

        return intstate

    # -----------------------------------------------------------------------

    @staticmethod
    def linear_interpolate_streams(streams, gammas):
        """ Linear interpolation of a set of streams, of one state only.

        :param streams: (OrderedDict)
        :param gammas: List of coefficients (must sum to 1.)

        :returns: stream (OrderedDict)

        """
        intmix = copy.deepcopy(streams[0])
        mixtures = [item['mixtures'] for item in streams]
        for i in range(len(mixtures[0])):
            values = [v[i] for v in mixtures]
            intmix['mixtures'][i] = HMMInterpolation.linear_interpolate_mixtures(values, gammas)
        return intmix

    # -----------------------------------------------------------------------

    @staticmethod
    def linear_interpolate_mixtures(mixtures, gammas):
        """ Linear interpolation of a set of mixtures, of one stream only.

        :param mixtures: (OrderedDict)
        :param gammas: List of coefficients (must sum to 1.)

        :returns: mixture (OrderedDict)

        """
        pdfs = [item['pdf'] for item in mixtures]
        means = [item['mean']['vector'] for item in pdfs]
        variances = [item['covariance']['variance']['vector'] for item in pdfs]
        gconsts = [item['gconst'] for item in pdfs]

        dim = pdfs[0]['mean']['dim']
        if all(item['mean']['dim'] == dim for item in pdfs) is False:
            return None
        dim = pdfs[0]['covariance']['variance']['dim']
        if all(item['covariance']['variance']['dim'] == dim for item in pdfs) is False:
            return None

        # interpolate weights
        intwgt = None
        w = []
        for m in mixtures:
            if m['weight'] is not None:
                w.append(m['weight'])
        if len(w) == len(mixtures[0]):
            intwgt = HMMInterpolation.linear_interpolate_values(w, gammas)

        # interpolate means, variance and gconsts
        intmean = HMMInterpolation.linear_interpolate_vectors(means, gammas)
        intvari = HMMInterpolation.linear_interpolate_vectors(variances, gammas)
        intgcst = HMMInterpolation.linear_interpolate_values(gconsts, gammas)

        # Assign to a new state
        if intmean is None or intvari is None or intgcst is None:
            return None

        intmixt = copy.deepcopy(mixtures[0])
        intmixt['weight'] = intwgt
        intmixt['pdf']['mean']['vector'] = intmean
        intmixt['pdf']['covariance']['variance']['vector'] = intvari
        intmixt['pdf']['gconst'] = intgcst

        return intmixt
