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
# File: src.resources.acm.modelmixer.py
# ----------------------------------------------------------------------------

import copy
from .acmodel import AcModel

# ----------------------------------------------------------------------------


class ModelMixer(object):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Mix two acoustic models.

    Create a mixed monophone model.
    Typical use is to create an acoustic model of a non-native speaker.

    """
    def __init__(self):
        """
        Constructor.

        """
        self.modelText = None
        self.modelSpk = None

    # ------------------------------------------------------------------------

    def load(self, modelTextDir, modelSpkDir):
        """
        Load the acoustic models from their directories.

        @param modelTextDir (str)
        @param modelSpkDir (str)

        """
        modelText = AcModel()
        modelSpk  = AcModel()

        # Load the acoustic models.
        modelText.load(modelTextDir)
        modelSpk.load(modelSpkDir)

        self.set_models(modelText, modelSpk)

    # ------------------------------------------------------------------------

    def set_models(self, modelText, modelSpk):
        """
        Fix the acoustic models.

        @param modelText (AcModel)
        @param modelSpk (AcModel)

        """
        # Check the MFCC parameter kind:
        # we can only interpolate identical models.
        if modelText.get_mfcc_parameter_kind() != modelSpk.get_mfcc_parameter_kind() :
            raise TypeError('Can only mix models of identical MFCC parameter kind.')

        # Extract the monophones of both models.
        self.modelText = modelText.extract_monophones()
        self.modelSpk  = modelSpk.extract_monophones()

        # Map the phonemes names.
        # Why? Because the same phoneme can have a different name
        # in each model. Fortunately, we have the mapping table!
        self.modelText.replace_phones(reverse=False)
        self.modelSpk.replace_phones( reverse=False)

    # ------------------------------------------------------------------------

    def mix(self, outputdir, gamma=1.):
        """
        Mix the acoustic model of the text with the one of the mother language
        of the speaker reading such text.

        All new phones are added and the shared ones are combined using a
        Static Linear Interpolation.

        @param outputdir (str) The directory to save the new mixed model.
        @param gamma (float) coefficient to apply to the model: between 0.
        and 1. This means that a coefficient value of 1. indicates to keep
        the current version of each shared hmm.

        @raise TypeError, ValueError
        @return a tuple indicating the number of hmms that was
        (appended, interpolated, keeped, changed).

        """
        if self.modelText is None or self.modelSpk is None:
            raise TypeError('No model to mix.')

        self.modelmix = copy.deepcopy(self.modelText)

        # Manage both mapping table to provide conflicts.
        # Because a key in modelText can be a value in modelSpk
        # i.e. in modelText, a WRONG symbol is used!
        for k in self.modelmix.repllist:
            v = self.modelmix.repllist.get(k)

            for key in self.modelSpk.repllist:
                value = self.modelSpk.repllist.get(key)

                if k == value and v != key:
                    if self.modelSpk.repllist.is_value(v):
                        for key2 in self.modelSpk.repllist:
                            value2 = self.modelSpk.repllist.get(key2)
                            if v == value2:
                                newkey = key2
                                while self.modelmix.repllist.is_key(newkey) is True:
                                    newkey = newkey+key2
                    else:
                        newkey = k
                        while self.modelmix.repllist.is_key(newkey) is True:
                            newkey = newkey+k

                    self.modelmix.repllist.remove(k)
                    self.modelmix.repllist.add(newkey, v)

        (appended,interpolated,keeped,changed) = self.modelmix.merge_model(self.modelSpk, gamma)
        self.modelmix.replace_phones(reverse=True)

        self.modelmix.save(outputdir)
        return appended, interpolated, keeped, changed
