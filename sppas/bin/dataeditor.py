#!/usr/bin/env python2
#
# Copyright (C) 2013  Brigitte Bigi
#
# This file is part of SPPAS.
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
# along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

#import gettext
#import locale
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
        "Your python version is too old. DataRoamer requires 2.7\n. Verify your python installation and try again."
        )
    sys.exit(1)

if sys.version_info >= (3, 0):
    import tkMessageBox
    tkMessageBox.showwarning(
        "Python Error...",
        "Your python version is not appropriate. DataRoamer requires 2.7\n. Verify your python installation and try again."
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
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "wxgui"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

try:
    from editor.frameeditor import FrameEditor
except ImportError as e:
    import tkMessageBox
    tkMessageBox.showwarning(
        "Error...",
        "A problem occurred.\nVerify your installation and try again.\n\nThe system error message is: %s" % str(e)
        )
    sys.exit(1)



# ---------------------------------------------------------------------------
# Fix locale, install Gettext
# ---------------------------------------------------------------------------

if platform.system() == "Windows":
    # The appropriate environment variables are set on other systems
    import locale
    language, encoding = locale.getdefaultlocale()
    os.environ['LANG'] = language


#LOCALE_DIR = os.path.join(os.path.dirname(__file__), "po")
#gettext.install('drawing', LOCALE_DIR, unicode=True)


# ---------------------------------------------------------------------------
# Setup a logger to communicate on the terminal, or a file.
# ---------------------------------------------------------------------------

def setup_logging(log_level, filename):
    """ 
    Setup default logger to log to stderr or and possible also to a file.
    
    The default logger is used like this:
        >>> import logging
        >>> logging.error(text message)
    """
    format= "%(asctime)s [%(levelname)s] %(message)s"
    # Setup logging to stderr
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format))
    console_handler.setLevel(log_level)
    logging.getLogger().addHandler(console_handler)

    # Setup logging to file if filename is specified
    if filename:
        file_handler = logging.FileHandler(filename, "w")
        file_handler.setFormatter(logging.Formatter(format))
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(log_level)
    loginfo("Logging set up with log level=%s, filename=%s", log_level,
            filename)



# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def usage(output):
    """ Print the program usage on an output.
        Parameters: 
           - output is a string representing the output (for example: sys.stdout)
        Return:      none
        Exceptions:  none
    """
    output.write('dataeditor.py [options] where options are:\n')
    output.write('      -i file     A wav or an annotation file (give as many -i options as needed)\n')
    output.write('      -t str      Title of the main frame.\n')
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
    sys.stderr.write('dataeditor.py. '+message)
    sys.exit(status)

# End quit
# ----------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

def __dataeditor( argv ):

    # Log
    log_level = 1
    log_file  = None
    setup_logging(log_level, log_file)

    # Args
    arguments = {}
    arguments['files'] = []

    # Get options (if any...)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:t:", ["help"])
    except getopt.GetoptError, err:
        # Print help information and exit:
        quit("Error: "+str(err)+".\nUse option --help for any help.\n", 1)

    # Extract options
    for o, a in opts:
        if o == "-i": 
            p,b = os.path.split(a)
            if not p:
                p = os.getcwd()
            arguments['files'].append( os.path.abspath(os.path.join(p,b)) )
        elif o == "-t":
            arguments['title'] = a
        elif o == "--help": # need help
            print 'Help'
            usage(sys.stdout)
            sys.exit(0)

    # App
    app = wx.App()
    #wx.InitAllImageHandlers()
    frame = FrameEditor(None, -1, arguments)

    app.SetTopWindow(frame)
    if "files" in arguments:
        frame.AddFiles( arguments["files"] )

    app.MainLoop()

# ---------------------------------------------------------------------------


if __name__ == '__main__':

    if len(sys.argv) < 1:  
        # stop the program and print an error message
        usage(sys.stderr)
        sys.exit(1)

    __dataeditor( sys.argv )

# ---------------------------------------------------------------------------
