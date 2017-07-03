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

    scripts.acmsplit.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to split a hmmdef file into hmms.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.models.acm.acmodel import sppasAcModel

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i hmmdef -o dir" % os.path.basename(PROGRAM),
                        description="... a script to split a hmmdef file into hmms.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input file name (commonly hmmdefs)')

parser.add_argument("-r",
                    metavar="file",
                    required=False,
                    help='Optional: Input mapping file name (commonly monophones.repl).')

parser.add_argument("-o",
                    metavar="dir",
                    required=True,
                    help='Output directory name')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if not os.path.isdir(args.o):
    print("Error: {0} must be an existing directory.".format(args.o))
    sys.exit(1)

if not os.path.isfile(args.i):
    print("Error: {0] must be an acoustic model file (HTK-ASCII format).".format(args.i))
    sys.exit(1)

if args.quiet is False:
    print("Loading AC:")
acmodel1 = sppasAcModel()
acmodel1.load_htk(args.i)
if args.r:
    acmodel1.load_phonesrepl(args.r)
if args.quiet is False:
    print("... done")

# ----------------------------------------------------------------------------

acmodel = acmodel1.extract_monophones()
acmodel.replace_phones()

for hmm in acmodel.hmms:

    filename = os.path.join(args.o, hmm.name)
    filename = filename + ".hmm"
    if args.quiet is False:
        print(hmm.name+": "+filename)
    hmm.save(filename)
