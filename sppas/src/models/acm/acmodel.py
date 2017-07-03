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

    src.models.acm.acmodel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections
import json
import copy
import glob
import os.path

from sppas.src.resources.mapping import sppasMapping

from .acmodelhtkio import sppasHtkIO
from .hmm import sppasHMM
from .tiedlist import sppasTiedList

# ---------------------------------------------------------------------------


class sppasAcModel(object):
    """
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      brigitte.bigi@gmail.com
    :summary:      Acoustic model representation.

    An acoustic model is made of:
       - 'macros' is an OrderedDict of options, transitions, states, ...
       - 'hmms' models (one per phone/biphone/triphone): list of HMM instances
       - a tiedlist (if any)
       - a mapping table to replace phone names.

    """
    def __init__(self):
        """ Create an sppasAcModel instance. """

        self.macros = None
        self.hmms = []
        self.tiedlist = sppasTiedList()
        self.repllist = sppasMapping()

    # -----------------------------------------------------------------------
    # Files
    # -----------------------------------------------------------------------

    def load(self, directory):
        """ Load all known data from a directory.
        
        The default file names are:
            - hmmdefs for an HTK-ASCII acoustic model
            - tiedlist
            - monophones.repl

        :param directory: (str) Folder name of the acoustic model
        :returns: list of loaded file names

        """
        l = []
        hmmdefsfiles = glob.glob(os.path.join(directory, 'hmmdefs'))
        if len(hmmdefsfiles) == 0:
            raise IOError('Missing hmmdefs file in %s' % directory)
        self.load_htk(hmmdefsfiles[0])
        l.append(hmmdefsfiles[0])

        tiedlistfiles = glob.glob(os.path.join(directory, 'tiedlist'))
        if len(tiedlistfiles) == 1:
            self.load_tiedlist(tiedlistfiles[0])
            l.append(tiedlistfiles[0])

        replfiles = glob.glob(os.path.join(directory, 'monophones.repl'))
        if len(replfiles) == 1:
            self.load_phonesrepl(replfiles[0])
            l.append(replfiles[0])

        return l

    # -----------------------------------------------------------------------

    def save(self, directory):
        """ Save all data into a directory.

        The default file names are:
            - hmmdefs for an HTK-ASCII acoustic model
            - tiedlist
            - monophones.repl

        :param directory: (str)
        :returns: list of saved file names

        """
        if os.path.isdir(directory) is False:
            os.mkdir(directory)

        l = list()
        self.save_htk(os.path.join(directory, 'hmmdefs'))
        l.append(os.path.join(directory, 'hmmdefs'))

        if self.tiedlist.is_empty() is False:
            self.save_tiedlist(os.path.join(directory, 'tiedlist'))
            l.append(os.path.join(directory, 'tiedlist'))

        if self.repllist.is_empty() is False:
            self.save_phonesrepl(os.path.join(directory, 'monophones.repl'))
            l.append(os.path.join(directory, 'monophones.repl'))

        return l

    # -----------------------------------------------------------------------

    def load_phonesrepl(self, filename):
        """ Load a replacement table of phone names from a file.

        :param filename: (str)

        """
        try:
            self.repllist.load_from_ascii(filename)
            # Some HACK...
            # because '+' and '-' are the biphones/triphones delimiters,
            # they can't be used as phone name.
            self.repllist.remove('+')
            self.repllist.remove('-')
        except Exception:
            pass

    # -----------------------------------------------------------------------

    def save_phonesrepl(self, filename):
        """ Save a replacement table of phone names into a file.

        :param filename: (str)

        """
        try:
            self.repllist.save_as_ascii(filename)
        except Exception:
            pass

    # -----------------------------------------------------------------------

    def load_tiedlist(self, filename):
        """ Load a tiedlist from a file.

        :param filename: (str)

        """
        try:
            self.tiedlist.load(filename)
        except Exception:
            pass

    # -----------------------------------------------------------------------

    def save_tiedlist(self, filename):
        """ Save a tiedlist into a file.

        :param filename: (str)

        """
        try:
            self.tiedlist.save(filename)
        except Exception:
            pass

    # -----------------------------------------------------------------------

    def load_htk(self, *args):
        """ Load an HTK model from one or more files.

        :param args: Filenames of the model (e.g. macros and/or hmmdefs)

        """
        htk_model = sppasHtkIO(*args)
        self.macros = htk_model.get_macros()
        self.hmms = htk_model.get_hmms()

    # -----------------------------------------------------------------------

    def save_htk(self, filename):
        """ Save the model into a file, in HTK-ASCII standard format.

        :param filename: File where to save the model.

        """
        htk_model = sppasHtkIO()
        htk_model.set(self.macros, self.hmms)
        htk_model.save(filename)

    # -----------------------------------------------------------------------
    # HMM
    # -----------------------------------------------------------------------

    def get_hmm(self, phone):
        """ Return the hmm corresponding to the given phoneme.

        :param phone: (str) the phoneme name to get hmm
        :raises: ValueError if phoneme is not in the model

        """
        hmms = [h for h in self.hmms if h.name == phone]
        if len(hmms) == 1:
            return hmms[0]
        raise ValueError('%s not in the model' % phone)

    # -----------------------------------------------------------------------

    def append_hmm(self, hmm):
        """ Append an HMM to the model.

        :param hmm: (OrderedDict)
        :raises: TypeError, ValueError

        """
        if isinstance(hmm, sppasHMM) is False:
            raise TypeError('Expected an HMM instance. Got %s' % type(hmm))

        if hmm.name is None:
            raise TypeError('Expected an hmm with a name as key.')
        for h in self.hmms:
            if h.name == hmm.name:
                raise ValueError('Duplicate HMM is forbidden. %s already in the model.' % hmm.name)

        if hmm.definition is None:
            raise TypeError('Expected an hmm with a definition as key.')
        if hmm.definition.get('states', None) is None or hmm.definition.get('transition', None) is None:
            raise TypeError('Expected an hmm with a definition including states and transitions.')

        self.hmms.append(hmm)

    # -----------------------------------------------------------------------

    def pop_hmm(self, phone):
        """ Remove an HMM of the model.

        :param phone: (str) the phoneme name to get hmm
        :raises: ValueError if phoneme is not in the model

        """
        hmm = self.get_hmm(phone)
        idx = self.hmms.index(hmm)
        self.hmms.pop(idx)

    # -----------------------------------------------------------------------
    # Manage the model
    # -----------------------------------------------------------------------

    def replace_phones(self, reverse=False):
        """ Replace the phones by using a mapping table.

        This is mainly useful due to restrictions in some acoustic model toolkits:
        X-SAMPA can't be fully used and a "mapping" is required.
        As for example, the /2/ or /9/ can't be represented directly in an
        HTK-ASCII acoustic model. We commonly replace respectively by /eu/ and
        /oe/.

        Notice that '+' and '-' can't be used as a phone name.

        :param reverse: (bool) reverse the replacement direction.

        """
        if self.repllist.is_empty() is True:
            return
        delimiters = ["-", "+"]

        oldreverse = self.repllist.get_reverse()
        self.repllist.set_reverse(reverse)

        # Replace in the tiedlist
        newtied = sppasTiedList()

        for observed in self.tiedlist.observed:
            mapped = self.repllist.map(observed,delimiters)
            newtied.add_observed(mapped)
        for tied,observed in self.tiedlist.tied.items():
            mappedtied = self.repllist.map(tied, delimiters)
            mappedobserved = self.repllist.map(observed, delimiters)
            newtied.add_tied(mappedtied, mappedobserved)
        self.tiedlist = newtied

        # Replace in HMMs
        for hmm in self.hmms:
            hmm.set_name(self.repllist.map(hmm.name, delimiters))

            states = hmm.definition['states']
            if all(isinstance(state['state'], (collections.OrderedDict, collections.defaultdict)) for state in states) is False:
                for state in states:
                    if isinstance(state['state'], (collections.OrderedDict, collections.defaultdict)) is False:
                        tab = state['state'].split('_')
                        tab[1] = self.repllist.map_entry(tab[1])
                        state['state'] = "_".join(tab)

            transition = hmm.definition['transition']
            if isinstance(transition, (collections.OrderedDict, collections.defaultdict)) is False:
                tab = transition.split('_')
                tab[1] = self.repllist.map_entry(tab[1])
                transition = "_".join(tab)

        self.repllist.set_reverse(oldreverse)

    # -----------------------------------------------------------------------

    def fill_hmms(self):
        """ Fill HMM states and transitions, i.e.:

           - replace all the "ST_..." by the corresponding macro, for states.
           - replace all the "T_..." by the corresponding macro, for transitions.

        """
        for hmm in self.hmms:

            states = hmm.definition['states']
            transition = hmm.definition['transition']

            if all(isinstance(state['state'],(collections.OrderedDict, collections.defaultdict)) for state in states) is False:
                newstates = self._fill_states(states)
                if all(s is not None for s in newstates):
                    hmm.definition['states'] = newstates
                else:
                    raise ValueError('No corresponding macro for states: %s'%states)

            if isinstance(transition, (collections.OrderedDict, collections.defaultdict)) is False:
                newtrs = self._fill_transition(transition)
                if newtrs is not None:
                    hmm.definition['transition'] = newtrs
                else:
                    raise ValueError('No corresponding macro for transition: %s' % transition)

        # No more need of states and transitions in macros
        newmacros = list()
        if self.macros is not None:
            for m in self.macros:
                if m.get('transition', None) is None and m.get('state', None) is None:
                    newmacros.append(m)
        self.macros = newmacros

    # -----------------------------------------------------------------------

    def create_model(self, macros, hmms):
        """ Create an empty sppasAcModel and return it.

        :param macros: OrderedDict of options, transitions, states, ...
        :param hmms: models (one per phone/biphone/triphone) is a list of HMM instances

        """
        model = sppasAcModel()
        model.macros = macros
        model.hmms = hmms
        return model

    # -----------------------------------------------------------------------

    def extract_monophones(self):
        """ Return an Acoustic Model that includes only monophones:
            - hmms and macros are selected,
            - repllist is copied,
            - tiedlist is ignored.

        :returns: sppasAcModel

        """
        ac = sppasAcModel()

        # The macros
        if self.macros is not None:
            ac.macros = copy.deepcopy(self.macros)

        # The HMMs
        for h in self.hmms:
            if "+" not in h.name and "-" not in h.name:
                ac.append_hmm(copy.deepcopy(h))
        ac.fill_hmms()

        # The repl mapping table
        ac.repllist = copy.deepcopy(self.repllist)

        return ac

    # -----------------------------------------------------------------------

    def get_mfcc_parameter_kind(self):
        """ Return the MFCC parameter kind, as a string, or an empty string. """

        if self.macros is None:
            return ""

        for m in self.macros:
            option = m.get('options',None)
            if option is not None:
                definition = option.get('definition',None)
                if definition is not None:
                    for defn in definition:
                        parameter_kind = defn.get('parameter_kind', None)
                        if parameter_kind is not None:
                            # Check if of MFCC type...
                            if parameter_kind['base'].lower() == "mfcc":
                                return "mfcc_" + "".join(parameter_kind['options'])

        return ""

    # -----------------------------------------------------------------------

    def compare_mfcc(self, other):
        """ Compare MFCC parameter kind with another one.

        :param other: (sppasAcModel)
        :returns: bool

        """
        my_param = self.get_mfcc_parameter_kind().lower()
        other_param = other.get_mfcc_parameter_kind().lower()

        my_params = sorted(my_param.split('_'))
        other_params = sorted(other_param.split('_'))
        return my_params == other_params

    # -----------------------------------------------------------------------

    def merge_model(self, other, gamma=1.):
        """ Merge another model with self.

        All new phones/biphones/triphones are added and the shared ones are
        combined using a static linear interpolation.

        :param other: (sppasAcModel) the sppasAcModel to be merged with.
        :param gamma: (float) coefficient to apply to the model: between 0.
        and 1. This means that a coefficient value of 1. indicates to keep
        the current version of each shared hmm.

        :raises: TypeError, ValueError
        :returns: a tuple indicating the number of hmms that was
        appended, interpolated, keeped, changed.

        """
        # Check the given input data
        if gamma < 0. or gamma > 1.:
            raise ValueError('Gamma coefficient must be between 0. and 1. Got %f' % gamma)
        if isinstance(other, sppasAcModel) is False:
            raise TypeError('Expected an sppasAcModel instance.')

        # Check the MFCC parameter kind:
        # we can only interpolate identical models.
        if self.compare_mfcc(other) is False:
            raise TypeError('Can only merge models of identical MFCC parameter kind.')

        # Fill HMM states and transitions, i.e.:
        #   - replace all the "ST_..." by the corresponding macro, for states.
        #   - replace all the "T_..." by the corresponding macro, for transitions.
        self.fill_hmms()
        othercopy = copy.deepcopy(other)
        othercopy.fill_hmms()

        # Merge the list of HMMs
        appended = 0
        interpolated = 0
        keeped = len(self.hmms)
        changed = 0
        for hmm in othercopy.hmms:
            got = False
            for h in self.hmms:
                if h.name == hmm.name:
                    got = True
                    if gamma == 1.0:
                        pass
                    elif gamma == 0.:
                        self.pop_hmm(hmm.name)
                        self.append_hmm(hmm)
                        changed = changed + 1
                        keeped = keeped - 1
                    else:
                        selfhmm = self.get_hmm(hmm.name)
                        res = selfhmm.static_linear_interpolation(hmm, gamma)
                        if res is True:
                            interpolated = interpolated + 1
                            keeped = keeped - 1
                    break
            if got is False:
                self.append_hmm(hmm)
                appended = appended + 1

        # Merge the tiedlists
        self.tiedlist.merge(other.tiedlist)

        for k in other.repllist:
            v = other.repllist.get(k)
            if k not in self.repllist and self.repllist.is_value(v) is False:
                self.repllist.add(k, v)

        return appended, interpolated, keeped, changed

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __str__(self):
        strmacros = json.dumps(self.macros, indent=2)
        strhmms = "\n".join([str(h) for h in self.hmms])
        return "MACROS:" + strmacros + "\nHMMS:" + strhmms

    # ----------------------------------

    def _fill_states(self, states):
        newstates = []
        for state in states:
            if isinstance(state['state'], (collections.OrderedDict,collections.defaultdict)) is True:
                newstates.append(state)
                continue
            news = copy.deepcopy(state)
            news['state'] = self._fill_state(state['state'])
            newstates.append(news)
        return newstates

    # ----------------------------------

    def _fill_state(self, state):
        newstate = None
        if self.macros is not None:
            for macro in self.macros:
                if macro.get('state', None):
                    if macro['state']['name'] == state:
                        newstate = copy.deepcopy(macro['state']['definition'])
        return newstate

    # ----------------------------------

    def _fill_transition(self, transition):
        newtransition = None
        if self.macros is not None:
            for macro in self.macros:
                if macro.get('transition', None):
                    if macro['transition']['name'] == transition:
                        newtransition = copy.deepcopy(macro['transition']['definition'])
        return newtransition

    # ----------------------------------

    def _create_default(self):
        return collections.OrderedDict()

    # ----------------------------------

    def create_parameter_kind(self, base=None, options=[]):
        result = self._create_default()
        result['base'] = base
        result['options'] = options
        return result

    # ----------------------------------

    def create_options(self, vector_size, parameter_kind=None, stream_info=None, duration_kind="nulld", covariance_kind="diagc"):
        macro = self._create_default()
        options = []

        if stream_info:
            option = self._create_default()
            option['stream_info'] = self._create_default()
            option['stream_info']['count'] = len(stream_info)
            option['stream_info']['sizes'] = stream_info
            options.append(option)

        option = self._create_default()
        option['vector_size'] = vector_size
        options.append(option)

        option = self._create_default()
        option['duration_kind'] = duration_kind
        options.append(option)

        if parameter_kind:
            option = self._create_default()
            option['parameter_kind'] = parameter_kind
            options.append(option)

        option = self._create_default()
        option['covariance_kind'] = covariance_kind
        options.append(option)

        macro['options'] = {'definition': options}

        return macro
