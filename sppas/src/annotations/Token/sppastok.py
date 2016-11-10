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
# File: tok.py
# ---------------------------------------------------------------------------

import os.path

from tokenize import DictTok

from resources.wordslst import WordsList
from resources.dictrepl import DictRepl

from annotationdata.transcription import Transcription
from annotationdata.tier          import Tier
from annotationdata.annotation    import Annotation
from annotationdata.label.label   import Label
import annotationdata.io

from sp_glob import ERROR_ID, WARNING_ID, OK_ID, INFO_ID
from sp_glob import RESOURCES_PATH

from annotations.sppasbase import sppasBase

# ---------------------------------------------------------------------------
# sppasTok main class
# ---------------------------------------------------------------------------

class sppasTok( sppasBase ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Tokenization automatic annotation.

    Tokenization is a text normalization task.

    For details, read the following reference:
        - Brigitte Bigi (2011).
        - A Multilingual Text Normalization Approach.
        - 2nd Less-Resourced Languages workshop,
        - 5th Language & Technology Conference, Poznan (Poland).

    """
    def __init__(self, vocab, lang="und", logfile=None):
        """
        Create a sppasTok instance.

        @param vocab (str - IN) the file name with the orthographic transcription
        @param lang (str - IN) the language code
        @param logfile (sppasLog)

        """
        sppasBase.__init__(self, logfile)

        self.fix_tokenizer( vocab,lang )

        # List of options to configure this automatic annotation
        self._options['std'] = False

    # -----------------------------------------------------------------------

    def fix_tokenizer(self, vocab, lang):
        """
        Fix the tokenizer.

        @param vocab (str - IN) the file name with the orthographic transcription
        @param lang (str - IN) the language code

        """
        pvoc = WordsList(vocab)
        self.tokenizer = DictTok(pvoc, lang)

        try:
            repl = DictRepl(os.path.join(RESOURCES_PATH, "repl", lang + ".repl"), nodump=True)
            self.tokenizer.set_repl( repl )
        except Exception:
            pass

        try:
            punct = WordsList(os.path.join(RESOURCES_PATH, "vocab", "Punctuations.txt"), nodump=True)
            self.tokenizer.set_punct( punct )
        except Exception:
            pass

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

    # -----------------------------------------------------------------------

    def set_std(self, std):
        """
        Fix the std option.

        @param std (bool - IN) If std is set to True, a standard tokenization
        is created.

        """
        self._options['std'] = std

    # -----------------------------------------------------------------------
    # Methods to tokenize series of data
    # -----------------------------------------------------------------------

    def convert(self, tier):
        """
        Tokenization of all labels of a tier.

        @param tier (Tier - IN) contains the orthographic transcription
        @return A tuple with 2 tiers named "Tokens-Std" and "Tokens-Faked"

        """
        if tier.IsEmpty() is True:
            raise IOError("Empty input tier %s.\n"%tier.GetName())

        tokensStd = None
        if self._options['std'] is True:
            tokensStd = self.__convert(tier, True)
        tokensFaked = self.__convert(tier, False)

        return (tokensFaked, tokensStd)

    # ------------------------------------------------------------------------

    def align_tiers(self, stdtier, fakedtier):
        """
        Force standard spelling and faked spelling to share the same number of tokens.

        @param stdtier (Tier - IN)
        @param fakedtier (Tier - IN)

        """
        if self._options['std'] is False:
            return

        for astd, afaked in zip(stdtier, fakedtier):

                for textstd,textfaked in zip(astd.GetLabel().GetLabels(),afaked.GetLabel().GetLabels()):

                    try:
                        texts, textf = self.__align_tiers(textstd.GetValue(), textfaked.GetValue())
                        textstd.SetValue( texts )
                        textfaked.SetValue( textf )

                    except Exception:
                        self.print_message(u"StdTokens and FakedTokens matching error, at %s\n"%astd.GetLocation().GetValue(),indent=2,status=1)
                        self.print_message(astd.GetLabel().GetValue(),  indent=3)
                        self.print_message(afaked.GetLabel().GetValue(),indent=3)
                        self.print_message(u"Fall back on faked.",indent=3,status=3)
                        textstd.SetValue( textf )

    # ------------------------------------------------------------------------

    def get_transtier(self, inputfilename):
        """
        Return the tier with transcription, or None.

        """
        trsinput  = annotationdata.io.read(inputfilename)
        tierinput = None

        for tier in trsinput:
            tiername = tier.GetName().lower()
            if "transcription" in tiername:
                tierinput = tier
                break

        if tierinput is None:
            for tier in trsinput:
                print
                print tier.GetName()
                print
                tiername = tier.GetName().lower()
                if "trans" in tiername:
                    tierinput = tier
                    break
                elif "trs" in tiername:
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

        return tierinput

    # ------------------------------------------------------------------------

    def run( self, inputfilename, outputfilename ):
        """
        Run the Tokenization process on an input file.

        @param inputfilename (str - IN) the input file name of the transcription
        @param outputfilename (str - IN) the output file name of the tokenization

        """
        self.print_options()
        self.print_diagnosis( inputfilename )

        # Get input tier to tokenize
        tierinput = self.get_transtier(inputfilename)
        if tierinput is None:
            raise IOError("Transcription tier not found. "
                          "Tier name must contain "
                          "'trans' or 'trs' or 'ipu' 'ortho' or 'toe'.")

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

        # Save in a file
        annotationdata.io.write( outputfilename,trsoutput )


    # ------------------------------------------------------------------------
    # Private: some workers...
    # ------------------------------------------------------------------------

    def __convert(self, tier, std):
        """
        Tokenize all labels of an annotation, not only the one with the best score.

        """
        tiername = "Tokenization-Standard" if std is True else "Tokenization"
        tokens = Tier( tiername )
        for a in tier:

            af = a.Copy()
            for text in af.GetLabel().GetLabels():
                # Do not tokenize an empty label, noises, laughter...
                if text.IsSpeech() is True:
                    tokenized = self.tokenizer.tokenize( text.GetValue(), std=std )
                    text.SetValue( tokenized )
            tokens.Append( af )

        return tokens

    # -----------------------------------------------------------------------

    def __align_tiers(self, std, faked):
        """
        Align standard spelling tokens with faked spelling tokens.

        @param std (string)
        @param faked (string)
        @return a tuple of std and faked

        """
        stds   = std.split()
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

# ---------------------------------------------------------------------------
