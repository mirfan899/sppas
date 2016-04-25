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

from presenters.audiosppaspresenter import AudioSppasPresenter
import utils.fileutils as fileutils

import annotationdata.io
from annotationdata.transcription import Transcription
from annotationdata.media         import Media
from annotationdata.io.utils      import gen_id

from speechseg import SpeechSegmenter
from alignerio import AlignerIO

from sp_glob import ERROR_ID, WARNING_ID, OK_ID, INFO_ID

# ----------------------------------------------------------------------------

class sppasAlign:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      SPPAS integration of the Alignment automatic annotation.

    SPPAS automatic Alignment is also called phonetic segmentation.
    Alignment is performed in 3 sub-steps:

        1. Split the audio/trs into units;
        2. Align each unit using an external aligner;
        3. Create a transcription with results.

    If step 1 fails, a basic alignment is applied on all units.
    At step 2, if the aligner fails, a basic alignment is applied on the unit.

    This alignment produces 1 or 3 tiers with names:

        - Phonemes,
        - PhonTokens (if tokens are given in the input),
        - Tokens (if tokens are given in the input).

    How to use sppasAlign?

    >>> a = sppasAlign( modeldirname )
    >>> a.run(inputphonesname, inputtokensname, inputaudioname, outputfilename)

    """
    def __init__(self, model, modelL1=None, logfile=None):
        """
        Create a new sppasAlign instance.

        @param model is the acoustic model directory name of the language of the text,
        @param modelL1 is the acoustic model directory name of the mother language of the speaker,
        @param logfile is a file descriptor of a log file (see log.py).

        """
        # The automatic alignment system:
        self.speechseg = SpeechSegmenter( model )
        self.logfile = logfile

        # List of options to configure this automatic annotation
        self._options = {}
        self._options['expend']  = True
        self._options['extend']  = False
        self._options['clean']   = True  # Remove temporary files
        self._options['infersp'] = False # Add 'sp' at the end of each token
        self._options['basic']   = False # Perform a basic alimnent if error

    # ------------------------------------------------------------------------
    # Methods to fix options
    # ------------------------------------------------------------------------

    def fix_options(self, options):
        """
        Fix all options.

        @param options (option)

        """
        for opt in options:
            if "expend" == opt.get_key():
                self.set_expend( opt.get_value() )
            elif "extend" == opt.get_key():
                self.set_extend( opt.get_value() )
            elif "clean" == opt.get_key():
                self.set_clean( opt.get_value() )
            elif "aligner" == opt.get_key():
                self.set_aligner( opt.get_value() )
            elif "infersp" == opt.get_key():
                self.set_infersp( opt.get_value() )
            elif "basic" == opt.get_key():
                self.set_basic( opt.get_value() )

    # ------------------------------------------------------------------------

    def set_extend(self, extend):
        """
        Fix the extend option.
        If extend is set to True, sppasAlign() will extend the last
        phoneme/token to the audio file duration.
        Otherwise, a silence is inserted.

        @param extend is a Boolean

        """
        self._options['extend'] = extend

    # ----------------------------------------------------------------------

    def set_expend(self, expend):
        """
        Fix the expend option.
        If expend is set to True, sppasAlign() will expend the last
        phoneme/token of each unit to the unit duration.

        @param expend is a Boolean

        """
        self._options['expend'] = expend

    # ----------------------------------------------------------------------

    def set_clean(self, clean):
        """
        Fix the clean option.
        If clean is set to True, sppasAlign() will remove temporary files.

        @param clean is a Boolean

        """
        self._options['clean'] = clean

    # -----------------------------------------------------------------------

    def set_aligner(self, alignername):
        """
        Fix the name of the aligner: julius, hvite or basic.

        @param alignername is a string (upper/lower accepted)

        """
        self.speechseg.set_aligner(alignername)

    # -----------------------------------------------------------------------

    def set_infersp(self, infersp):
        """
        Fix the infersp option.
        If infersp is set to True, sppasAlign() will add a short pause at
        the end of each token, and the automatic aligner will infer if it is
        appropriate or not.

        @param infersp is a Boolean

        """
        self.speechseg.set_infersp( infersp )

    # -----------------------------------------------------------------------

    def set_basic(self, basic):
        """
        Fix the basic option.
        If basic is set to True, sppasAlign() will perform a basic segmentation
        if an aligner fails.

        @param basic is a Boolean

        """
        self._options['basic'] = basic

    # -----------------------------------------------------------------------
    # Methods to time-align series of data
    # -----------------------------------------------------------------------

    def audioinput(self):
        """
        Fix the self.inputaudio value.
        Verify if a audio file corresponds to the expected
        input format and convert_tracks if it is needed.

        @return Boolean value (the input audio file was converted or not).

        """
        isconverted = False
        tmpname = fileutils.gen_name() + ".wav"
        try:
            converter = AudioSppasPresenter(self.logfile)
            isconverted = converter.export(self.inputaudio, tmpname)
        except Exception:
            pass

        if isconverted is False:
            testname = fileutils.string_to_ascii(fileutils.format_filename(self.inputaudio))
            if testname != self.inputaudio:
                shutil.copy(self.inputaudio, tmpname)
                isconverted = True

        if isconverted is True:
            self.inputaudio = tmpname

        return isconverted

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

        if self.speechseg._alignerid == 'basic':
            self.__convert_basic(diralign, trstier)
            return

        # Get all audio tracks
        dirlist = glob.glob(os.path.join(diralign, "track_*.wav"))
        ntracks = len(dirlist)
        if ntracks == 0:
            raise IOError('The directory '+diralign+' does not contain tracks.')

        track = 1
        while track <= ntracks:

            if self.logfile:
                self.logfile.print_message('Align unit number '+str(track), indent=3)

            audiofilename = os.path.join(diralign, "track_%06d.wav"%track)
            phonname      = os.path.join(diralign, "track_%06d.phon"%track)
            alignname     = os.path.join(diralign, "track_%06d.%s"%(track,self.speechseg._aligner.get_outext()))

            try:
                msg = self.speechseg.segmenter(audiofilename, phonname, alignname)
                if self.logfile:
                    if len(msg) == 0:
                        self.logfile.print_message("", indent=3, status=OK_ID)
                    else:
                        self.logfile.print_message(msg, indent=3, status=INFO_ID)

            except Exception as e:
                if self.logfile:
                    self.logfile.print_message(self.speechseg._alignerid+' failed to perform segmentation.', indent=3, status=ERROR_ID)
                    self.logfile.print_message(str(e), indent=4, status=INFO_ID)

                if os.path.exists(alignname):
                    os.rename(alignname, alignname+'.backup')
                alignname = os.path.join(diralign, "track_%06d.%s"%(track,self.speechseg._basicaligner.get_outext()))

                # Execute BasicAlign
                if self._options['basic'] is True:
                    if self.logfile:
                        self.logfile.print_message('Execute a Basic Alignment - same duration for each phoneme:', indent=3)
                    self.speechseg.exec_basic_alignment(audiofilename, phonname, alignname)
                else:
                    self.speechseg.exec_basic_alignment(audiofilename, None, alignname)

            track = track + 1

    # ------------------------------------------------------------------------

    def convert( self, phontier, toktier, inputaudioname ):
        """
        Time-align an input tokenization/phonetization.

        @param phontier (Tier) contains the phonetization.
        @param toktier (Tier) contains the tokenization, or None.
        @return A transciption with 1 or 3 tiers.

        """
        # Set local file names
        self.inputaudio = inputaudioname

        # Verify the input audio file (and optionally convert it...)
        # --------------------------------------------------------------
        try:
            if self.logfile:
                self.logfile.print_message("Check audio file: ",indent=2)
            converted = self.audioinput( )
            if self.logfile:
                if converted is False:
                    self.logfile.print_message("", indent=3, status=OK_ID)
                else:
                    self.logfile.print_message("A copy of the file was created with the required format.", indent=3, status=INFO_ID)
        except IOError as e:
            raise IOError('Not a valid audio file: '+str(e))

        # Fix the working directory name
        # ------------------------------
        # we use inputaudio instead of inputphonesname because it contains
        # only ascii characters in filename (which is required under Windows).
        diralign, fileExt = os.path.splitext( self.inputaudio )
        if not os.path.exists( diralign ):
            os.mkdir( diralign )
            if self._options['clean'] is False:
                if self.logfile:
                    self.logfile.print_message("The working directory is: %s"%diralign, indent=3, status=INFO_ID)

        listfilename = os.path.join(diralign, "tracks.list")

        # Split input into inter-pausal units
        # --------------------------------------------------------------
        if self.logfile:
            self.logfile.print_message("Split into inter-pausal units: ",indent=2)

        try:
            s1 = s2 = 0
            t1 = t2 = 0
            if self.logfile:
                self.logfile.print_message("Phonemes",indent=3)

            (s1,t1) = self.speechseg.split( self.inputaudio, phontier, diralign, "phon", listfilename )

            if toktier is not None:
                if self.logfile:
                    self.logfile.print_message("Tokens",indent=3)
                dirtmp = diralign+"tmp"
                if not os.path.exists( dirtmp ):
                    os.mkdir( dirtmp )
                (s2,t2) = self.speechseg.split( self.inputaudio, toktier, dirtmp, "trans" )
                if s1 != s2  or  t1 != t2:
                    if self.logfile is not None:
                        self.logfile.print_message("Inconsistency between phonetization and tokenization: ", indent=3, status=WARNING_ID)
                        self.logfile.print_message("Got %d silences and %d IPUs in phonetization."%(s1,t1), indent=4)
                        self.logfile.print_message("Got %d silences and %d IPUs in tokenization"%(s2,t2), indent=4)
                        self.logfile.print_message("Tokens won't be time-aligned.", indent=4)
                    else:#out of SPPAS
                        raise Exception('align.py. Split error: inconsistency between phonemes and tokens (not the same number of IPUs)',indent=3)
                else:
                    self.speechseg.split( self.inputaudio, toktier, diralign, "trans" )
                shutil.rmtree( dirtmp )
        except Exception as e:
            if self._options['clean'] is True:
                shutil.rmtree( diralign )
            if self.logfile is not None:
                self.logfile.print_message("The audio input file is corrupted: "+str(e), indent=2, status=ERROR_ID)
                self.logfile.print_message("Automatic Speech Segmentation CAN'T work.", indent=2, status=INFO_ID)
                return
            else:
                raise

        if self.logfile:
            self.logfile.print_message("", indent=2, status=OK_ID)

        # Align each unit
        # --------------------------------------------------------------
        if self.logfile:
            self.logfile.print_message("Align each inter-pausal unit: ",indent=2)
        try:
            self.convert_tracks( diralign , phontier)
            if self.logfile:
                self.logfile.print_message("", indent=2, status=OK_ID)
        except Exception:
            if self._options['clean'] is True:
                shutil.rmtree( diralign )
            raise

        # Merge unit alignments
        # --------------------------------------------------------------
        if self.logfile:
            self.logfile.print_message("Merge unit's alignment and save into a file ", indent=2)

        # Create a Transcription() object with alignments
        if self.logfile:
            self.logfile.print_message("Read each alignment unit: ", indent=3)

        try:
            trsoutput = AlignerIO(self.speechseg._alignerid)
            if toktier is not None:
                trsoutput.read( diralign, listfilename, self.speechseg._mapping, expend=self._options['expend'], extend=self._options['extend'], tokens=True)
            else:
                trsoutput.read( diralign, listfilename, self.speechseg._mapping, expend=self._options['expend'], extend=self._options['extend'], tokens=False)

            if self.speechseg._alignerid != 'basic':
                trsoutput = self.rustine_liaisons(trsoutput)
                trsoutput = self.rustine_others(trsoutput)

            if self.logfile:
                self.logfile.print_message("", indent=4, status=OK_ID)

        except Exception:
            if self._options['clean'] is True:
                shutil.rmtree( diralign )
            raise # IOError("align.py. AlignerIO. Error while reading aligned tracks: " + str(e))

        # Set media
        extm = os.path.splitext(inputaudioname)[1].lower()[1:]
        media = Media( gen_id(), inputaudioname, "audio/"+extm )
        trsoutput.AddMedia( media )
        for tier in trsoutput:
            tier.SetMedia( media )

        return trsoutput

    # ------------------------------------------------------------------------

    def save(self, trsinput, inputfilename, trsoutput, outputfile=None):
        """
        Save depending on the given data.
        If no output file name is given, output is appended to the input.

        @param trsinput (Transcription)
        @param inputfilename (str)
        @param trsoutput (Transcription)
        @param outputfile (str)

        """
        # Append to the input
        if outputfile is None:
            for tier in trsoutput:
                trsinput.Append(tier)
            trsoutput  = trsinput
            outputfile = inputfilename

        # Save in a file
        annotationdata.io.write( outputfile,trsoutput )

    # ------------------------------------------------------------------------

    def get_phonestier(self, trsinput):
        """
        Return the tier with phonetization or None.

        """
        for tier in trsinput:
            if tier.GetName().lower().startswith("phon") is True:
                return tier

        for tier in trsinput:
            if "phon" in tier.GetName().lower():
                return tier

        return None

    # ------------------------------------------------------------------------

    def get_tokenstier(self, trsinputtok):
        """
        Return the tier with tokens, or None.

        In case of EOT, 2 tiers with tokens are available: std and faked.
        Priority is given to std.

        """
        toktier   = None # None tier with tokens
        stdtier   = None # index of stdtoken tier
        fakedtier = None # index of fakedtoken tier

        for tier in trsinputtok:
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

    def run(self, inputphonesname, inputtokensname, inputaudioname, outputfilename=None):
        """
        Execute SPPAS Alignment.

        @param inputphonesname is the file containing the phonetization
        @param inputtokensname is the file containing the tokenization
        @param outputfilename is the file name with the result (3 tiers)

        """
        if self.logfile:
            for k,v in self._options.items():
                self.logfile.print_message("Option: %s: %s"%(k,v), indent=2, status=INFO_ID)

        # Get the tiers to be time-aligned.
        trsinput = annotationdata.io.read( inputphonesname )
        phontier = self.get_phonestier( trsinput )
        if phontier is None:
            raise IOError(' Not a valid input file: no tier with phonetization was found.')

        try:
            trsinputtok = annotationdata.io.read( inputtokensname )
            toktier = self.get_tokenstier( trsinputtok )
            for tier in trsinputtok:
                trsinput.Append( tier )
        except Exception:
            toktier = None
            if self.logfile:
                self.logfile.print_message("Tokens alignment disabled: no tokenization available", indent=2, status=INFO_ID)

        # Processing...
        try:
            trsoutput = self.convert( phontier,toktier,inputaudioname )
        except Exception:
            import traceback
            print traceback.format_exc()
            raise

        # Save results
        try:
            if self.logfile:
                self.logfile.print_message("Save alignment of the units: ",indent=3)
            self.save( trsinput, inputphonesname, trsoutput, outputfilename )
            if self.logfile:
                self.logfile.print_message("", indent=4, status=OK_ID)

        except Exception:
            if self._options['clean'] is True:
                diralign, fileExt = os.path.splitext( self.inputaudio )
                shutil.rmtree( diralign )
            raise #IOError("align.py. Save. Error while saving file: " + str(e))

        # Clean!
        # if the audio file was converted.... remove the tmpaudio
        if self.inputaudio != inputaudioname:
            os.remove(self.inputaudio)
        if self._options['clean'] is True:
            diralign, fileExt = os.path.splitext( self.inputaudio )
            shutil.rmtree( diralign )

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def __convert_basic(self, diralign, trstier=None):
        """
        Perform segmentation without an audio file.

        """

        if self.logfile: self.logfile.print_message('Basic Align', indent=2)

        i = 0
        track = 1
        last = trstier.GetSize()

        while i < last:

            if self.logfile: self.logfile.print_message('Basic Align, unit number '+str(track), indent=3)

            # Set the current annotation values
            __ann   = trstier[i]
            __label = __ann.GetLabel().GetValue()

            # Save information
            if __ann.GetLabel().IsSilence():
                # Verify next annotations (concatenate all silences between 2 tracks)
                if (i + 1) < last:
                    __nextann = trstier[i + 1]
                    while (i + 1) < last and __nextann.GetLabel().IsSilence():
                        i = i + 1
                        if (i + 1) < last:
                            __nextann = trstier[i+1]

            else:
                try:
                    unitduration = __ann.GetLocation().GetEnd().GetMidpoint() - __ann.GetLocation().GetBegin().GetMidpoint()
                    phonname  = os.path.join(diralign, "track_%06d.phon"%track)
                    alignname = os.path.join(diralign, "track_%06d.palign"%track)
                    self.speechseg.exec_basic_alignment(unitduration, phonname, alignname)
                    if self.logfile:
                        self.logfile.print_message(" ", indent=3, status=OK_ID)
                except Exception as e:
                    if self.logfile:
                        self.logfile.print_message(str(e), indent=3, status=ERROR_ID)
                track = track + 1

            i = i + 1

    # ------------------------------------------------------------------------

    def rustine_others(self, trs):
        """ veritable rustine pour decaler la fin des non-phonemes. """
        tierphon   = trs.Find("PhonAlign")
        if tierphon is None:
            return trs

        imax = tierphon.GetSize() - 1
        for i, a in reversed(list(enumerate(tierphon))):
            if i < imax:
                nexta = tierphon[i+1]
                durnexta = nexta.GetLocation().GetDuration()

                if a.GetLabel().GetValue() == "sil" and durnexta > 0.04:
                    a.GetLocation().SetEndMidpoint( a.GetLocation().GetEndMidpoint() + 0.03 )

                if a.GetLabel().GetValue() in [ "gb", "@@", "fp", "dummy" ]:
                    a.GetLocation().SetEndMidpoint( a.GetLocation().GetEndMidpoint() + 0.02 )

                nexta.GetLocation().SetBeginMidpoint( a.GetLocation().GetEndMidpoint() )

        return trs

    def rustine_liaisons(self, trs):
        """ veritable rustine pour supprimer qqs liaisons en trop. """
        # Only for French!
        if "fra" not in self.speechseg._model: return trs

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
