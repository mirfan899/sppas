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
from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.utils.fileutils import setup_logging

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

# separators = ['#', '@@', 'euh', 'fp', 'gb', '##', '*', 'dummy']
separators = ['#', 'sil']


# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------


def unalign(aligned_tier):
    """ Convert a time-aligner tier into a non-aligned tier.

    :param aligned_tier: (Tier)
    :returns: (Tier)
    
    """
    new_tier = Tier("Un-aligned")
    b = aligned_tier.GetBegin()
    e = b
    l = ""
    for a in aligned_tier:
        if a.GetLabel().IsSilence() is True or a.GetLabel().GetValue() in separators:
            if len(l) > 0 and e > b:
                at = Annotation(TimeInterval(b, e), Label(l))
                new_tier.Add(at)
                new_tier.Add(a)
            b = a.GetLocation().GetEnd()
            e = b
            l = ""
        else:
            e = a.GetLocation().GetEnd()
            label = a.GetLabel().GetValue()
            label = label.replace('.', ' ')
            if a.GetLabel().IsEmpty() is False:
                l = l + " " + label

    if e > b:
        a = aligned_tier[-1]
        label = a.GetLabel().GetValue()
        label = label.replace('.', ' ')
        at = Annotation(TimeInterval(b, e), Label(label))
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

# ----------------------------------------------------------------------------
# Transform the PhonAlign tier to a Phonetization tier

align_tier = trs_input.Find("PhonAlign", case_sensitive=False)
phon_tier = None
if align_tier is None:
    logging.info("PhonAlign tier found.")
    phon_tier = unalign(align_tier)
    phon_tier.SetName("Phonetization")
else:
    logging.info("PhonAlign tier not found.")

# ----------------------------------------------------------------------------
# Transform the TokensAlign tier to a Tokenization tier

align_tier = trs_input.Find("TokensAlign", case_sensitive=False)
token_tier = None
if align_tier is not None:
    logging.info("TokensAlign tier found.")
    token_tier = unalign(align_tier)
    token_tier.SetName("Tokenization")
else:
    logging.info("TokensAlign tier not found.")

# ----------------------------------------------------------------------------
# Write

trs_out = Transcription()
if phon_tier:
    trs_out.Add(phon_tier)
if token_tier:
    trs_out.Add(token_tier)
if len(trs_out) > 0:
    sppas.src.annotationdata.aio.write(args.o, trs_out)
else:
    logging.info("No tier converted.")
    sys.exit(1)
