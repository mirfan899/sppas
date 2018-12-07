#!/usr/bin/env python
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

    bin.intsint.py
    ~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Run the intsint automatic annotation

"""
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sppasIntsint
from sppas.src.anndata.aio import extensions_out
from sppas.src.config import annots

from sppas.src.annotations.param import sppasParam
from sppas.src.annotations.manager import sppasAnnotationsManager
from sppas.src.utils.fileutils import setup_logging


# ---------------------------------------------------------------------------
# Verify and extract args:
# ---------------------------------------------------------------------------

parameters = sppasParam()
parameters.activate_annotation("intsint")

parser = ArgumentParser(usage="{:s} -I file -I file ..."
                              "".format(os.path.basename(PROGRAM)),
                        description="INTSINT automatic annotations.")

parser.add_argument("-i",
                    required=False,
                    metavar="file",
                    help='Input file name with anchors.')

parser.add_argument("-o",
                    required=False,
                    metavar="file",
                    help="Intsint output file name of -i option (default: stdout)")

parser.add_argument("-I",
                    required=False,
                    action='append',
                    metavar="file",
                    help='Input file name with anchors.')

parser.add_argument("-e",
                    default=annots.extension,
                    metavar="extension",
                    help='Output file extension. One of: {:s}'
                         ''.format(" ".join(extensions_out)))

parser.add_argument("--quiet",
                    action='store_true',
                    help="Print only warnings and errors.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ---------------------------------------------------------------------------
# The automatic annotation is here:
# ---------------------------------------------------------------------------

# Perform the annotation on a single file
# ---------------------------------------
if args.i and args.o:
    intsint = sppasIntsint(logfile=None)
    intsint.run(args.i, args.o)
    sys.exit(0)

# Perform the annotation on a set of files
# ----------------------------------------

# Fix the output file extension
parameters.set_output_format(args.e)

# Fix input files
files = list()
if args.I:
    for f in args.I:
        parameters.add_sppasinput(os.path.abspath(f))
if args.i:
    parameters.add_sppasinput(os.path.abspath(args.i))

# Redirect all messages to logging.
# Not fully quiet: print warnings and errors.
parameters.set_logfilename(None)
if not args.quiet:
    setup_logging(10, None)
else:
    setup_logging(30, None)

# Perform the annotation
process = sppasAnnotationsManager(parameters)
process.run_intsint()
