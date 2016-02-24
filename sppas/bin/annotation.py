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
#           http://www.lpl-aix.fr/~bigi/sppas
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2016  Brigitte Bigi
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
# File: annotation.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
import os.path
from argparse import ArgumentParser

PROGRAM_PATH = os.path.abspath(__file__)
SPPAS = os.path.join( os.path.dirname( os.path.dirname( PROGRAM_PATH ) ), "src" )
sys.path.append(SPPAS)

from sp_glob import program, author, version, copyright, url
from annotationdata.io import extensions_out_multitiers
from annotations.param import sppasParam
from annotations.process import sppasProcess
from term.textprogress import TextProgress
from term.terminalcontroller import TerminalController


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parameters = sppasParam()
parser = ArgumentParser(usage="%s -w file|folder [options]" % os.path.basename(PROGRAM_PATH), prog=PROGRAM_PATH, description="Automatic annotations command line interface.")

parser.add_argument("-w", required=True, metavar="file|folder", help='Input wav file name, or directory')

parser.add_argument("-l", metavar="lang", help='Input language, using iso639-3 code')
parser.add_argument("-e", metavar="extension", help='Output extension. One of: %s'%" ".join(extensions_out_multitiers))
parser.add_argument("--momel", action='store_true', help="Activate Momel and INTSINT" )
parser.add_argument("--ipu",   action='store_true', help="Activate IPUs Segmentation" )
parser.add_argument("--tok",   action='store_true', help="Activate Tokenization" )
parser.add_argument("--phon",  action='store_true', help="Activate Phonetization" )
parser.add_argument("--align", action='store_true', help="Activate Alignment" )
parser.add_argument("--syll",  action='store_true', help="Activate Syllabification" )
parser.add_argument("--rep",   action='store_true', help="Activate Repetitions" )
parser.add_argument("--all",   action='store_true', help="Activate ALL automatic annotations" )
parser.add_argument("--merge", action='store_true', help="Create a merged TextGrid file, if more than two automatic annotations. (this is the default)" )
parser.add_argument("--nomerge", action='store_true', help="Do not create a merged TextGrid file." )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------
# Automatic Annotations are here:
# ----------------------------------------------------------------------------

parameters.add_sppasinput( os.path.abspath(args.w) )

if args.l: parameters.set_lang( args.l )
if args.e:
    extensions = [e.lower() for e in extensions_out_multitiers]
    if not args.e.lower() in extensions:
        print "[WARNING] Unknown extension:",args.e,". Extension is set to its default value."
    else:
        parameters.set_output_format( args.e )

if args.momel: parameters.activate_step(0)
if args.ipu:   parameters.activate_step(1)
if args.tok:   parameters.activate_step(2)
if args.phon:  parameters.activate_step(3)
if args.align: parameters.activate_step(4)
if args.syll:  parameters.activate_step(5)
if args.rep:   parameters.activate_step(6)
if args.all:
    for step in range(parameters.get_step_numbers()):
        parameters.activate_step(step)

try:
    term = TerminalController()
    print term.render('${GREEN}-----------------------------------------------------------------------${NORMAL}')
    print term.render('${RED}'+program+' - Version '+version+'${NORMAL}')
    print term.render('${BLUE}'+copyright+'${NORMAL}')
    print term.render('${BLUE}'+url+'${NORMAL}')
    print term.render('${GREEN}-----------------------------------------------------------------------${NORMAL}\n')
except:
    print '-----------------------------------------------------------------------\n'
    print program+'   -  Version '+version
    print copyright
    print url+'\n'
    print '-----------------------------------------------------------------------\n'


# ----------------------------------------------------------------------------
# Annotation is here
# ----------------------------------------------------------------------------

p = TextProgress()
process = sppasProcess( parameters )
if args.nomerge:
    process.set_domerge( False )
if args.merge:
    process.set_domerge( True )
process.run_annotations( p )

try:
    term = TerminalController()
    print term.render('${GREEN}-----------------------------------------------------------------------${NORMAL}')
    print term.render('${RED}See '+parameters.get_logfilename()+' for details.')
    print term.render('${GREEN}Thank you for using '+program+".")
    print term.render('${GREEN}-----------------------------------------------------------------------${NORMAL}\n')
except:
    print ('-----------------------------------------------------------------------\n')
    print "See "+parameters.get_logfilename()+" for details.\nThank you for using "+program+"."
    print ('-----------------------------------------------------------------------\n')

# ----------------------------------------------------------------------------
