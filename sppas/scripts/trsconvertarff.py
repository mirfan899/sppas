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

    scripts.trsconvert.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to export annotations files.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.anndata.aio.readwrite import sppasRW

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM),
                        description="... a script to export annotations files.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("-c",
                    metavar="class",
                    required=False,
                    type=str,
                    help='The class tier name.')

parser.add_argument("-C",
                    metavar="classtags",
                    required=False,
                    type=int,
                    default=10,
                    help='Extend the maximum number of possible tags of the class (default: 10).')

parser.add_argument("-t",
                    metavar="value",
                    required=False,
                    action='append',
                    type=int,
                    help='An attribute tier number (use as many -t options as wanted). '
                         'Positive or negative value: 1=first tier, -1=last tier.')

parser.add_argument("-n",
                    metavar="tiername",
                    required=False,
                    action='append',
                    type=str,
                    help='An attribute tier name (use as many -n options as wanted).')

instance_group = parser.add_mutually_exclusive_group(required=False)

instance_group.add_argument("-a",
                            metavar="anchor",
                            required=False,
                            type=str,
                            help='Anchor tier name to create instances.')

instance_group.add_argument("-s",
                            metavar="step",
                            required=False,
                            type=float,
                            help='Time step to create instances.')

parser.add_argument("-u",
                    metavar="uncertaintag",
                    required=False,
                    type=str,
                    default="?",
                    help='Tag that is used into annotations for an uncertain label. (default: ?)')

parser.add_argument("-e",
                    metavar="emptytag",
                    required=False,
                    type=str,
                    default="none",
                    help='Tag to be used for un-labelled annotations. (default: none)')

parser.add_argument("--probas",
                    action='store_true',
                    help="Enable the conversion of annotations into distribution of probabilities.")

parser.add_argument("--xra",
                    action='store_true',
                    help="Also export an xra file.")

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Read

if args.quiet is False:
    print("Read input file:")
parser = sppasRW(args.i)
trs = parser.read(heuristic=True)
if args.quiet is False:
    print(" [  OK  ]")

# ----------------------------------------------------------------------------
# Attributes tiers

attribute_type = "string"
if args.probas:
    attribute_type = "numeric"

# Take all tiers or only specified tiers
attribute_tiers = list()
if not args.t and not args.n:
    for tier in trs:
        tier.set_meta("weka_attribute", attribute_type)

if args.t:
    for tier_number in args.t:
        if 0 < tier_number <= len(trs):
            trs[tier_number-1].set_meta("weka_attribute", attribute_type)
        elif tier_number < 0:
            trs[tier_number].set_meta("weka_attribute", attribute_type)
        else:
            print("{:d} is not a valid tier number.".format(tier_number))
            sys.exit(1)

if args.n:
    for tier_name in args.n:
        tier = trs.find(tier_name)
        if tier is not None:
            tier.set_meta("weka_attribute", attribute_type)

# ----------------------------------------------------------------------------
# Class

if args.c:
    tier = trs.find(args.c)
    if tier is None:
        print("{:s} is not a valid tier name.".format(args.c))
        sys.exit(1)
    tier.set_meta("weka_class", "")
    tier.pop_meta("weka_attribute")

# ----------------------------------------------------------------------------
# Time split

if args.a:
    tier = trs.find(args.a)
    if tier is None:
        print("{:s} is not a valid tier name.".format(args.a))
        sys.exit(1)
    tier.set_meta('weka_instance_anchor', "")

if args.s:
    trs.set_meta("weka_instance_step", str(args.s))

# ----------------------------------------------------------------------------
# Meta-data, to configure how the data will have to be interpreted

if args.e:
    trs.set_meta("weka_empty_annotation_tag", args.e)

if args.u:
    trs.set_meta("weka_uncertain_annotation_tag", args.u)

if args.C:
    trs.set_meta("weka_max_class_tags", str(args.C))

# ----------------------------------------------------------------------------

name, extension = os.path.splitext(args.i)
parser.set_filename(name + ".arff")
parser.write(trs)

if args.xra:
    parser.set_filename(name + "-export.xra")
    parser.write(trs)
