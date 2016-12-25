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
#       Copyright (C) 2011-2017  Brigitte Bigi
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
# File: plugin.py
# ----------------------------------------------------------------------------

"""
@author:       Brigitte Bigi
@organization: Laboratoire Parole et Langage, Aix-en-Provence, France
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2011-2017  Brigitte Bigi
@summary:      Main script to work with SPPAS plugins.

Examples of use:

Install a plugin:
>>> ./sppas/bin/plugin.py --install -p sppas/src/plugins/tests/data/soxplugin.zip

Use a plugin on a file:
>>> ./sppas/bin/plugin.py --apply -p soxplugin -i samples/samples-eng/oriana1.wav -o resampled.wav

Remove a plugin:
>>> ./sppas/bin/plugin.py --remove -p soxplugin


A "all-in-one" solution:
>>> ./sppas/bin/plugin.py --install --apply --remove -p sppas/src/plugins/tests/data/soxplugin.zip -i samples/samples-eng/oriana1.wav -o resampled.wav

"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
from argparse import ArgumentParser

PROGRAM_PATH = os.path.abspath(__file__)
SPPAS = os.path.join( os.path.dirname( os.path.dirname( PROGRAM_PATH ) ), "src" )
sys.path.append(SPPAS)

from sp_glob import program, author, version, copyright, url
from term.textprogress import ProcessProgressTerminal
from term.terminalcontroller import TerminalController

from plugins.manager import sppasPluginsManager

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s [actions] [options]" % os.path.basename(PROGRAM_PATH), prog=PROGRAM_PATH, description="Plugin command line interface.")

parser.add_argument("--install", action='store_true', help="Install a new plugin from a plugin package." )
parser.add_argument("--remove",  action='store_true', help="Remove an existing plugin." )
parser.add_argument("--apply",   action='store_true', help="Apply a plugin on a file." )
parser.add_argument("-p",        metavar="string", required=True, help="Plugin (identifier, or archive file)." )
parser.add_argument("-i",        metavar="string", required=False, help="Input file to apply a plugin on it." )
parser.add_argument("-o",        metavar="string", required=False, help="Output file, ie the result of the plugin." )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------
# Plugins is here:
# ----------------------------------------------------------------------------

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

manager = sppasPluginsManager()
pluginid = args.p


if args.install:

    print "Plugin installation"

    # fix a name for the plugin directory
    pluginfolder = os.path.splitext(os.path.basename( args.p ))[0]
    pluginfolder.replace(' ', "_")

    # install the plugin.
    pluginid = manager.install( args.p, pluginfolder )

if args.apply and args.i:

    # Get the plugin
    p = manager.get_plugin( pluginid )

    # Set the output file name (if any)
    if args.o:
        options = p.get_options()
        for opt in options.values():
            if opt.get_key() == "output":
                opt.set_value( args.o )
        p.set_options(options)

    # Run
    message = manager.run_plugin( pluginid, [args.i] )
    print message


if args.remove:

    manager.delete( pluginid )

print '-----------------------------------------------------------------------\n'

# ----------------------------------------------------------------------------
