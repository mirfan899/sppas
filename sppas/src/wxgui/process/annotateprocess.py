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
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
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
# File: annotateprocess.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os
import wx
from annotations.process import sppasProcess

from wxgui.views.log import LogDialog
from wxgui.views.processprogress import ProcessProgressDialog
from wxgui.sp_consts import FRAME_TITLE


# ----------------------------------------------------------------------------

class AnnotateProcess( object ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Automatic annotation process, with progress bar.

    """

    def __init__(self, preferences):
        """
        Constructor.
        """
        self.process = None
        self.preferences = preferences

    # End __init__
    # ------------------------------------------------------------------------


    def IsRunning(self):
        """
        Return True if the process is running.
        Returns: (bool)
        """
        if self.process is None:
            return False
        return True

    # End IsRunning
    # ------------------------------------------------------------------------


    def Run(self, parent, filelist, activeannot, parameters):
        """
        Execute the automatic annotations.
        """
        # Check input files
        if len(filelist) == 0:
            message = "Empty selection! Select WAV file(s) to annotate."
            dlg = wx.MessageDialog(parent, message, 'Warning', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Fix options
        nbsteps = 0
        for i in range(len(activeannot)):
            if activeannot[i]:
                nbsteps = nbsteps + 1
                parameters.activate_step(i)
                #if there are languages available and none of them is selected, print an error
                if len(parameters.get_langlist(i)) > 0 and parameters.get_lang(i) == None:
                    message = "There isn't any language selected for the annotation \"%s\"" % parameters.get_step_name(i)
                    dlg = wx.MessageDialog(parent, message, 'Warning', wx.OK | wx.ICON_WARNING)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
            else:
                parameters.disable_step(i)

        if not nbsteps:
            message = "No annotation selected! Check steps to annotate."
            dlg = wx.MessageDialog(parent, message, 'Warning', wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
            return

        parameters.set_sppasinput(filelist)
        parameters.set_output_format(self.preferences.GetValue('M_OUTPUT_EXT'))

        # Create the progress bar then run the annotations
        wx.BeginBusyCursor()
        p = ProcessProgressDialog(parent, self.preferences)
        p.set_title("Automatic Annotation progress...")
        self.process = sppasProcess(parameters)
        self.process.run_annotations( p )
        p.close()
        self.process = None
        wx.EndBusyCursor()

        # Show report
        try:
            logframe = LogDialog(parent, self.preferences, parameters.get_logfilename())
            logframe.ShowModal()
            logframe.Destroy()
        except Exception as e:
            import logging
            #import traceback
            #print traceback.format_exc()
            logging.debug('Log Error: %s'%str(e))
            message = "SPPAS finished.\nSee " + parameters.get_logfilename() + " for details.\nThanks for using SPPAS.\n"
            dlg = wx.MessageDialog(parent, message, 'SPPAS automatic annotation finished', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

        try:
            os.remove(parameters.get_logfilename())
            # eg. source or destination doesn't exist
        except IOError, shutil.Error:
            pass

        try:
            parent.GetTopLevelParent().SetFocus()
            parent.GetTopLevelParent().Raise()
            parent.GetTopLevelParent().RefreshTree()
        except Exception:
            pass


    # -----------------------------------------------------------------------

