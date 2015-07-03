#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# File: tok.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import os.path

from tokenize import DictTok

from resources.wordslst import WordsList
from resources.dictrepl import DictRepl

from annotationdata.transcription import Transcription
from annotationdata.tier import Tier
from annotationdata.annotation import Annotation
from annotationdata.label.label import Label
import annotationdata.io

from sp_glob import RESOURCES_PATH


# ---------------------------------------------------------------------------
# sppasTok main class
# ---------------------------------------------------------------------------


class sppasTok(object):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Tokenization automatic annotation.

    Tokenization is a text normalization task.

    For details, read the following reference:
        - Brigitte Bigi (2011).
        - A Multilingual Text Normalization Approach.
        - 2nd Less-Resourced Languages workshop,
        - 5th Language & Technology Conference, Poznan (Poland).

    """

    def __init__(self, vocab, lang="und", logfile=None):
        """
        Create a new sppasTok instance.

        @param vocab (string) is the file name with the list of words,
        @param lang (string) is the language code.

        """
        try:
            pvoc = WordsList(vocab)
        except Exception as e:
            raise Exception("Load words list file failed: %s" % e)

        self.tokenizer = DictTok(pvoc, lang)

        try:
            repl = DictRepl(os.path.join(RESOURCES_PATH, "repl", self.lang + ".repl"), nodump=True)
            self.tokenizer.set_repl( repl )
        except Exception:
            pass

        try:
            punct = WordsList(os.path.join(RESOURCES_PATH, "vocab", "Punctuations.txt"), nodump=True)
            self.tokenizer.set_punct( punct )
        except Exception:
            pass

        self.std = True
        self.logfile = logfile

    # End __init__
    # ------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------


    def fix_options(self, options):
        """
        Fix all options.

        Available options are:
            - std

        @param options (option)

        """

        for opt in options:

            key = opt.get_key()

            if key == "std":
                self.set_std(opt.get_value())

            else:
                raise Exception('Unknown key option: %s'%key)

    # End fix_options
    # -----------------------------------------------------------------------


    def set_std(self, std):
        """
        Fix the std option.
        If std is set to True, a standard tokenization is created.

        @param std (Boolean)

        """
        self.std = std

    # End set_std
    # ----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Methods to tokenize series of data
    # -----------------------------------------------------------------------


    def convert(self, tier):
        """
        Tokenize labels of a tier.

        @param tier (Tier) contains the orthographic transcription

        @return A tuple with 2 tiers named "Tokens-Std" and "Tokens-Faked"

        """
        if tier.IsEmpty() is True:
            raise Exception('convert. Error: Empty input tier.\n')

        if self.std:
            tokensFaked = Tier("Tokens-Faked")
            tokensStd   = Tier("Tokens-Std")
        else:
            tokensFaked = Tier("Tokens")
            tokensStd=None

        for a in tier:
            # Do not tokenize an empty label
            if a.GetLabel().IsEmpty():
                _labelf = Label()
                if self.std:
                    _labels = Label()
            # Do not tokenize silences
            elif a.GetLabel().IsSilence():
                _labelf = Label(a.GetLabel().GetValue())
                if self.std:
                    _labels = Label(a.GetLabel().GetValue())
            else:
                try:
                    _labelf = Label(self.tokenizer.tokenize( a.GetLabel().GetValue(), std=False ))
                    if self.std:
                        _labels = Label(self.tokenizer.tokenize( a.GetLabel().GetValue(), std=True ))
                except Exception as e:
                    raise Exception('convert. tokenize error in interval: '+str(a)+'. Error: '+str(e)+'\n')

            try:
                b = Annotation(a.GetLocation().Copy(), _labelf)
                tokensFaked.Append(b)
                if self.std:
                    c = Annotation(a.GetLocation().Copy(), _labels)
                    tokensStd.Append(c)
            except Exception as e:
                raise Exception('convert. Tier insertion error: '+str(e)+'\n')

        return (tokensFaked, tokensStd)

    # End convert
    # ------------------------------------------------------------------------


    def align_tiers(self, stdtier, fakedtier):
        """
        Align standard spelling tokens with faked spelling tokens.

        @param stdtier (Tier)
        @param fakedtier (Tier)

        """
        if self.std is False:
            return

        for std, faked in zip(stdtier, fakedtier):
            try:
                s, f = self.__align_tiers(std.GetLabel().GetValue(), faked.GetLabel().GetValue())
            except Exception:
                if self.logfile:
                    self.logfile.print_message(u"StdTokens and FakedTokens matching error, at %s\n"%std.GetLocation().GetValue(),indent=2,status=1)
                    self.logfile.print_message(std.GetLabel().GetValue(),  indent=3)
                    self.logfile.print_message(faked.GetLabel().GetValue(),indent=3)
                    self.logfile.print_message(u"Fall back on faked: %s" %self.fallback, indent=3,status=3)
                    std.GetLabel().SetValue( faked.GetLabel().GetValue() )

                continue

            std.GetLabel().SetValue( s )
            faked.GetLabel().SetValue( f )

    # End align_tiers
    # ------------------------------------------------------------------------


    def __align_tiers(self, std, faked):
        """
        Align standard spelling tokens with faked spelling tokens.

        @param std (string)
        @param faked (string)
        @return a tuple of std and faked
        """
        stds = std.split()
        fakeds = faked.split()
        if len(stds) == len(fakeds):
            return (std, faked)

        tmp = []
        for f in fakeds:
            toks = f.split('_')
            for t in toks:
                tmp.append(t)
        fakeds = tmp[:]

        num_tokens = len(stds)
        i = 0
        while i < num_tokens:
            if "'" in stds[i]:
                if not stds[i].endswith("'") and fakeds[i].endswith("'"):
                    fakeds[i] = fakeds[i] + fakeds[i+1]
                    del fakeds[i+1]

            if "-" in stds[i]:
                if not stds[i].endswith("-") and "-" not in fakeds[i]:

                    fakeds[i] = fakeds[i] + fakeds[i+1]
                    del fakeds[i+1]

            num_underscores = stds[i].count('_')
            if num_underscores > 0:
                if not self.tokenizer.vocab.is_unk(stds[i]):
                    n = num_underscores + 1
                    fakeds[i] = "_".join(fakeds[i:i+n])
                    del fakeds[i+1:i+n]

            i = i + 1

        if len(stds) != len(fakeds):
            raise Exception('Standard and Faked alignment Error: %s\n'
                            '                 %s' % (std, faked))

        return (std, " ".join(fakeds))

    # End __align_tiers
    # ------------------------------------------------------------------------


    def save(self, trsinput, inputfilename, trsoutput, outputfile=None):
        """
        Save depending on the given data.

        If no output file name is given, trsoutput is appended to the input
        transcription.

        @param trsinput (Transcription)
        @param inputfilename (String)
        @param trsoutput (Transcription)
        @param outputfile (String)

        """

        # Append to the input
        if outputfile is None:
            for tier in trsoutput:
                trsinput.Append(tier)
            trsoutput  = trsinput
            outputfile = inputfilename

        # Save in a file
        annotationdata.io.write( outputfile,trsoutput )

    # End save
    # ------------------------------------------------------------------------


    def run( self, inputfilename, outputfile=None ):
        """
        Run the Tokenization process on an input file.

        @param inputfilename is the input file name
        @param outputfile is the output file name of the tokenization

        """
        # Get input tier to tokenize
        transtier = -1 # First tier
        trsinput  = annotationdata.io.read(inputfilename)
        tierinput = None

        for tier in trsinput:
            tiername = tier.GetName().lower()
            if "trs" in tiername:
                tierinput = tier
                break
            elif "trans" in tiername:
                tierinput = tier
                break
            elif "ipu" in tiername:
                tierinput = tier
                break
            elif "ortho" in tiername:
                tierinput = tier
            elif "toe" in tiername:
                tierinput = tier
                break
                break

        if tierinput is None:
            raise Exception("Transcription tier not found. "
                            "Tier name must contain "
                            "'trans' or 'trs' or 'ipu' 'ortho' or 'toe'.")

        tierinput = trsinput[transtier]

        # Tokenize the tier
        tiertokens, tierStokens = self.convert( tierinput )

        # Align Faked and Standard
        if tierStokens is not None:
            self.align_tiers(tierStokens, tiertokens)

        # Save
        trsoutput = Transcription()
        trsoutput.Add( tiertokens )
        if tierStokens is not None:
            trsoutput.Add( tierStokens )

        self.save(trsinput, inputfilename, trsoutput, outputfile)

    # End run
    # ------------------------------------------------------------------------

# End sppasTok
# ---------------------------------------------------------------------------
