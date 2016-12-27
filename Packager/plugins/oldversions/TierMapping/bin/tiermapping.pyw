#!/usr/bin/env python2
# -*- coding: utf-8 -*-


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import os.path
import platform
import sys
import getopt

import wx
import logging
from logging import info as loginfo


# VERIFY PYTHON
# -------------
if sys.version_info < (2, 7):
    import tkMessageBox
    tkMessageBox.showwarning(
        "Python Error...",
        "Your python version is too old. Mapping requires 2.7\n. Verify your python installation and try again."
        )
    sys.exit(1)

if sys.version_info > (3, 0):
    import tkMessageBox
    tkMessageBox.showwarning(
        "Python Error...",
        "Your python version is not appropriate. Mapping requires 2.7\n. Verify your python installation and try again."
        )
    sys.exit(1)


# VERIFY WXPYTHON
# ----------------

try:
    import wx
except ImportError,e:
    import tkMessageBox
    tkMessageBox.showwarning(
        "WxPython Error...",
        "WxPython is not installed on your system.\n. Verify your installation and try again."
        )
    sys.exit(1)


# Make sure that we can import libraries
LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib")
sys.path.insert(0, LIB)

_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
_files = os.listdir(_dir)
MAPCHAR = [os.path.join(_dir, f) for f in _files]


from tiermapping.app import TierMappingApp

def usage(output):
    """ Print the program usage on an output.
        Parameters: 
           - output is a string representing the output (for example: sys.stdout)
        Return:      none
        Exceptions:  none
    """
    output.write('mapping.py [options] where options are:\n')
    output.write('      file an annotation file\n')
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
    sys.stderr.write('mapping.py. '+message)
    sys.exit(status)

# End quit
# ----------------------------------------------------------------------

def main( argv ):
    files = argv[1:]
    app = TierMappingApp(files)
    app.MainLoop()


# ---------------------------------------------------------------------------


if __name__ == '__main__':

    if len(sys.argv) < 1:
        # stop the program and print an error message
        usage(sys.stderr)
        sys.exit(1)

    main( sys.argv )

# ---------------------------------------------------------------------------
