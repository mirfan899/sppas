#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2017  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# this program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# this program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# phonemesmapping.py
# ---------------------------------------------------------------------------

import sys
import os
import codecs
from argparse import ArgumentParser
from collections import OrderedDict

PROGRAM = os.path.abspath(__file__)
SPPAS = os.getenv('SPPAS')
if SPPAS is None:
    SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))

if os.path.exists(SPPAS) is False:
    print "ERROR: SPPAS not found."
    sys.exit(1)

SPPASSRC = os.path.join(SPPAS, "sppas", "src")
sys.path.append(SPPASSRC)

import annotationdata.io
from presenters.tiermapping import TierMapping
from annotationdata.transcription import Transcription
from sp_glob import encoding

reload(sys)
sys.setdefaultencoding(encoding)

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -m table" %
                        os.path.basename(PROGRAM),
                        description="... a program to classify phonemes.")
parser.add_argument("-i", metavar="file", required=True,  help='Input annotated file name.')
parser.add_argument("-m", metavar="file", required=True,  help='Mapping table file name.')
parser.add_argument("-s", metavar="symbol", required=False, default="*", help='Symbol for unknown phonemes (default:*).')
parser.add_argument("--quiet", action='store_true', help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Load input data

fname, fext = os.path.splitext(args.i)
if fname.endswith("-palign") is False:
    print "ERROR: this plugin requires SPPAS alignment files (i.e. with -palign in its name)."
    sys.exit(1)

# read content
trs_input = annotationdata.io.read(args.i)
tier = trs_input.Find("PhonAlign", case_sensitive=False)
if tier is None:
    print "A tier with name PhonAlign is required."
    sys.exit(1)

# read the table
if not args.quiet: print "Loading..."
mappings = OrderedDict()
with codecs.open(args.m, "r", encoding) as fp:
    firstline = fp.readline()
    tiernames = firstline.split(";")
    tiernames.pop(0)
    for name in tiernames:
        mapping = TierMapping()
        mapping.set_reverse(False)     # from PhonAlign to articulatory direction
        mapping.set_keep_miss(False)   # keep unknown entries as given
        mapping.set_miss_symbol(args.s)   # mapping symbol in case of unknown entry
        mapping.set_delimiters([])  #
        mappings[name] = mapping

    for line in fp.readlines():
        phones = line.split(";")
        phoneme = phones[0]
        phones.pop(0)
        if not args.quiet:
            if len(phones) != len(mappings):
                sys.stdout.write("%s (ignored) " % phoneme.encode('utf8'))
            else:
                sys.stdout.write("%s " % phoneme.encode('utf8'))

        for name, value in zip(tiernames, phones):
            mappings[name].add(phoneme, value)

if not args.quiet: print "\ndone..."

# ----------------------------------------------------------------------------
# Convert input file

trs = Transcription(name="PhonemesClassification")

if not args.quiet: print "Classifying..."
for name in mappings.keys():
    if not args.quiet: print " -", name
    new_tier = mappings[name].map_tier(tier)
    new_tier.SetName(name)
    trs.Append(new_tier)
print "done..."

# ----------------------------------------------------------------------------
# Write converted tiers

if not args.quiet: print "Saving..."
filename = fname + "-class" + fext
annotationdata.io.write(filename, trs)
print "File %s created." % filename.encode('utf8')
