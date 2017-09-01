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

    src.models.acm.modelmixer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import copy

from .acmodel import sppasAcModel

# ----------------------------------------------------------------------------


class sppasModelMixer(object):
    """
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      brigitte.bigi@gmail.com
    :summary:      Mix two acoustic models.

    Create a mixed monophones model.
    Typical use is to create an acoustic model of a non-native speaker.

    """
    def __init__(self):
        """ Create a sppasModelMixer instance. """
        
        self.model1 = None
        self.model2 = None
        self.model_mix = None

    # ------------------------------------------------------------------------

    def load(self, model_text_dir, model_spk_dir):
        """ Load the acoustic models from their directories.

        :param model_text_dir: (str)
        :param model_spk_dir: (str)

        """
        model_text = sppasAcModel()
        model_spk = sppasAcModel()
        self.model_mix = None

        # Load the acoustic models.
        model_text.load(model_text_dir)
        model_spk.load(model_spk_dir)

        self.set_models(model_text, model_spk)

    # ------------------------------------------------------------------------

    def set_models(self, model_text, model_spk):
        """ Fix the acoustic models.

        :param model_text: (sppasAcModel)
        :param model_spk: (sppasAcModel)

        """
        # Check the MFCC parameter kind:
        # we can only interpolate identical models.
        if model_text.get_mfcc_parameter_kind() != model_spk.get_mfcc_parameter_kind():
            raise TypeError('Can only mix models of identical MFCC parameter kind.')

        # Extract the monophones of both models.
        self.model1 = model_text.extract_monophones()
        self.model2 = model_spk.extract_monophones()

        # Map the phonemes names.
        # Why? Because the same phoneme can have a different name
        # in each model. Fortunately, we have the mapping table!
        self.model1.replace_phones(reverse=False)
        self.model2.replace_phones(reverse=False)

    # ------------------------------------------------------------------------

    def mix(self, outputdir, gamma=1.):
        """ Mix the acoustic model of the text with the one of the mother language
        of the speaker reading such text.

        All new phones are added and the shared ones are combined using a
        Static Linear Interpolation.

        :param outputdir: (str) The directory to save the new mixed model.
        :param gamma: (float) coefficient to apply to the model: between 0.
        and 1. This means that a coefficient value of 1. indicates to keep
        the current version of each shared hmm.

        :raises: TypeError, ValueError
        :returns: a tuple indicating the number of hmms that was
        (appended, interpolated, kept, changed).

        """
        if self.model1 is None or self.model2 is None:
            raise TypeError('No model to mix.')

        self.model_mix = copy.deepcopy(self.model1)

        # Manage both mapping table to provide conflicts.
        # Because a key in modelText can be a value in modelSpk
        # i.e. in modelText, a WRONG symbol is used!
        for k in self.model_mix.repllist:
            v = self.model_mix.repllist.get(k)

            for key in self.model2.repllist:
                value = self.model2.repllist.get(key)

                if k == value and v != key:
                    new_key = key
                    if self.model2.repllist.is_value(v):
                        for key2 in self.model2.repllist:
                            value2 = self.model2.repllist.get(key2)
                            if v == value2:
                                new_key = key2
                                while self.model_mix.repllist.is_key(new_key) is True:
                                    new_key = new_key + key2
                    else:
                        new_key = k
                        while self.model_mix.repllist.is_key(new_key) is True:
                            new_key = new_key + k

                    self.model_mix.repllist.remove(k)
                    self.model_mix.repllist.add(new_key, v)

        (appended, interpolated, kept, changed) = self.model_mix.merge_model(self.model2, gamma)
        self.model_mix.replace_phones(reverse=True)

        self.model_mix.save(outputdir)
        return appended, interpolated, kept, changed
