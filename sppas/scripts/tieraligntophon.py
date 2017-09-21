#!/usr/bin/env python2
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

    scripts.tieraligntophon.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to a time-aligned phonemes tier to its phonetization tier.

"""
import sys
import os.path
import logging
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.annotationdata.aio
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotations.searchtier import sppasSearchTier
from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.utils.fileutils import setup_logging

# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------


def unalign(aligned_tier, ipus_separators=['#', 'dummy']):
    """ Convert a time-aligned tier into a non-aligned tier.

    :param aligned_tier: (Tier)
    :param ipus_separators: (list)
    :returns: (Tier)
    
    """
    new_tier = Tier("Un-aligned")
    b = aligned_tier.GetBegin()
    e = b
    l = ""
    for a in aligned_tier:
        label = a.GetLabel().GetValue()
        if label in ipus_separators or a.GetLabel().IsEmpty() is True:
            if e > b:
                at = Annotation(TimeInterval(b, e), Label(l))
                new_tier.Add(at)
            new_tier.Add(a)
            b = a.GetLocation().GetEnd()
            e = b
            l = ""
        else:
            e = a.GetLocation().GetEnd()
            label = label.replace('.', ' ')
            l += " " + label

    if e > b:
        a = aligned_tier[-1]
        e = a.GetLocation().GetEnd()
        at = Annotation(TimeInterval(b, e), Label(l))
        new_tier.Add(at)

    return new_tier
    
    
# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM),
                        description="... a script to convert time-aligned phonemes into their phonetization.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output file name')

parser.add_argument("--tok",
                    action='store_true',
                    help="Convert time-aligned tokens into their tokenization.")

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

if not args.quiet:
    setup_logging(1, None)
else:
    setup_logging(None, None)

# ----------------------------------------------------------------------------
# Read

trs_input = sppas.src.annotationdata.aio.read(args.i)
trs_out = Transcription()

# ----------------------------------------------------------------------------
# Transform the PhonAlign tier to a Phonetization tier

try:
    align_tier = sppasSearchTier.aligned_phones(trs_input)
    logging.info("PhonAlign tier found.")
    phon_tier = unalign(align_tier)
    phon_tier.SetName("Phonetization")
    trs_out.Add(phon_tier)
except IOError:
    logging.info("PhonAlign tier not found.")

# ----------------------------------------------------------------------------
# Transform the TokensAlign tier to a Tokenization tier

if args.tok:
    try:
        align_tier = sppasSearchTier.aligned_tokens(trs_input)
        logging.info("TokensAlign tier found.")
        token_tier = unalign(align_tier)
        token_tier.SetName("Tokenization")
        trs_out.Add(token_tier)
    except IOError:
        logging.info("TokensAlign tier not found.")

# ----------------------------------------------------------------------------
# Write

if len(trs_out) > 0:
    sppas.src.annotationdata.aio.write(args.o, trs_out)
else:
    logging.info("No tier converted.")
    sys.exit(1)
