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
# File: sppasalign.py
# ----------------------------------------------------------------------------

import shutil
import os.path
import glob
import logging

from sppas import RESOURCES_PATH

import sppas.src.utils.fileutils
import sppas.src.annotationdata.aio
from sppas.src.annotationdata import Transcription
from sppas.src.annotationdata import Tier
from sppas.src.annotationdata import Media
from sppas.src.annotationdata import Text
from sppas.src.annotationdata.aio.utils import gen_id
from sppas.src.resources.mapping import Mapping
from sppas.src.models.acm.modelmixer import ModelMixer

from .. import ERROR_ID, WARNING_ID, OK_ID, INFO_ID
from ..baseannot import sppasBaseAnnotation
from .alignio import AlignIO
from .activity import Activity

# ----------------------------------------------------------------------------


class sppasAlign(sppasBaseAnnotation):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      SPPAS integration of the Alignment automatic annotation.

    This class can produce 1 up to 4 tiers with names:

        - PhonAlign,
        - TokensAlign (if tokens are given in the input).
        - PhnTokAlign - option (if tokens are given in the input),
        - Activity    - option (if tokens are given in the input),

    How to use sppasAlign?

    >>> a = sppasAlign(modeldirname)
    >>> a.run(inputphonesname, inputtokensname, inputaudioname, outputfilename)

    """
    def __init__(self, model, modelL1=None, logfile=None):
        """
        Create a new sppasAlign instance.

        @param model (str) the acoustic model directory name of the language of the text
        @param modelL1 (str) the acoustic model directory name of the mother language of the speaker
        @param logfile (sppasLog)

        """
        sppasBaseAnnotation.__init__(self, logfile)

        # Members: self.alignio
        self.fix_segmenter(model,modelL1)
        self.reset()

    # ------------------------------------------------------------------

    def reset(self):
        """
        Set default values.

        """
        # List of options to configure this automatic annotation
        self._options = {}
        self._options['clean']    = True  # Remove temporary files
        self._options['infersp']  = False # Add 'sp' at the end of each token
        self._options['basic']    = False # Perform a basic alignment if error
        self._options['activity'] = True
        self._options['activityduration'] = False
        self._options['phntok']   = False

    # -----------------------------------------------------------------------

    def fix_segmenter(self, model, modelL1):
        """
        Fix the acoustic model directory, then create a SpeechSegmenter and AlignerIO.

        @param model is the acoustic model directory name of the language of the text,
        @param modelL1 is the acoustic model directory name of the mother language of the speaker,

        """
        if modelL1 is not None:
            try:
                modelmixer = ModelMixer()
                modelmixer.load(model,modelL1)
                outputdir = os.path.join(RESOURCES_PATH, "models", "models-mix")
                modelmixer.mix(outputdir, gamma=1.)
                model = outputdir
            except Exception as e:
                self.print_message("The model is ignored: %s"%str(e), indent=3, status=WARNING_ID)

        # Map phoneme names from model-specific to SAMPA and vice-versa
        mappingfilename = os.path.join(model, "monophones.repl")
        if os.path.isfile(mappingfilename):
            try:
                mapping = Mapping(mappingfilename)
            except Exception:
                mapping = Mapping()
        else:
            mapping = Mapping()

        # Manager of the interval tracks
        self.alignio = AlignIO(mapping, model)

    # ------------------------------------------------------------------------
    # Methods to fix options
    # ------------------------------------------------------------------------

    def fix_options(self, options):
        """
        Fix all options.

        @param options (option)

        """
        for opt in options:

            key = opt.get_key()

            if "clean" == key:
                self.set_clean(opt.get_value())

            elif "basic" == key:
                self.set_basic(opt.get_value())

            elif "aligner" == key:
                self.set_aligner(opt.get_value())

            elif "infersp" == key:
                self.set_infersp(opt.get_value())

            elif "activity" == key:
                self.set_activity_tier(opt.get_value())

            elif "activityduration" == key:
                self.set_activityduration_tier(opt.get_value())

            elif "phntok" == key:
                self.set_phntokalign_tier(opt.get_value())

            else:
                raise KeyError('Unknown key option: %s'%key)

    # ----------------------------------------------------------------------

    def set_clean(self, clean):
        """
        Fix the clean option.

        @param clean (bool - IN) If clean is set to True then temporary files
        will be removed.

        """
        self._options['clean'] = clean

    # -----------------------------------------------------------------------

    def set_aligner(self, alignername):
        """
        Fix the name of the aligner.
        The list of accepted aligner names is available in:
        >>> aligners.aligner_names()

        @param alignername (str - IN) Case-insensitive name of the aligner.

        """
        self.alignio.set_aligner(alignername)
        self._options['aligner'] = alignername

    # -----------------------------------------------------------------------

    def set_infersp(self, infersp):
        """
        Fix the infersp option.

        @param infersp (bool - IN) If infersp is set to True, the aligner
        will add an optional short pause at the end of each token, and the
        will infer if it is relevant.

        """
        self.alignio.set_infersp(infersp)

    # -----------------------------------------------------------------------

    def set_basic(self, basic):
        """
        Fix the basic option.

        @param basic (bool - IN) If basic is set to True, a basic segmentation
        will be performer if the main aligner fails.

        """
        self._options['basic'] = basic

    # -----------------------------------------------------------------------

    def set_activity_tier(self, value):
        """
        Fix the activity option.

        @param value (bool - IN) Activity tier generation.

        """
        self._options['activity'] = bool(value)

    # -----------------------------------------------------------------------

    def set_activityduration_tier(self, value):
        """
        Fix the activity duration option.

        @param value (bool - IN) Activity tier generation.

        """
        self._options['activityduration'] = bool(value)

    # -----------------------------------------------------------------------

    def set_phntokalign_tier(self, value):
        """
        Fix the phntok option.

        @param value (bool - IN) PhnTokAlign tier generation.

        """
        self._options['phntok'] = bool(value)

    # -----------------------------------------------------------------------
    # Methods to time-align series of data
    # -----------------------------------------------------------------------

    def convert_tracks(self, diralign, trstier):
        """
        Call the Aligner to align each unit of a directory.

        @param diralign is the directory to get units and put alignments.
        @param trstier (Tier) required only if basic alignment.

        """
        # Verify if the directory exists
        if not os.path.exists(diralign):
            raise IOError('The directory '+diralign+' does not exist.')

        # Get all audio tracks
        dirlist = glob.glob(os.path.join(diralign, "track_*.wav"))
        ntracks = len(dirlist)
        if ntracks == 0:
            raise IOError('The directory '+diralign+' does not contain data.')

        track = 1
        while track <= ntracks:
            self.print_message('Align interval number '+str(track), indent=3)

            try:
                msg = self.alignio.segment_track(track,diralign)
                if len(msg)>0:
                    self.print_message(msg, indent=3, status=INFO_ID)

            except Exception as e:
                self.print_message(self.alignio.get_aligner()+' failed to perform segmentation.', indent=3, status=ERROR_ID)
                self.print_message(str(e), indent=4, status=INFO_ID)
                #import traceback
                #print(traceback.format_exc())

                # Execute BasicAlign
                if self._options['basic'] is True:
                    if self.logfile:
                        self.logfile.print_message('Execute a Basic Alignment - same duration for each phoneme:', indent=3)
                    alignerid = self.alignio.get_aligner()
                    self.alignio.set_aligner('basic')
                    msg = self.alignio.segment_track(track,diralign)
                    self.alignio.set_aligner(alignerid)
                # or Create an empty alignment, to get an empty interval in the final tier
                else:
                    msg = self.alignio.segment_track(track,diralign,segment=False)

            track = track + 1

    # ------------------------------------------------------------------------

    def convert(self, phontier, toktier, inputaudio, workdir):
        """
        Perform speech segmentation of data in tiers tokenization/phonetization.

        @param phontier (Tier - IN) The phonetization.
        @param toktier (Tier - IN) The tokenization, or None.
        @param audioname (str - IN) Audio file name.

        @return A transcription.

        """
        if os.path.exists(workdir) is False:
            os.mkdir(workdir)

        # Split input into tracks
        # --------------------------------------------------------------

        self.print_message("Split into intervals: ", indent=2)
        sgmt = self.alignio.split(inputaudio, phontier, toktier, workdir)

        # Align each track
        # --------------------------------------------------------------

        self.print_message("Align each interval: ", indent=2)
        self.convert_tracks(workdir, phontier)

        # Merge track alignment results
        # --------------------------------------------------------------

        self.print_message("Merge interval's alignment:", indent=2)

        trsoutput = Transcription("AutomaticAlignment")
        for tier in sgmt:
            trsoutput.Append(tier)

        # Create a Transcription() object with alignments
        trs = self.alignio.read(workdir)
        if self.alignio.get_aligner() != 'basic':
            trs = self.rustine_liaisons(trs)
            trs = self.rustine_others(trs)
        for tier in trs:
            trsoutput.Append(tier)

        return trsoutput

    # ------------------------------------------------------------------------

    def append_extra(self, trs):
        """
        Append extra tiers in trs: Activity and PhnTokAlign.

        """
        tokenalign = trs.Find("TokensAlign")
        if tokenalign is None:
            self.print_message("No time-aligned tokens found. No extra tier can be generated.", indent=2, status=WARNING_ID)
            return trs

        # PhnTokAlign tier
        if self._options['phntok'] is True:
            try:
                phonalign = trs.Find("PhonAlign")
                tier = self.phntokalign_tier(phonalign,tokenalign)
                trs.Append(tier)
                trs.GetHierarchy().add_link("TimeAssociation", tokenalign, tier)
            except Exception as e:
                self.print_message("PhnTokAlign generation: %s"%str(e), indent=2, status=WARNING_ID)

        # Activity tier
        if self._options['activity'] is True or self._options['activityduration']:
            try:
                activity = Activity(trs)
                tier = activity.get_tier()
                if self._options['activity'] is True:
                    trs.Append(tier)
                    trs.GetHierarchy().add_link("TimeAlignment", tokenalign, tier)

                if self._options['activityduration'] is True:
                    dtier = tier.Copy()
                    dtier.SetName("ActivityDuration")
                    trs.Append(dtier)
                    for a in dtier:
                        d = a.GetLocation().GetDuration().GetValue()
                        a.GetLabel().SetValue('%.3f' % d)

            except Exception as e:
                self.print_message("Activities generation: %s"%str(e), indent=2, status=WARNING_ID)

        return trs

    # ------------------------------------------------------------------------

    def get_phonestier(self, trsinput):
        """
        Return the tier with phonetization or None.

        """
        # Search for a tier starting with "phon"
        for tier in trsinput:
            if tier.GetName().lower().startswith("phon") is True:
                return tier

        # Search for a tier containing "phon"
        for tier in trsinput:
            if "phon" in tier.GetName().lower():
                return tier

        return None

    # ------------------------------------------------------------------------

    def get_tokenstier(self, trsinput):
        """
        Return the tier with tokens, or None.

        In case of EOT, 2 tiers with tokens are available: std and faked.
        Priority is given to std.

        """
        toktier   = None # None tier with tokens
        stdtier   = None # index of stdtoken tier
        fakedtier = None # index of fakedtoken tier

        for tier in trsinput:
            tiername = tier.GetName().lower()
            if "std" in tiername and "token" in tiername:
                return stdtier
            elif "faked" in tiername and "token" in tiername:
                fakedtier = tier
            elif "token" in tiername:
                toktier = tier

        if fakedtier is not None:
            return fakedtier

        return toktier

    # ------------------------------------------------------------------------

    def phntokalign_tier(self, tierphon, tiertoken):
        """
        Generates the PhnTokAlignTier from PhonAlign and TokensAlign.

        """
        newtier = Tier('PhnTokAlign')
        newtier.SetMedia(tiertoken.GetMedia())

        for anntoken in tiertoken:

            # Create the sequence of phonemes
            # Use only the phoneme with the best score.
            # Don't generate alternatives, and won't never do it.
            beg = anntoken.GetLocation().GetBegin()
            end = anntoken.GetLocation().GetEnd()
            annphons = tierphon.Find(beg,end)
            l = "-".join(ann.GetLabel().GetValue() for ann in annphons)

            # Append in the new tier
            newann = anntoken.Copy()
            score = newann.GetLabel().GetLabel().GetScore()
            newann.GetLabel().SetValue(Text(l,score))
            newtier.Add(newann)

        return newtier

    # ------------------------------------------------------------------------

    def run(self, phonesname, tokensname, audioname, outputfilename):
        """
        Execute SPPAS Alignment.

        @param phonesname (str - IN) file containing the phonetization
        @param tokensname (str - IN) file containing the tokenization
        @param audioname (str - IN) Audio file name
        @param outputfilename (str - IN) the file name with the result

        @return Transcription

        """
        self.print_options()
        self.print_diagnosis(audioname, phonesname, tokensname)

        # Get the tiers to be time-aligned
        # ---------------------------------------------------------------

        trsinput = sppas.src.annotationdata.aio.read(phonesname)
        phontier = self.get_phonestier(trsinput)
        if phontier is None:
            raise IOError("No tier with the phonetization was found.")

        try:
            trsinputtok = sppas.src.annotationdata.aio.read(tokensname)
            toktier = self.get_tokenstier(trsinputtok)
        except Exception:
            toktier = None
            self.print_message("Tokens alignment disabled.", indent=2, status=WARNING_ID)

        # Prepare data
        # -------------------------------------------------------------

        inputaudio = sppas.src.utils.fileutils.fix_audioinput(audioname)
        workdir    = sppas.src.utils.fileutils.fix_workingdir(inputaudio)
        if self._options['clean'] is False:
            self.print_message("The working directory is: %s"%workdir, indent=3, status=None)

        # Processing...
        # ---------------------------------------------------------------

        try:
            trsoutput = self.convert(phontier,toktier,audioname,workdir)
            if toktier is not None:
                trsoutput = self.append_extra(trsoutput)
        except Exception as e:
            self.print_message(str(e))
            self.print_message("WORKDIR=%s"%workdir)
            if self._options['clean'] is True:
                shutil.rmtree(workdir)
            raise

        # Set media
        # --------------------------------------------------------------

        extm = os.path.splitext(audioname)[1].lower()[1:]
        media = Media(gen_id(), audioname, "audio/"+extm)
        trsoutput.AddMedia(media)
        for tier in trsoutput:
            tier.SetMedia(media)

        # Save results
        # --------------------------------------------------------------
        try:
            self.print_message("Save automatic alignment: ",indent=3)
            # Save in a file
            sppas.src.annotationdata.aio.write(outputfilename,trsoutput)
        except Exception:
            if self._options['clean'] is True:
                shutil.rmtree(workdir)
            raise

        # Clean!
        # --------------------------------------------------------------
        # if the audio file was converted.... remove the tmpaudio
        if inputaudio != audioname:
            os.remove(inputaudio)
        # Remove the working directory we created
        if self._options['clean'] is True:
            shutil.rmtree(workdir)

    # ------------------------------------------------------------------------
    # Private: some very bad hack...
    # ------------------------------------------------------------------------

    def rustine_others(self, trs):
        """ veritable rustine pour decaler la fin des non-phonemes. """

        tierphon = trs.Find("PhonAlign")
        if tierphon is None:
            return trs

        imax = tierphon.GetSize() - 1
        for i, a in reversed(list(enumerate(tierphon))):
            if i < imax:
                nexta = tierphon[i+1]
                if nexta.GetLabel().GetValue() == "#":
                    continue
                durnexta = nexta.GetLocation().GetDuration()

                if a.GetLabel().GetValue() == "sil" and durnexta > 0.05:
                    a.GetLocation().SetEndMidpoint(a.GetLocation().GetEndMidpoint() + 0.03)
                    nexta.GetLocation().SetBeginMidpoint(a.GetLocation().GetEndMidpoint())

                if a.GetLabel().GetValue() in [ "*", "@@", "fp", "dummy" ] and durnexta > 0.04:
                    a.GetLocation().SetEndMidpoint(a.GetLocation().GetEndMidpoint() + 0.02)
                    nexta.GetLocation().SetBeginMidpoint(a.GetLocation().GetEndMidpoint())

        tiertok = trs.Find("TokensAlign")
        if tiertok is None:
            return trs

        imax = tiertok.GetSize() - 1
        for i, a in reversed(list(enumerate(tiertok))):
            if i < imax:
                nexta = tiertok[i+1]
                if nexta.GetLabel().GetValue() == "#":
                    continue
                durnexta = nexta.GetLocation().GetDuration()

                if a.GetLabel().GetValue() == "sil" and durnexta > 0.05:
                    a.GetLocation().SetEndMidpoint(a.GetLocation().GetEndMidpoint() + 0.03)
                    nexta.GetLocation().SetBeginMidpoint(a.GetLocation().GetEndMidpoint())

                if a.GetLabel().GetValue() in [ "*", "@", "euh", "dummy" ] and durnexta > 0.04:
                    a.GetLocation().SetEndMidpoint(a.GetLocation().GetEndMidpoint() + 0.02)
                    nexta.GetLocation().SetBeginMidpoint(a.GetLocation().GetEndMidpoint())

        return trs

    # ------------------------------------------------------------------------

    def rustine_liaisons(self, trs):
        """ veritable rustine pour supprimer qqs liaisons en trop. """

        # Only for French!
        if self.alignio.aligntrack.get_model().endswith("fra") is False:
            return trs

        logging.debug('SPPAS patch for the selection of liaisons...')

        tierphon   = trs.Find("PhonAlign")
        tiertokens = trs.Find("TokensAlign")
        if tiertokens is None or tierphon is None:
            return trs

        # supprime les /z/ et /t/ de fin de mot si leur duree est < 65ms.
        for i, a in reversed(list(enumerate(tierphon))):
            if a.GetLocation().GetDuration().GetValue() < 0.055 and a.GetLabel().GetValue() in [ "z", "n", "t" ]:
                # get the corresponding token
                for t in tiertokens:
                    # this is not the only phoneme in this token!
                    # and the token is not finishing by a vowel...
                    lastchar = t.GetLabel().GetValue()
                    if len(lastchar)>0:
                        lastchar = lastchar[-1]
                    if a.GetLocation().GetEnd() == t.GetLocation().GetEnd() and a.GetLocation().GetBegin() != t.GetLocation().GetBegin() and not lastchar in ["a", "e", "i", "o", "u", u"é", u"à", u"è"] :
                        # Remove a and extend previous annotation
                        logging.debug(' ... liaison removed %s in token %s'%(a,t.GetLabel().GetValue()))
                        prev = tierphon[i-1]
                        a = tierphon.Pop(i)
                        prev.GetLocation().SetEndMidpoint(a.GetLocation().GetEndMidpoint())
                        #self.logfile.print_message("Liaison removed: %s " % a)
                        # Enlever le phoneme de tierphntok!
                        # TODO
        return trs

    # ------------------------------------------------------------------------
