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

    bin.plugin.py
    ~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Main script to work with SPPAS plugins.

    Examples of use:

    Install a plugin:
    >>> ./sppas/bin/plugin.py --install -p sppas/src/plugins/tests/data/soxplugin.zip

    Use a plugin on a file:
    >>> ./sppas/bin/plugin.py --apply -p soxplugin -i samples/samples-eng/oriana1.wav -o resampled.wav

    Remove a plugin:
    >>> ./sppas/bin/plugin.py --remove -p soxplugin

    An "all-in-one" solution:
    >>> ./sppas/bin/plugin.py --install --apply --remove -p sppas/src/plugins/tests/data/soxplugin.zip -i samples/samples-eng/oriana1.wav -o resampled.wav

"""
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas
from sppas.src.ui.term.terminalcontroller import TerminalController

from sppas.src.plugins import sppasPluginsManager

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s [actions] [options]" % os.path.basename(PROGRAM),
                        prog=PROGRAM,
                        description="Plugin command line interface.")

parser.add_argument("--install",
                    action='store_true',
                    help="Install a new plugin from a plugin package.")

parser.add_argument("--remove",
                    action='store_true',
                    help="Remove an existing plugin.")

parser.add_argument("--apply",
                    action='store_true',
                    help="Apply a plugin on a file.")

parser.add_argument("-p",
                    metavar="string",
                    required=True,
                    help="Plugin (either an identifier, or an archive file).")

parser.add_argument("-i",
                    metavar="string",
                    required=False,
                    help="Input file to apply a plugin on it.")

parser.add_argument("-o",
                    metavar="string",
                    required=False,
                    help="Output file, ie the result of the plugin.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------
# Plugins is here:
# ----------------------------------------------------------------------------

try:
    term = TerminalController()
    print(term.render('${GREEN}-----------------------------------------------------------------------${NORMAL}'))
    print(term.render('${RED}'+sppas.__name__+' - Version '+sppas.__version__+'${NORMAL}'))
    print(term.render('${BLUE}'+sppas.__copyright__+'${NORMAL}'))
    print(term.render('${BLUE}'+sppas.__url__+'${NORMAL}'))
    print(term.render('${GREEN}-----------------------------------------------------------------------${NORMAL}\n'))
except Exception:
    print('-----------------------------------------------------------------------\n')
    print(sppas.__name__+'   -  Version '+sppas.__version__)
    print(sppas.__copyright__)
    print(sppas.__url__+'\n')
    print('-----------------------------------------------------------------------\n')

manager = sppasPluginsManager()
plugin_id = args.p


if args.install:

    print("Plugin installation")

    # fix a name for the plugin directory
    plugin_folder = os.path.splitext(os.path.basename(args.p))[0]
    plugin_folder.replace(' ', "_")

    # install the plugin.
    plugin_id = manager.install(args.p, plugin_folder)

if args.apply and args.i:

    # Get the plugin
    p = manager.get_plugin(plugin_id)

    # Set the output file name (if any)
    if args.o:
        options = p.get_options()
        for opt in options.values():
            if opt.get_key() == "output":
                opt.set_value(args.o)
        p.set_options(options)

    # Run
    message = manager.run_plugin(plugin_id, [args.i])
    print(message)


if args.remove:

    manager.delete(plugin_id)

print("-----------------------------------------------------------------------\n")
