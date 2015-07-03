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
#       Copyright (C) 2011-2014  Brigitte Bigi
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
# File: sppasgui.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
import os.path
from argparse import ArgumentParser
import traceback
import tkMessageBox


# VERIFY PYTHON
# -------------
if sys.version_info < (2, 7):
    tkMessageBox.showwarning(
        "Python Error...",
        "Your python version is too old. SPPAS requires 2.7\n. Verify your python installation and try again."
        )
    sys.exit(1)

if sys.version_info >= (3, 0):
    tkMessageBox.showwarning(
        "Python Error...",
        "Your python version is not appropriate. SPPAS requires 2.7\n. Verify your python installation and try again."
        )
    sys.exit(1)


# VERIFY WXPYTHON
# ----------------
try:
    import wx
except ImportError:
    tkMessageBox.showwarning(
        "WxPython Error...",
        "WxPython is not installed on your system\n. Verify your installation and try again."
        )
    sys.exit(1)

try:
    wxv = wx.version().split()[0]
except Exception:
    wxv = '2'

if int(wxv[0]) < 3:
    tkMessageBox.showwarning(
        "WxPython Warning...",
        'Your version of wxpython is too old. You could encounter problem while using SPPAS.\n'
        'Please, perform the update at http://wxpython.org/download.php and restart SPPAS.\n\n'
        'For any help, see SPPAS installation page.')


# THEN, VERIFY SPPAS
# ------------------

# Make sure that we can import libraries
PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.insert(0,SPPAS)

try:
    from wxgui.frames.mainframe import FrameSPPAS
    from utils.commons import setup_logging
except ImportError as e:
    print traceback.format_exc()
    tkMessageBox.showwarning(
        "SPPAS installation Error...",
        "A problem occurred when launching SPPAS.\nVerify your SPPAS installation directory and try again. The error is: %s"%(str(e))
        )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Install Gettext
# ---------------------------------------------------------------------------

def install_gettext_in_builtin_namespace():
    def _(message):
        return message
    import __builtin__
    if not "_" in __builtin__.__dict__:
        __builtin__.__dict__["_"] = _


# ---------------------------------------------------------------------------
# Test if Julius is installed.
# ---------------------------------------------------------------------------

def test_julius(parent):
    """
    Test if Julius is available.
    """
    import subprocess
    try:
        NULL = open(os.devnull, "w")
        subprocess.call(['julius'], stdout=NULL, stderr=subprocess.STDOUT)
    except OSError:
        dial = wx.MessageDialog(None, 'Julius is not installed on your system.\nThe automatic annotation "Alignment" WILL NOT WORK.', 'Exclamation',
            wx.OK | wx.ICON_EXCLAMATION)
        dial.ShowModal()

# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

# Log
log_level = 0
log_file  = None
setup_logging(log_level, log_file)

# Gettext
install_gettext_in_builtin_namespace()


# Arguments
# ------------------------------------------------------------------------

parser = ArgumentParser(usage="%s files" % os.path.basename(PROGRAM), description="SPPAS Graphical User Interface.")
parser.add_argument("files", nargs="*", help='Input wav file name(s)')
args = parser.parse_args()

# force to add path
filenames = []
for f in args.files:
    p,b = os.path.split( f )
    if not p:
        p = os.getcwd()
    filenames.append( os.path.abspath(os.path.join(p,b) ))


# ----------------------------------------------------------------------------
# SPPAS GUI is here:
# ----------------------------------------------------------------------------

sppas = wx.App(redirect=True)

# Create the main frame
try:
    frame = FrameSPPAS( )
    sppas.SetTopWindow(frame)
    frame.Show()
    test_julius(frame)
    if len(filenames) > 0:
        frame.RefreshTree( filenames )
except Exception as e:
    tkMessageBox.showwarning(
    "SPPAS Error...",
    "A problem occurred when creating the SPPAS graphical user interface.\nThe error is: %s"%(str(e))
    )
    print traceback.format_exc()


#
sppas.MainLoop()

# ---------------------------------------------------------------------------
