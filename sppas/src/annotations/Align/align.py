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
# File: align.py
# ----------------------------------------------------------------------------

import shutil
import os.path
import glob
import logging

from presenters.audiosppaspresenter import AudioSppasPresenter
import utils.fileutils as fileutils

import audiodata.io
import annotationdata.io
from annotationdata import Transcription
from annotationdata import Tier
from annotationdata import Media
from annotationdata import Text
from annotationdata.io.utils import gen_id

from speechseg import SpeechSegmenter
from alignio   import AlignIO
from activity  import Activity

from sp_glob import ERROR_ID, WARNING_ID, OK_ID, INFO_ID
from sp_glob import RESOURCES_PATH

from resources.mapping        import Mapping
from resources.acm.modelmixer import ModelMixer

# ----------------------------------------------------------------------------

class sppasAlign:
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
        - PhnTokALign - option (if tokens are given in the input),
        - Activity    - option (if tokens are given in the input),

    How to use sppasAlign?

    >>> a = sppasAlign( modeldirname )
    >>> a.run(inputphonesname, inputtokensname, inputaudioname, outputfilename)

    """
    def __init__(self, model, modelL1=None, logfile=None):
        """
        Create a new sppasAlign instance.

        @param model (str) the acoustic model directory name of the language of the text
        @param modelL1 (str) the acoustic model directory name of the mother language of the speaker
        @param logfile (sppasLog)

        """
        # Log messages for the user
        self.logfile = logfile

        # Members: self.speechseg and self.alignio
        self.fix_segmenter( model,modelL1 )

        self.workdir = ""
        self.inputaudio = ""

        # List of options to configure this automatic annotation
        self._options = {}
        self._options['clean']   = True  # Remove temporary files
        self._options['infersp'] = False # Add 'sp' at the end of each token
        self._options['basic']   = False # Perform a basic alignment if error
        self._options['activity'] = True
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
                modelmixer.load( model,modelL1 )
                outputdir = os.path.join(RESOURCES_PATH, "models", "models-mix")
                modelmixer.mix( outputdir, gamma=1. )
                model = outputdir
            except Exception as e:
                if self.logfile is not None:
                    self.logfile.print_message("The model is ignored: %s"%str(e), indent=3, status=WARNING_ID)
                else:
                    logging.info( "The model is ignored: %s"%str(e) )

        # The automatic alignment system; it will use the default aligner
        self.speechseg = SpeechSegmenter( model )

        # Map phoneme names from model-specific to SAMPA and vice-versa
        mappingfilename = os.path.join( model, "monophones.repl")
        if os.path.isfile( mappingfilename ):
            try:
                mapping = Mapping( mappingfilename )
            except Exception:
                mapping = Mapping()
        else:
            mapping = Mapping()

        # Manager of the interval tracks
        self.alignio = AlignIO( mapping )

    # ------------------------------------------------------------------------
    # Methods to fix options
    # ------------------------------------------------------------------------

    def get_option(self, key):
        """
        Return the option value of a given key or raise an Exception.

        """
        return self._options[key]

    # ------------------------------------------------------------------------

    def fix_options(self, options):
        """
        Fix all options.

        @param options (option)

        """
        for opt in options:

            key = opt.get_key()

            if "clean" == key:
                self.set_clean( opt.get_value() )

            elif "basic" == key:
                self.set_basic( opt.get_value() )

            elif "aligner" == key:
                self.set_aligner( opt.get_value() )

            elif "infersp" == key:
                self.set_infersp( opt.get_value() )

            elif "activity" == key:
                self.set_activity_tier( opt.get_value() )

            elif "phntok" == key:
                self.set_phntokalign_tier( opt.get_value() )

            else:
                raise Exception('Unknown key option: %s'%key)

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
        self.speechseg.set_aligner(alignername)

    # -----------------------------------------------------------------------

    def set_infersp(self, infersp):
        """
        Fix the infersp option.

        @param infersp (bool - IN) If infersp is set to True, the aligner
        will add an optional short pause at the end of each token, and the
        will infer if it is relevant.

        """
        self.speechseg.set_infersp( infersp )

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

    def set_phntokalign_tier(self, value):
        """
        Fix the phntok option.

        @param value (bool - IN) PhnTokAlign tier generation.

        """
        self._options['phntok'] = bool(value)

    # -----------------------------------------------------------------------
    # Methods to time-align series of data
    # -----------------------------------------------------------------------

    def print_message(self, message, indent=3, status=INFO_ID):
        """
        Print a message either in the user log or in the console log.

        """
        if self.logfile:
            self.logfile.print_message(message, indent=indent, status=status)

        elif len(message) > 0:
            if status==INFO_ID:
                logging.info( message )
            elif status==WARNING_ID:
                logging.warning( message )
            elif status==ERROR_ID:
                logging.error( message )
            else:
                logging.debug( message )

    # -----------------------------------------------------------------------

    def fix_audioinput(self, inputaudioname):
        """
        Fix the audio file name that will be used.
        An only-ascii-based file name without whitespace is set if the
        current audio file name does not fit in these requirements.

        @param inputaudioname (str - IN) Given audio file name

        """
        self.inputaudio = fileutils.string_to_ascii(fileutils.format_filename(inputaudioname))
        if self.inputaudio != inputaudioname:
            shutil.copy(inputaudioname, self.inputaudio)

        try:
            audio = audiodata.io.open( self.inputaudio )
            audio.close()
        except IOError as e:
            raise IOError("Not a valid audio file: "+str(e))

    # ------------------------------------------------------------------------

    def fix_workingdir(self):
        """
        Fix the working directory to store temporarily the data.

        """
        if len(self.inputaudio) == 0:
            # Notice that the following generates a directory that the
            # aligners won't be able to access under Windows.
            # No problem with MacOS or Linux.
            self.workdir = fileutils.gen_name()
            while os.path.exists( self.workdir ) is True:
                self.workdir = fileutils.gen_name()
        else:
            self.workdir = os.path.splitext(self.inputaudio)[0]+"-temp"

        os.mkdir( self.workdir )

    # ------------------------------------------------------------------------

    def convert_tracks(self, diralign, trstier):
        """
        Call the Aligner to align each unit of a directory.

        @param diralign is the directory to get units and put alignments.
        @param trstier (Tier) required only if basic alignment.

        """
        # Verify if the directory exists
        if not os.path.exists( diralign ):
            raise IOError('The directory '+diralign+' does not exist.')

        # Get all audio tracks
        dirlist = glob.glob(os.path.join(diralign, "track_*.wav"))
        ntracks = len(dirlist)
        if ntracks == 0:
            raise IOError('The directory '+diralign+' does not contain data.')

        track = 1
        while track <= ntracks:
            self.print_message('Align unit number '+str(track), indent=3)

            audiofilename = self.alignio.get_audiofilename(diralign,track)
            phonname      = self.alignio.get_phonesfilename(diralign,track)
            tokenname     = self.alignio.get_tokensfilename(diralign,track)
            alignname     = self.alignio.get_alignfilename(diralign,track)

            try:
                msg = self.speechseg.segmenter(audiofilename, phonname, tokenname, alignname)
                self.print_message(msg, indent=3, status=INFO_ID)

            except Exception as e:
                self.print_message(self.speechseg._alignerid+' failed to perform segmentation.', indent=3, status=ERROR_ID)
                self.print_message(str(e), indent=4, status=INFO_ID)
                #    import traceback
                #    print(traceback.format_exc())

                #if os.path.exists(alignname):
                #    os.rename(alignname, alignname+'.backup')

                # Execute BasicAlign
                if self._options['basic'] is True:
                    if self.logfile:
                        self.logfile.print_message('Execute a Basic Alignment - same duration for each phoneme:', indent=3)
                    alignerid = self.speechseg.get_aligner()
                    self.speechseg.set_aligner('basic')
                    alignname = self.alignio.get_alignfilename(diralign,track)
                    self.speechseg.segmenter(audiofilename, phonname, tokenname, alignname)
                    self.speechseg.set_aligner(alignerid)
                # or Create an empty alignment, to get an empty interval in the final tier
                else:
                    self.speechseg.segmenter(audiofilename, None, None, alignname)

            track = track + 1

    # ------------------------------------------------------------------------

    def convert( self, phontier, toktier, audioname ):
        """
        Perform speech segmentation of data in tiers tokenization/phonetization.

        @param phontier (Tier - IN) The phonetization.
        @param toktier (Tier - IN) The tokenization, or None.
        @param audioname (str - IN) Audio file name.

        @return A transcription.

        """
        # Prepare data
        # -------------------------------------------------------------

        # Fix the input audio file: self.inputaudio
        self.fix_audioinput(audioname)

        # Fix the working directory name: self.workdir
        self.fix_workingdir()
        if self._options['clean'] is False:
            self.print_message( "The working directory is: %s"%self.workdir, indent=3, status=INFO_ID )

        # Split input into tracks
        # --------------------------------------------------------------

        self.print_message("Split into intervals: ", indent=2)

        try:
            self.alignio.split( self.inputaudio, phontier, toktier, self.workdir )
        except Exception as e:
            self.alignio.split( self.inputaudio, phontier, None, self.workdir )
            self.print_message("Tokens alignment disabled: %s"%str(e), indent=3, status=WARNING_ID)

        self.print_message("", indent=2, status=OK_ID)

        # Align each track
        # --------------------------------------------------------------

        self.print_message("Align each interval: ", indent=2)
        self.convert_tracks( self.workdir, phontier )
        self.print_message("", indent=2, status=OK_ID)

        # Merge track alignment results
        # --------------------------------------------------------------

        self.print_message("Merge interval's alignment:", indent=2)

        # Create a Transcription() object with alignments
        trsoutput = self.alignio.read( self.workdir )

        if self.speechseg._alignerid != 'basic':
            trsoutput = self.rustine_liaisons(trsoutput)
            trsoutput = self.rustine_others(trsoutput)

        self.print_message("", indent=4, status=OK_ID)

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
                trs.GetHierarchy().addLink("TimeAssociation", tokenalign, tier)
            except Exception as e:
                self.print_message("PhnTokAlign generation: %s"%str(e), indent=2, status=WARNING_ID)

        # Activity tier
        if self._options['activity'] is True:
            try:
                activity = Activity( trs )
                tier = activity.get_tier()
                trs.Append(tier)
                trs.GetHierarchy().addLink("TimeAlignment", tokenalign, tier)
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

        # We got the phonetization from a raw text file
        if trsinput.GetSize() == 1 and trsinput[0].GetName().lower() == "rawtranscription":
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

        if toktier is None:
            # We got the tokenization from a raw text file
            if trsinput.GetSize() == 1 and trsinput[0].GetName().lower() == "rawtranscription":
                return tier

        return toktier

    # ------------------------------------------------------------------------

    def phntokalign_tier(self, tierphon, tiertoken):
        """
        Generates the PhnTokAlignTier from PhonAlign and TokensAlign.

        """
        newtier = Tier('PhnTokAlign')
        newtier.SetMedia( tiertoken.GetMedia() )

        for anntoken in tiertoken:

            # Create the sequence of phonemes
            beg = anntoken.GetLocation().GetBegin()
            end = anntoken.GetLocation().GetEnd()
            annphons = tierphon.Find(beg,end)
            l = "-".join( ann.GetLabel().GetValue() for ann in annphons )

            # Append in the new tier
            newann = anntoken.Copy()
            score = newann.GetLabel().GetLabel().GetScore()
            newann.GetLabel().SetValue( Text(l,score) )
            newtier.Add( newann )

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
        for k,v in self._options.items():
            self.print_message("Option %s: %s"%(k,v), indent=2, status=INFO_ID)

        # Get the tiers to be time-aligned
        # ---------------------------------------------------------------

        trsinput = annotationdata.io.read( phonesname )
        phontier = self.get_phonestier( trsinput )
        if phontier is None:
            raise IOError("No tier with the phonetization was found.")

        try:
            trsinputtok = annotationdata.io.read( tokensname )
            toktier = self.get_tokenstier( trsinputtok )
        except Exception:
            toktier = None
            self.print_message("Tokens alignment disabled.", indent=2, status=WARNING_ID)

        # Processing...
        # ---------------------------------------------------------------

        try:
            trsoutput = self.convert( phontier,toktier,audioname )
            if toktier is not None:
                trsoutput = self.append_extra(trsoutput)
        except Exception as e:
            self.print_message( str(e) )
            self.print_message("WORKDIR=%s"%self.workdir)
            #if self._options['clean'] is True:
            #    shutil.rmtree( self.workdir )
            raise

        # Set media
        # --------------------------------------------------------------

        extm = os.path.splitext(audioname)[1].lower()[1:]
        media = Media( gen_id(), audioname, "audio/"+extm )
        trsoutput.AddMedia( media )
        for tier in trsoutput:
            tier.SetMedia( media )

        # Save results
        # --------------------------------------------------------------
        try:
            self.print_message("Save alignment of the units: ",indent=3)
            # Save in a file
            annotationdata.io.write( outputfilename,trsoutput )
            self.print_message("", indent=4, status=OK_ID)
        except Exception:
            if self._options['clean'] is True:
                shutil.rmtree( self.workdir )
            raise

        # Clean!
        # --------------------------------------------------------------
        # if the audio file was converted.... remove the tmpaudio
        if self.inputaudio != audioname:
            os.remove(self.inputaudio)
        # Remove the working directory we created
        if self._options['clean'] is True:
            shutil.rmtree( self.workdir )


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
                    a.GetLocation().SetEndMidpoint( a.GetLocation().GetEndMidpoint() + 0.03 )
                    nexta.GetLocation().SetBeginMidpoint( a.GetLocation().GetEndMidpoint() )

                if a.GetLabel().GetValue() in [ "*", "@@", "fp", "dummy" ] and durnexta > 0.04:
                    a.GetLocation().SetEndMidpoint( a.GetLocation().GetEndMidpoint() + 0.02 )
                    nexta.GetLocation().SetBeginMidpoint( a.GetLocation().GetEndMidpoint() )

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
                    a.GetLocation().SetEndMidpoint( a.GetLocation().GetEndMidpoint() + 0.03 )
                    nexta.GetLocation().SetBeginMidpoint( a.GetLocation().GetEndMidpoint() )

                if a.GetLabel().GetValue() in [ "*", "@", "euh", "dummy" ] and durnexta > 0.04:
                    a.GetLocation().SetEndMidpoint( a.GetLocation().GetEndMidpoint() + 0.02 )
                    nexta.GetLocation().SetBeginMidpoint( a.GetLocation().GetEndMidpoint() )

        return trs

    # ------------------------------------------------------------------------

    def rustine_liaisons(self, trs):
        """ veritable rustine pour supprimer qqs liaisons en trop. """
        # Only for French!
        if self.speechseg.get_model().startswith("fra") is False:
            return trs

        tierphon   = trs.Find("PhonAlign")
        tiertokens = trs.Find("TokensAlign")
        if tiertokens is None or tierphon is None:
            return trs

        # supprime les /z/ et /t/ de fin de mot si leur duree est < 65ms.
        for i, a in reversed(list(enumerate(tierphon))):
            if a.GetLocation().GetDuration() < 0.045 and a.GetLabel().GetValue() in [ "z", "n", "t" ]:
                # get the corresponding token
                for t in tiertokens:
                    # this is not the only phoneme in this token!
                    # and the token is not finishing by a vowel...
                    lastchar = t.GetLabel().GetValue()
                    if len(lastchar)>0:
                        lastchar = lastchar[-1]
                    if a.GetLocation().GetEnd() == t.GetLocation().GetEnd() and a.GetLocation().GetBegin() != t.GetLocation().GetBegin() and not lastchar in ["a", "e", "i", "o", "u", u"é", u"à", u"è"] :
                        # Remove a and extend previous annotation
                        prev = tierphon[i-1]
                        a = tierphon.Pop(i)
                        prev.GetLocation().SetEndMidpoint( a.GetLocation().GetEndMidpoint() )
                        #self.logfile.print_message( "Liaison removed: %s " % a)
                        # Enlever le phoneme de tierphntok!

        return trs

    # ------------------------------------------------------------------------
