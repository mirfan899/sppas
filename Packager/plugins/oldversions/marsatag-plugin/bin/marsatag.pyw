#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013  Tatsuya Watanabe
#
# This file is part of MarsaTagPlugin.
#
# MarsaTagPlugin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MarsaTagPlugin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MarsaTagPlugin.  If not, see <http://www.gnu.org/licenses/>.


import os.path
import platform
import sys
import getopt
import wx

LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib")
sys.path.insert(0, LIB)


try:
    from marsatag.MarsaTagFrame import MarsaTagFrame
except ImportError as e:
    sys.stderr.write("MarsaTag. Import error: \n")
    sys.stderr.write(str(e)+"\n")
    sys.exit(1)


def usage(output):
    """ Print the program usage on an output.
        Parameters: 
           - output is a string representing the output (for example: sys.stdout)
        Return:      none
        Exceptions:  none
    """
    output.write('marsatag.py [options] where options are:\n')
    output.write('      file     an annotation file\n')
    output.write('      --help      Print this help\n')

# End usage
# ----------------------------------------------------------------------


def quit(message, status):
    """ Exit this program.
        Parameters: 
           - message is a text to communicate to the user on sys.stderr.
           - status is an integer of the status exit value 
        Return:      none
        Exceptions:  none
    """
    sys.stderr.write('marsatag.py. '+message)
    sys.exit(status)

# End quit
# ----------------------------------------------------------------------

def main( argv ):

    SETTING = os.path.join(os.path.dirname(
                           os.path.dirname(
                           os.path.abspath(__file__))), 'setting', 'command.json')
    files = argv[1:]
    # App
    app = wx.App(False)
    f = MarsaTagFrame(parent=None, inputfiles=files, cfgfile=SETTING)
    f.Hide()
    app.MainLoop()

# ---------------------------------------------------------------------------


if __name__ == '__main__':

    if len(sys.argv) < 1:
        # stop the program and print an error message
        usage(sys.stderr)
        sys.exit(1)

    main( sys.argv )

# ---------------------------------------------------------------------------
