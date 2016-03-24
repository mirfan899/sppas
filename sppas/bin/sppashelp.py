#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
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
# File: sppashelp.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os.path
import traceback
import time

def exit_error( msg ):
    print "[ ERROR ] ",msg
    time.sleep( 20 )
    sys.exit(1)

# VERIFY PYTHON
# -------------
if sys.version_info < (2, 7):
    exit_error(" The version of Python is too old: SPPAS requires exactly the version 2.7.something.")

if sys.version_info >= (3, 0):
    exit_error( "The version of Python is not the right one: SPPAS requires exactly the version 2.7.something.")

# VERIFY WXPYTHON
# ----------------
try:
    import wx
except ImportError:
    exit_error( "WxPython is not installed on your system\n. The Graphical User Interface of SPPAS can't work. Refer to the installation instructions of the SPPAS web site.")

try:
    wxv = wx.version().split()[0]
except Exception:
    wxv = '2'

if int(wxv[0]) < 3:
    print "[ WARNING ] The version of WxPython is too old.\n\tThe Graphical User Interface will not display properly.\n\tUpdate at http://wxpython.org/ and restart SPPAS.\n\tFor any help, see SPPAS installation page.\n"
    time.sleep( 20 )

# THEN, VERIFY SPPAS
# ------------------

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.insert(0,SPPAS)

try:
    from wxgui.frames.helpbrowser  import HelpBrowser
    from wxgui.structs.prefs       import Preferences
except ImportError as e:
    print traceback.format_exc()
    exit_error( "A problem occurred when launching HelpBrowser.\nThe error is: %s.\nVerify the SPPAS installation directory and try again."%(str(e)))


# ----------------------------------------------------------------------------
# SPPAS GUI is here:
# ----------------------------------------------------------------------------

sppas = wx.App(redirect=True)

try:
    frame = HelpBrowser( None, Preferences() )
    sppas.SetTopWindow(frame)
    frame.Show()
except Exception as e:
    print traceback.format_exc()
    exit_error("A problem occurred when creating the Graphical User Interface.\nThe error is: %s"%(str(e)) )

sppas.MainLoop()

# ---------------------------------------------------------------------------
