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
# File: repetition.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os

from annotationdata.transcription import Transcription
from annotationdata.tier import Tier
from annotationdata.annotation import Annotation
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.label.label import Label
import annotationdata.io
import annotations.log
from dictlem import LemmaDict
from resources.wordslst import WordsList
from resources.unigram import Unigram
from detectrepetition import Repetitions
from detectrepetition import DataSpeaker


DEBUG=False

# ######################################################################### #


class sppasRepetition( ):
    """
    SPPAS Automatic Repetition Detection
    (either self-repetitions or other-repetitions).

    This annotation is performed on the basis of aligned-tokens.
    The tokens can be lemmatized from a dictionary.

    The output is made of 2 tiers including intervals with
    sources and echos.

    How to use sppasRepetition?

    >>> p = sppasRepetition( dictpath, lang )
    >>> p.run(inputtrsname, outputfilename)

    """


    def __init__(self, resourcefile, logfile=None):
        """
        Create a new sppasRepetition instance.

        @param resourcefile is either the lemma dictionary or the list of stop-words.

        Attention: the extention of the resource file name is very important:
        must be ".stp" for stop-words and ".lem" for lemmas (case-sensitive)!

        """

        # Members
        self._merge         = False  # Merge input in the output
        self._use_lemmatize = True   # Lemmatize the input
        self._use_stopwords = True   # Add specific stopwords of the input
        self._empan  = 5             # Detection length (nb of IPUs; 1=current IPU)
        self._alpha  = 0.5           # Specific stop-words threshold coefficient
        self.logfile = logfile
        self.lemmatizer = None
        self.stopwords  = None

        # Create the lemmatizer instance
        try:
            lemmafile = resourcefile.replace(".stp", ".lem")
            self.lemmatizer = LemmaDict(lemmafile)
        except Exception:
            self._use_lemmatize = False

        if (self._use_lemmatize is True and self.lemmatizer.get_size() == 0) or self._use_lemmatize is False:
            if logfile is not None:
                logfile.print_message("Lemmatization disabled.",indent=2,status=3)
            else:
                print " ... ... [ INFO ] Lemmatization disabled."
            self._use_lemmatize = False

        # Create the list of stop words (list of non-relevant words)
        try:
            stopfile = resourcefile.replace(".lem", ".stp")
            self.stopwords = WordsList(filename=resourcefile, nodump=True)
            if self.stopwords.get_size() == 0:
                self._use_stopwords = False
        except Exception:
            self.stopwords = WordsList()

        #if (self._use_stopwords is True and self.stopwords.get_size() == 0) or self._use_stopwords is False:
        if self._use_stopwords is False:
            if logfile is not None:
                logfile.print_message("StopWords disabled.",indent=2,status=3)
            else:
                print " ... ... [ INFO ] StopWords disabled."
            #self._use_stopwords = False

    # End __init__
    # ------------------------------------------------------------------


    def fix_options(self, options):
        for opt in options:
            if "merge" == opt.get_key():
                self.set_merge( opt.get_value() )
            elif "stopwords" == opt.get_key():
                self.set_use_stopwords( opt.get_value() )
            elif "lemmatize" == opt.get_key():
                self.set_use_lemmatize( opt.get_value() )
            elif "empan" == opt.get_key():
                self.set_empan( opt.get_value() )
            elif "alpha" == opt.get_key():
                self.set_alpha( opt.get_value() )

    # End fix_options
    # ------------------------------------------------------------------


    # ###################################################################### #
    # Getters and Setters                                                    #
    # ###################################################################### #


    def set_merge(self, merge):
        """
        Fix the merge option.
        If merge is set to True, sppasRepetition() will save the input tiers
        in the output file.

        @param merge (Boolean)

        """
        self._merge = merge

    # End set_merge
    # ----------------------------------------------------------------------


    def set_use_lemmatize(self, use_lemmatize):
        """
        Fix the use_lemmatize option.

        If use_lemmatize is set to True, sppasRepetition() will lemmatize the
        input before the repetition automatic detection.

        @param use_lemmatize (Boolean)

        """
        self._use_lemmatize = use_lemmatize

    # End set_use_lemmatize
    # ----------------------------------------------------------------------


    def set_use_stopwords(self, use_stopwords):
        """
        Fix the use_stopwords option.

        If use_stopwords is set to True, sppasRepetition() will add specific
        stopwords to the stopwords list (deducted from the input text).

        @param use_stopwords (Boolean)

        """
        self._use_stopwords = use_stopwords

    # End set_use_stopwords
    # ----------------------------------------------------------------------


    def set_empan(self, empan):
        """
        Fix the empan option.

        @param empan (int)

        """
        self._empan = empan

    # End set_empan
    # ----------------------------------------------------------------------


    def set_alpha(self, alpha):
        """
        Fix the alpha option.

        @param alpha (int or float)

        """
        self._alpha = alpha

    # End set_alpha
    # ----------------------------------------------------------------------


    # ###################################################################### #
    # Automatic Detection search parameters                                  #
    # ###################################################################### #


    def lemmatize(self, inputtier):
        """
        Lemmatize a tier.

        @param inputtier (Tier)

        """
        if self._use_lemmatize is False:
            return

        lemmatier = inputtier.Copy()

        for i in range(lemmatier.GetSize()):
            lem = self.lemmatizer.get_lem( lemmatier[i].GetLabel().GetValue() )
            lemmatier[i].GetLabel().SetValue( lem )

        return lemmatier

    # ------------------------------------------------------------------


    def relevancy(self, inputtier):
        """
        Add very frequent tokens in a copy of the stopwords list.
        Return a WordsList instance

        Estimate the relevance of each term by using the number of
        occurrences of this term in the input and compare this value
        to a threshold, to add the term (or not) in the stopwords list.

        @param inputtier (Tier)

        """
        l = self.stopwords.copy()

        # Create the Unigram and put data
        u = Unigram()
        for a in inputtier:
            if a.GetLabel().IsSpeech() is True:
                u.add( a.GetLabel().GetValue() )

        # Estimate if a token is relevant, put in the stoplist
        for token in u.get_tokens():
            freq  = u.get_count(token)
            proba = float(freq) / float(u.get_sum())
            relevant = 1.0 / (float(u.get_size())*float(self._alpha))
            if proba > relevant:
                l.add( token )
                if self.logfile is not None:
                    self.logfile.print_message('Add in the stoplist: '+token, indent=3)
                elif DEBUG is True:
                    print(' ... ... ... Add in the stoplist: '+token.encode('utf8'))

        return l

    # End relevancy
    # ------------------------------------------------------------------


    def find_next_break (self, inputtier, start, empan):
        """
        Return the index of the next interval representing a break.
        This depends on the 'empan' value.

        @param start is the position of the token where the search will start

        """
        nbbreaks = 0
        for i in range (start, inputtier.GetSize()):
            if inputtier[i].GetLabel().IsSilence():
                nbbreaks = nbbreaks + 1
                if nbbreaks == empan:
                    return i
        return inputtier.GetSize() - 1

    # End find_next_break
    # ------------------------------------------------------------------


    # ###################################################################### #
    # Automatic Detection search                                             #
    # ###################################################################### #


    def _addrepetition(self, repeatobj, nbrepeats, inputtier1, inputtier2, tokstartsrc, tokstartrep, srctier, reptier):
        """
        Add sources and repetitions
        from repeatobj
        to the tiers.
        """

        n = 0
        for i in range(repeatobj.get_repeats_size()):

            # Source
            s,e = repeatobj.get_repeat_source(i)
            srcbegin = inputtier1[tokstartsrc+s].GetLocation().GetBegin()
            srcend   = inputtier1[tokstartsrc+e].GetLocation().GetEnd()
            time = TimeInterval(srcbegin.Copy(), srcend.Copy())
            srcann = Annotation(time, Label("S"+str(nbrepeats+n)))
            try:
                srctier.Add(srcann)
                if DEBUG:
                    print "src annotation added: ",srcann
            except Exception:
                continue

            # Repetition
            rep = repeatobj.get_repeat_repetition(i)
            for r in rep:
                (s,e) = r
                repbegin = inputtier2[tokstartrep+s].GetLocation().GetBegin()
                repend   = inputtier2[tokstartrep+e].GetLocation().GetEnd()
                r = reptier.Lindex(repbegin) #time)
                l = reptier.Rindex(repend) #time)

                # all other cases (no repetition, overlap)
                time = TimeInterval( repbegin.Copy(), repend.Copy() )
                repann = Annotation(time, Label("R"+str(nbrepeats+n)))
                reptier.Add(repann)
                if DEBUG:
                    print "rep annotation added: ",repann

            n = n + 1
        # end for

        return n



    def selfdetection(self, inputtier1):
        """
        Self-Repetition detection.

        @param inputtier1 (Tier)

        """
        # Verifications: is there any data?
        if inputtier1.IsEmpty() is True:
            raise Exception("Repetition. Empty input tokens tier.\n")

        # Update the stoplist
        if self._use_stopwords is True:
            stpw = self.relevancy( inputtier1 )
        else:
            stpw = self.stopwords

        # Create repeat objects
        repeatobj = Repetitions( )

        # Create output data
        srctier = Tier("Sources")
        reptier = Tier("Repetitions")
        nbrepeats = 1

        # Initialization of tokstart and tokend
        tokstart = 0
        if inputtier1[0].GetLabel().IsDummy():
            tokstart = 1
        toksearch = self.find_next_break( inputtier1, tokstart+1 , empan=1)
        tokend    = self.find_next_break( inputtier1, tokstart+1 , empan=self._empan)

        # Detection is here:
        while tokstart < tokend:

            # Build an array with the tokens
            tokens1 = list()
            for i in range(tokstart, tokend+1):
                tokens1.append( inputtier1[i].GetLabel().GetValue() )
            speaker1 = DataSpeaker( tokens1, stpw )

            # Detect repeats in these data
            repeatobj.detect( speaker1, toksearch-tokstart, None )

            # Save repeats
            if repeatobj.get_repeats_size()>0:
                n = self._addrepetition(repeatobj, nbrepeats, inputtier1, inputtier1, tokstart, tokstart, srctier, reptier)
                nbrepeats = nbrepeats + n

            # Prepare next search
            tokstart  = toksearch
            toksearch = self.find_next_break( inputtier1 , tokstart+1 , empan=1 )
            tokend    = self.find_next_break( inputtier1 , tokstart+1 , empan=self._empan )

        return (srctier,reptier)

    # End selfdetection
    # ------------------------------------------------------------------------


    def otherdetection(self, inputtier1, inputtier2):
        """
        Other-Repetition detection.

        @param inputtier (Tier)

        """
        # Verifications: is there any data?
        if inputtier1.IsEmpty() is True:
            raise Exception("Repetition. Empty input tokens tier.\n")

        # Update the stoplist
        if self._use_stopwords is True:
            # other-repetition: relevance of the echoing-speaker
            stpw = self.relevancy( inputtier2 )
        else:
            stpw = self.stopwords

        # Create repeat objects
        repeatobj = Repetitions( )

        # Create output data
        srctier = Tier("OR-Source")
        reptier = Tier("OR-Repetition")

        nbrepeats = 1

        # Initialization of tokstart, and tokend
        tokstartsrc = 0
        if inputtier1[0].GetLabel().IsDummy():
            tokstartsrc = 1
        tokendsrc = min(20, inputtier1.GetSize()-1)

        # Detection is here:
        # detect() is applied work by word, from tokstart to tokend
        while tokstartsrc < tokendsrc:

            # Build an array with the tokens
            tokens1 = list()
            for i in range(tokstartsrc, tokendsrc):
                tokens1.append( inputtier1[i].GetLabel().GetValue() )
            speaker1 = DataSpeaker( tokens1, stpw )

            # Create speaker2
            tokens2 = list()
            nbbreaks = 0
            tokstartrep = -1
            a = inputtier1[tokstartsrc]

            for (r,b) in enumerate(inputtier2):
                if b.GetLocation().GetBeginMidpoint() >= a.GetLocation().GetBeginMidpoint():
                    if tokstartrep == -1:
                        tokstartrep = r
                    if b.GetLabel().IsSilence():
                        nbbreaks = nbbreaks + 1
                    if nbbreaks == self._empan:
                        break
                    tokens2.append( b.GetLabel().GetValue() )
            speaker2 = DataSpeaker( tokens2, stpw )

            if DEBUG is True:
                print "SRC : ",speaker1
                print "ECHO: ",speaker2

            # Detect repeats in these data: search if the first token of spk1
            # is the first token of a source.
            repeatobj.detect( speaker1, 1, speaker2 )

            # Save repeats
            shift = 1
            if repeatobj.get_repeats_size()>0:
                if DEBUG is True:
                    print " ----> found : "
                    repeatobj.get_repeat(0).print_echo()
                s,e = repeatobj.get_repeat_source(0)
                n = self._addrepetition(repeatobj, nbrepeats, inputtier1, inputtier2, tokstartsrc, tokstartrep, srctier, reptier)
                if n > 0:
                    nbrepeats = nbrepeats + n
                shift = e + 1


            while speaker1.is_token(speaker1.get_token(shift)) is False and shift < 20:
                shift = shift + 1

            tokstartsrc = tokstartsrc + shift
            tokstartsrc = min(tokstartsrc, inputtier1.GetSize()-1)
            tokendsrc   = min(tokstartsrc + 20, inputtier1.GetSize()-1)

        return (srctier,reptier)

    # End otherdetection
    # ------------------------------------------------------------------------


    # ###################################################################### #
    # Run
    # ###################################################################### #


    def run(self, inputfilename1, inputfilename2=None, outputfilename=None):
        """
        Run the Repetition Automatic Detection annotation.

        @param inputfilename
        @param outputfilename

        """
        tokentier1 = None  # First tier
        tokentier2 = -1    # No echoing speaker
        try:
            # Find the token tier
            trsinput1 = annotationdata.io.read( inputfilename1 )
            for i in range( trsinput1.GetSize() ):
                if "token" in trsinput1[i].GetName().lower() and "align" in trsinput1[i].GetName().lower():
                    tokentier1 = i
                    break
            if inputfilename2 is not None:
                #find the token tier
                trsinput2 = annotationdata.io.read( inputfilename2 )
                for i in range( trsinput2.GetSize() ):
                    if "token" in trsinput2[i].GetName().lower() and "align" in trsinput2[i].GetName().lower():
                        tokentier2 = i
                        break
        except Exception as e:
            raise Exception('Repetitions. '+str(e))

        if tokentier1 is None:
            raise Exception('Repetitions. No valid input tier (expected: TokensAlign).')

        # Lemmatize input?
        if self._use_lemmatize is True and self.lemmatizer:
            tier1 = self.lemmatize( trsinput1[tokentier1] )
            if tokentier2 > -1:
                tier2 = self.lemmatize( trsinput2[tokentier2] )
        else:
            tier1 = trsinput1[tokentier1]
            if tokentier2 > -1:
                tier2 = trsinput2[tokentier2]

        if self.logfile is not None:
            self.logfile.print_message("Empan = "+str(self._empan), indent=3)
            self.logfile.print_message("Alpha = "+str(self._alpha), indent=3)

        # Repetition Automatic Detection
        if tokentier2 == -1:
            (srctier,reptier) = self.selfdetection( tier1 )
        else:
            (srctier,reptier) = self.otherdetection( tier1 , tier2 )

        # Manage results:
        # An output file name is given
        if outputfilename:
            trsoutput = Transcription("Repetitions")
            if self._merge is True:
                for i in range( trsinput1.GetSize() ):
                    trsoutput.Add( trsinput1[i] )
        # the repeat tier is added to the input transcription
        else:
            outputfilename = inputfilename1
            trsoutput = annotationdata.io.read( inputfilename1 )

        # Add repeats to this trsoutput
        trsoutput.Append( srctier )
        trsoutput.Append( reptier )

        trsoutput.SetMinTime( trsinput1.GetMinTime() )
        trsoutput.SetMaxTime( trsinput1.GetMaxTime() ) # hum, in case of OR... not sure! to be verified.

        # Save
        annotationdata.io.write( outputfilename, trsoutput )

    # End run
    # ------------------------------------------------------------------------
