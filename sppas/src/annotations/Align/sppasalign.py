# -*- coding: UTF-8 -*-
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

    src.annotations.Align.sppasalign.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import shutil
import os.path
import glob
import logging

from sppas.src.config import paths
import sppas.src.annotationdata.aio
from sppas.src.annotationdata import Transcription
from sppas.src.annotationdata import Tier
from sppas.src.annotationdata import Media
from sppas.src.annotationdata import Text
from sppas.src.annotationdata.aio.utils import gen_id
from sppas.src.resources.mapping import sppasMapping
from sppas.src.models.acm.modelmixer import sppasModelMixer

from .. import t
from .. import ERROR_ID, WARNING_ID, INFO_ID
from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasSearchTier
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import NoDirectoryError
from ..annotationsexc import EmptyDirectoryError
from ..annotationsexc import NoInputError
from ..annutils import fix_audioinput, fix_workingdir

from .alignio import AlignIO
from .activity import sppasActivity

# ----------------------------------------------------------------------------

MSG_MODEL_L1_FAILED = (t.gettext(":INFO 1210: "))
MSG_ALIGN_TRACK = (t.gettext(":INFO 1220: "))
MSG_ALIGN_FAILED = (t.gettext(":INFO 1230: "))
MSG_BASIC = (t.gettext(":INFO 1240: "))
MSG_ACTION_SPLIT_INTERVALS = (t.gettext(":INFO 1250: "))
MSG_ACTION_ALIGN_INTERVALS = (t.gettext(":INFO 1252: "))
MSG_ACTION_MERGE_INTERVALS = (t.gettext(":INFO 1254: "))
MSG_TOKENS_DISABLED = (t.gettext(":INFO 1260: "))
MSG_NO_TOKENS_ALIGN = (t.gettext(":INFO 1262: "))
MSG_EXTRA_TIER = (t.gettext(":INFO 1270: "))
MSG_WORKDIR = (t.gettext(":INFO 1280: "))

# ----------------------------------------------------------------------------


class sppasAlign(sppasBaseAnnotation):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS integration of the Alignment automatic annotation.

    This class can produce 1 up to 5 tiers with names:

        - PhonAlign
        - TokensAlign (if tokens are given in the input)
        - PhnTokAlign - option (if tokens are given in the input)
        - Activity - option (if tokens are given in the input)
        - ActivityDuration - option (if tokens are given in the input)

    How to use sppasAlign?

    >>> a = sppasAlign(model_dirname)
    >>> a.run(input_phones_filename, input_tokens_filename, input_audio_filename, output_filename)

    """
    def __init__(self, model, model_L1=None, logfile=None):
        """ Create a new sppasAlign instance.

        :param model: (str) Name of the directory of the acoustic model of the language of the text
        :param model_L1: (str) Name of the directory of the acoustic model of the mother language of the speaker
        :param logfile: (sppasLog)

        """
        sppasBaseAnnotation.__init__(self, logfile, "Alignment")
        self.mapping = sppasMapping()
        self.alignio = None

        self.fix_segmenter(model, model_L1)
        self.reset()

    # ------------------------------------------------------------------

    def reset(self):
        """ Reset the options to configure this automatic annotation. """

        self._options = dict()
        self._options['clean'] = True     # Remove temporary files
        self._options['infersp'] = False  # Add 'sp' at the end of each token
        self._options['basic'] = False    # Perform a basic alignment if error
        self._options['activity'] = True  # Add the Activity tier
        self._options['activityduration'] = False
        self._options['phntok'] = False   # Add the PhnTokAlign tier

    # -----------------------------------------------------------------------

    def fix_segmenter(self, model, model_L1):
        """ Fix the acoustic model directory, then create a SpeechSegmenter and AlignerIO.

        :param model: (str) Name of the directory of the acoustic model of the language of the text
        :param model_L1: (str) Name of the directory of the acoustic model of the mother language of the speaker

        """
        if model_L1 is not None:
            try:
                model_mixer = sppasModelMixer()
                model_mixer.load(model, model_L1)
                output_dir = os.path.join(paths.resources, "models", "models-mix")
                model_mixer.mix(output_dir, gamma=0.6)
                model = output_dir
            except Exception as e:
                self.print_message(MSG_MODEL_L1_FAILED.format(str(e)), indent=3, status=WARNING_ID)

        # Map phoneme names from model-specific to SAMPA and vice-versa
        mapping_filename = os.path.join(model, "monophones.repl")
        if os.path.isfile(mapping_filename):
            try:
                mapping = sppasMapping(mapping_filename)
            except Exception:
                mapping = sppasMapping()
        else:
            mapping = sppasMapping()

        # Manager of the interval tracks
        self.alignio = AlignIO(mapping, model)

    # ------------------------------------------------------------------------
    # Methods to fix options
    # ------------------------------------------------------------------------

    def fix_options(self, options):
        """ Fix all options. Available options are:

            - clean
            - basic
            - aligner
            - infersp
            - activity
            - activityduration
            - phntok

        :param options: (sppasOption)

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
                self.set_activity_duration_tier(opt.get_value())

            elif "phntok" == key:
                self.set_phntokalign_tier(opt.get_value())

            else:
                raise AnnotationOptionError(key)

    # ----------------------------------------------------------------------

    def set_clean(self, clean):
        """ Fix the clean option.

        :param clean: (bool) If clean is set to True then temporary files
        will be removed.

        """
        self._options['clean'] = clean

    # -----------------------------------------------------------------------

    def set_aligner(self, aligner_name):
        """ Fix the name of the aligner.

        :param aligner_name: (str) Case-insensitive name of the aligner.

        """
        self.alignio.set_aligner(aligner_name)
        self._options['aligner'] = aligner_name

    # -----------------------------------------------------------------------

    def set_infersp(self, infersp):
        """ Fix the infersp option.

        :param infersp: (bool) When set to True, the aligner adds an optional
        short pause at the end of each token, and it will infer it.
        Unfortunately... it does not really work as we expected!

        """
        self.alignio.set_infersp(infersp)

    # -----------------------------------------------------------------------

    def set_basic(self, basic):
        """ Fix the basic option.

        :param basic: (bool) If basic is set to True, a basic segmentation
        will be performed if the main aligner fails.

        """
        self._options['basic'] = basic

    # -----------------------------------------------------------------------

    def set_activity_tier(self, value):
        """ Fix the activity option.

        :param value: (bool) Activity tier generation.

        """
        self._options['activity'] = bool(value)

    # -----------------------------------------------------------------------

    def set_activity_duration_tier(self, value):
        """ Fix the activity duration option.

        :param value: (bool) Activity tier generation.

        """
        self._options['activityduration'] = bool(value)

    # -----------------------------------------------------------------------

    def set_phntokalign_tier(self, value):
        """ Fix the phntok option.

        :param value: (bool) PhnTokAlign tier generation.

        """
        self._options['phntok'] = bool(value)

    # -----------------------------------------------------------------------
    # Methods to time-align series of data
    # -----------------------------------------------------------------------

    def convert_tracks(self, diralign):
        """ Call the Aligner to align each unit of a directory.

        :param diralign: the directory to get units and put alignments.

        """
        # Verify if the directory exists
        if os.path.exists(diralign) is False:
            raise NoDirectoryError(diralign)

        # Get all audio tracks
        dirlist = glob.glob(os.path.join(diralign, "track_*.wav"))
        ntracks = len(dirlist)
        if ntracks == 0:
            raise EmptyDirectoryError(diralign)

        track = 1
        while track <= ntracks:
            self.print_message(MSG_ALIGN_TRACK.format(number=track), indent=2)

            try:
                msg = self.alignio.segment_track(track, diralign)
                if len(msg) > 0:
                    self.print_message(msg, indent=3, status=INFO_ID)

            except Exception as e:
                self.print_message(MSG_ALIGN_FAILED.format(name=self.alignio.get_aligner()), indent=3, status=ERROR_ID)
                self.print_message(str(e), indent=4, status=INFO_ID)

                # Execute BasicAlign
                if self._options['basic'] is True:
                    if self.logfile:
                        self.logfile.print_message(MSG_BASIC, indent=3)
                    aligner_id = self.alignio.get_aligner()
                    self.alignio.set_aligner('basic')
                    self.alignio.segment_track(track, diralign)
                    self.alignio.set_aligner(aligner_id)

                # or Create an empty alignment, to get an empty interval in the final tier
                else:
                    self.alignio.segment_track(track, diralign, segment=False)

            track += 1

    # ------------------------------------------------------------------------

    def convert(self, phontier, toktier, inputaudio, workdir):
        """ Perform speech segmentation of data in tiers tokenization/phonetization.

        :param phontier: (Tier) The phonetization.
        :param toktier: (Tier) The tokenization, or None.
        :param inputaudio: (str) Audio file name.
        :param workdir: (str) The working directory

        :returns: A transcription.

        """
        if os.path.exists(workdir) is False:
            os.mkdir(workdir)

        # Split input into tracks
        # --------------------------------------------------------------

        self.print_message(MSG_ACTION_SPLIT_INTERVALS, indent=2)
        sgmt = self.alignio.split(inputaudio, phontier, toktier, workdir)

        # Align each track
        # --------------------------------------------------------------

        self.convert_tracks(workdir)

        # Merge track alignment results
        # --------------------------------------------------------------

        self.print_message(MSG_ACTION_MERGE_INTERVALS, indent=2)

        trs_output = Transcription("AutomaticAlignment")
        for tier in sgmt:
            trs_output.Append(tier)

        # Create a Transcription() object with alignments
        trs = self.alignio.read(workdir)
        if self.alignio.get_aligner() != 'basic':
            trs = self.rustine_liaisons(trs)
            trs = self.rustine_others(trs)
        for tier in trs:
            trs_output.Append(tier)

        return trs_output

    # ------------------------------------------------------------------------

    def append_extra(self, trs):
        """ Append extra tiers in trs.

        :param trs: (Transcription)

        """
        token_align = trs.Find("TokensAlign")
        if token_align is None:
            self.print_message(MSG_NO_TOKENS_ALIGN, indent=2, status=WARNING_ID)
            return trs

        # PhnTokAlign tier
        if self._options['phntok'] is True:
            try:
                phonalign = trs.Find("PhonAlign")
                tier = sppasAlign.phntokalign_tier(phonalign, token_align)
                trs.Append(tier)
                trs.GetHierarchy().add_link("TimeAssociation", token_align, tier)
            except Exception as e:
                self.print_message(
                    MSG_EXTRA_TIER.format(tiername="PhnTokAlign", message=str(e)), 
                    indent=2, 
                    status=WARNING_ID)

        # Activity tier
        if self._options['activity'] is True or self._options['activityduration'] is True:
            try:
                activity = sppasActivity()
                tier = activity.get_tier(trs)
                if self._options['activity'] is True:
                    trs.Append(tier)
                    trs.GetHierarchy().add_link("TimeAlignment", token_align, tier)

                if self._options['activityduration'] is True:
                    dtier = tier.Copy()
                    dtier.SetName("ActivityDuration")
                    trs.Append(dtier)
                    for a in dtier:
                        d = a.GetLocation().GetDuration().GetValue()
                        a.GetLabel().SetValue('%.3f' % d)

            except Exception as e:
                self.print_message(
                    MSG_EXTRA_TIER.format(tiername="Activities", message=str(e)), 
                    indent=2, 
                    status=WARNING_ID)

        return trs

    # ------------------------------------------------------------------------

    @staticmethod
    def phntokalign_tier(tierphon, tiertoken):
        """ Generates the PhnTokAlignTier from PhonAlign and TokensAlign.

        :param tierphon: (Tier)
        :param tiertoken: (Tier)

        """
        new_tier = Tier('PhnTokAlign')
        new_tier.SetMedia(tiertoken.GetMedia())

        for ann_token in tiertoken:

            # Create the sequence of phonemes
            # Use only the phoneme with the best score.
            # Don't generate alternatives, and won't never do it.
            beg = ann_token.GetLocation().GetBegin()
            end = ann_token.GetLocation().GetEnd()
            ann_phons = tierphon.Find(beg, end)
            l = "-".join(ann.GetLabel().GetValue() for ann in ann_phons)

            # Append in the new tier
            new_ann = ann_token.Copy()
            score = new_ann.GetLabel().GetLabel().GetScore()
            new_ann.GetLabel().SetValue(Text(l, score))
            new_tier.Add(new_ann)

        return new_tier

    # ------------------------------------------------------------------------

    def run(self, phonesname, tokensname, audioname, outputfilename):
        """ Execute SPPAS Alignment.

        :param phonesname: (str) file containing the phonetization
        :param tokensname: (str) file containing the tokenization
        :param audioname: (str) Audio file name
        :param outputfilename: (str) the file name with the result

        :returns: (Transcription)

        """
        self.print_filename(audioname)
        self.print_options()
        self.print_diagnosis(audioname, phonesname, tokensname)

        # Get the tiers to be time-aligned
        # ---------------------------------------------------------------

        trsinput = sppas.src.annotationdata.aio.read(phonesname)
        phontier = sppasSearchTier.phonetization(trsinput)
        if phontier is None:
            raise NoInputError

        try:
            trsinputtok = sppas.src.annotationdata.aio.read(tokensname)
            toktier = sppasSearchTier.tokenization(trsinputtok)
        except Exception:   # IOError, AttributeError:
            toktier = None
            self.print_message(MSG_TOKENS_DISABLED, indent=2, status=WARNING_ID)

        # Prepare data
        # -------------------------------------------------------------

        inputaudio = fix_audioinput(audioname)
        workdir = fix_workingdir(inputaudio)
        if self._options['clean'] is False:
            self.print_message(MSG_WORKDIR.format(dirname=workdir), indent=3, status=None)

        # Processing...
        # ---------------------------------------------------------------

        try:
            trs_output = self.convert(phontier, toktier, audioname, workdir)
            if toktier is not None:
                trs_output = self.append_extra(trs_output)
        except Exception as e:
            self.print_message(str(e))
            if self._options['clean'] is True:
                shutil.rmtree(workdir)
            raise

        # Set media
        # --------------------------------------------------------------

        extm = os.path.splitext(audioname)[1].lower()[1:]
        media = Media(gen_id(), audioname, "audio/"+extm)
        trs_output.AddMedia(media)
        for tier in trs_output:
            tier.SetMedia(media)

        # Save results
        # --------------------------------------------------------------
        try:
            # Save in a file
            sppas.src.annotationdata.aio.write(outputfilename, trs_output)
            self.print_filename(outputfilename, status=0)
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

                if a.GetLabel().GetValue() in ["fp", "dummy"] and durnexta > 0.04:
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

                if a.GetLabel().GetValue() in ["euh", "dummy"] and durnexta > 0.04:
                    a.GetLocation().SetEndMidpoint(a.GetLocation().GetEndMidpoint() + 0.02)
                    nexta.GetLocation().SetBeginMidpoint(a.GetLocation().GetEndMidpoint())

        return trs

    # ------------------------------------------------------------------------

    def rustine_liaisons(self, trs):
        """ veritable rustine pour supprimer qqs liaisons en trop. """

        # Only for French!
        if self.alignio.aligntrack.get_model().endswith("fra") is False:
            return trs

        logging.debug('LIAISONS patch...')

        tierphon = trs.Find("PhonAlign")
        tiertokens = trs.Find("TokensAlign")
        if tiertokens is None or tierphon is None:
            return trs

        # supprime les /z/ et /t/ de fin de mot si leur duree est < 65ms.
        for i, a in reversed(list(enumerate(tierphon))):
            if a.GetLocation().GetDuration().GetValue() < 0.055 and \
               a.GetLabel().GetValue() in ["z", "n", "t"]:
                # get the corresponding token
                for t in tiertokens:
                    # this is not the only phoneme in this token!
                    # and the token is not finishing by a vowel...
                    last_char = t.GetLabel().GetValue()
                    if len(last_char) > 0:
                        last_char = last_char[-1]
                    if a.GetLocation().GetEnd() == t.GetLocation().GetEnd() and \
                       a.GetLocation().GetBegin() != t.GetLocation().GetBegin() and \
                       last_char not in ["a", "e", "i", "o", "u", u"é", u"à", u"è"]:
                        # Remove a and extend previous annotation
                        logging.debug(' ... liaison removed %s in token %s' % (a, t.GetLabel().GetValue()))
                        prev = tierphon[i-1]
                        a = tierphon.Pop(i)
                        prev.GetLocation().SetEndMidpoint(a.GetLocation().GetEndMidpoint())
                        #self.logfile.print_message("Liaison removed: %s " % a)

        return trs
