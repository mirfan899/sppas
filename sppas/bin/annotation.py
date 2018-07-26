#!/usr/bin/env python2
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sg.org/

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

    bin.annotation.py
    ~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Run any or all automatic annotations.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.config import sg
from sppas.src.annotations import DEFAULT_OUTPUT_EXTENSION
from sppas.src.annotations.param import sppasParam
from sppas.src.annotations.manager import sppasAnnotationsManager
from sppas.src.annotationdata.aio import extensions_out
from sppas.src.ui.term.textprogress import ProcessProgressTerminal
from sppas.src.ui.term.terminalcontroller import TerminalController


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parameters = sppasParam()
parser = ArgumentParser(usage="%s -w file|folder [options]" % os.path.basename(PROGRAM),
                        prog=PROGRAM,
                        description="Automatic annotations.")

parser.add_argument("-w", 
                    required=True, 
                    metavar="file|folder", 
                    help='Input wav file name, or directory')

parser.add_argument("-l", 
                    metavar="lang",
                    help='Input language, using iso639-3 code')

parser.add_argument("-e", 
                    default=DEFAULT_OUTPUT_EXTENSION,
                    metavar="extension",
                    help='Output extension. One of: %s' % " ".join(extensions_out))

parser.add_argument("--momel", action='store_true', help="Activate Momel")
parser.add_argument("--intsint", action='store_true', help="Activate INTSINT")
parser.add_argument("--ipus", action='store_true', help="Activate IPUs Segmentation")
parser.add_argument("--tok", action='store_true', help="Activate Tokenization")
parser.add_argument("--phon", action='store_true', help="Activate Phonetization")
parser.add_argument("--chunks", action='store_true', help="Activate Chunks alignment")
parser.add_argument("--align", action='store_true', help="Activate Phones alignment")
parser.add_argument("--syll", action='store_true', help="Activate Syllabification")
parser.add_argument("--tga", action='store_true', help="Activate TimeGroupAnalyzer")
parser.add_argument("--repet", action='store_true', help="Activate Self-Repetitions")
parser.add_argument("--all", action='store_true', help="Activate ALL automatic annotations")

parser.add_argument("--merge",
                    action='store_true',
                    help="Create a merged TextGrid file, if more than two automatic annotations. (this is the default)")

parser.add_argument("--nomerge",
                    action='store_true',
                    help="Do not create a merged TextGrid file.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------
# Automatic Annotations are here:
# ----------------------------------------------------------------------------

parameters.add_sppasinput(os.path.abspath(args.w))

if args.l:
    parameters.set_lang(args.l)
ext = args.e
if not ext.startswith("."):
    ext = "." + ext
extensions = [e.lower() for e in extensions_out]  #_multitiers]
if not ext.lower() in extensions:
    print("\n")
    print("[WARNING] Unknown extension:", args.e, ". Extension is set to its default value.")
    print("\n")
    ext = DEFAULT_OUTPUT_EXTENSION
parameters.set_output_format(ext)

if args.momel:
    parameters.activate_annotation("momel")
if args.intsint:
    parameters.activate_annotation("intsint")
if args.ipus:
    parameters.activate_annotation("ipus")
if args.tok:
    parameters.activate_annotation("textnorm")
if args.phon:
    parameters.activate_annotation("phon")
if args.chunks:
    parameters.activate_annotation("chunks")
if args.align:
    parameters.activate_annotation("align")
if args.syll:
    parameters.activate_annotation("syll")
if args.tga:
    parameters.activate_annotation("tga")
if args.repet:
    parameters.activate_annotation("repet")
if args.all:
    for step in range(parameters.get_step_numbers()):
        parameters.activate_step(step)

try:
    term = TerminalController()
    print(term.render('${GREEN}-----------------------------------------------------------------------${NORMAL}'))
    print(term.render('${RED}'+sg.__name__+' - Version '+sg.__version__+'${NORMAL}'))
    print(term.render('${BLUE}'+sg.__copyrigh__+'${NORMAL}'))
    print(term.render('${BLUE}'+sg.__url__+'${NORMAL}'))
    print(term.render('${GREEN}-----------------------------------------------------------------------${NORMAL}\n'))
except:
    print('-----------------------------------------------------------------------\n')
    print(sg.__name__+'   -  Version '+sg.__version__)
    print(sg.__copyright__)
    print(sg.__url__+'\n')
    print('-----------------------------------------------------------------------\n')


# ----------------------------------------------------------------------------
# Annotation is here
# ----------------------------------------------------------------------------

p = ProcessProgressTerminal()
process = sppasAnnotationsManager(parameters)
if args.nomerge:
    process.set_do_merge(False)
if args.merge:
    process.set_do_merge(True)
process.run_annotations(p)

try:
    term = TerminalController()
    print(term.render('${GREEN}-----------------------------------------------------------------------${NORMAL}'))
    print(term.render('${RED}See '+parameters.get_logfilename()+' for details.'))
    print(term.render('${GREEN}Thank you for using '+sg.__name__+"."))
    print(term.render('${GREEN}-----------------------------------------------------------------------${NORMAL}\n'))
except:
    print('-----------------------------------------------------------------------\n')
    print("See "+parameters.get_logfilename()+" for details.\nThank you for using "+sg.__name__+".")
    print('-----------------------------------------------------------------------\n')
