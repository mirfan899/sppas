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
# File: commondialogs.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import os.path

from wxgui.cutils.dialogutils import create_wildcard, extend_path
from wxgui.cutils.textutils   import TextAsNumericValidator
from wxgui.sp_consts          import MAIN_FONTSIZE


# ----------------------------------------------------------------------------

def AskQuestion(question, parent=None):
    """
    Ask a yes/no question and return the reply.
    """

    return wx.MessageBox(question, "Question",
                         wx.YES_NO|wx.CENTRE|wx.NO_DEFAULT, parent)

# ----------------------------------------------------------------------------


def SaveAsImageFile(image):
    """
    Save the current image as a PNG picture.
    """

    extension_map = {"png": wx.BITMAP_TYPE_PNG}
    extensions    = extension_map.keys()
    wildcard      = create_wildcard("Image files", extensions)

    dialog = wx.FileDialog(None, message="Export to Image",
                           wildcard=wildcard, style=wx.FD_SAVE)

    saved = False
    if dialog.ShowModal() == wx.ID_OK:
        path, extension = extend_path(dialog.GetPath(), extensions, "png")
        overwrite_question = "File '%s' exists. Overwrite?" % path

        if not os.path.exists(path) or AskQuestion(overwrite_question) == wx.YES:
            image.SaveFile(path, extension_map[extension])
            saved = True

    dialog.Destroy()
    return saved


# ----------------------------------------------------------------------------


class ZoomChooser( wx.Dialog ):
    """
    Show a dialog to choose a new period (start/end values).
    """

    def __init__(self, parent, start, end):
        wx.Dialog.__init__(self, parent, title="Zoom Chooser", size=(320,150), style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)

        self.start = start
        self.end   = end

        font = wx.Font(MAIN_FONTSIZE, wx.SWISS, wx.NORMAL, wx.NORMAL)

        # create the main sizer.
        gbs = wx.GridBagSizer(hgap=5, vgap=5)

        txtfrom = wx.StaticText(self, label="  From: ", size=(80, 24))
        txtfrom.SetFont( font )
        txtto   = wx.StaticText(self, label="  To:   ", size=(80, 24))
        txtto.SetFont( font )

        self.fieldfrom = wx.TextCtrl(self, -1, str(self.start), size=(150, 24), validator=TextAsNumericValidator())
        self.fieldfrom.SetFont(font)
        self.fieldfrom.SetInsertionPoint(0)
        self.fieldto   = wx.TextCtrl(self, -1, str(self.end),  size=(150, 24), validator=TextAsNumericValidator())
        self.fieldto.SetFont(font)
        self.fieldto.SetInsertionPoint(0)

        gbs.Add(txtfrom,       (0,0), flag=wx.ALL, border=2)
        gbs.Add(self.fieldfrom,(0,1), flag=wx.EXPAND, border=2)
        gbs.Add(txtto,         (1,0), flag=wx.ALL, border=2)
        gbs.Add(self.fieldto,  (1,1), flag=wx.EXPAND, border=2)

        # the buttons for close, and cancellation
        Buttons = wx.StdDialogButtonSizer()
        ButtonClose = wx.Button(self, wx.ID_OK)
        Buttons.AddButton(ButtonClose)
        ButtonCancel = wx.Button(self, wx.ID_CANCEL)
        Buttons.AddButton(ButtonCancel)
        Buttons.Realize()
        gbs.Add(Buttons, (2,0), (1,2), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, border=5)

        self.SetMinSize((300, 120))
        self.SetSizer( gbs )
        self.Layout()
        self.Refresh()

    # End __init__
    #-------------------------------------------------------------------------


    def GetValues(self):
        """ Return the new start/end values. """
        return self.fieldfrom.GetValue(), self.fieldto.GetValue()

    # End GetValues
    #-------------------------------------------------------------------------

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------


class RadiusChooser( wx.Dialog ):
    """
    Show a dialog to choose a new radius value.
    """

    def __init__(self, parent, radius):
        wx.Dialog.__init__(self, parent, title="Radius", size=(320,150), style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)

        self.radius = radius

        font = wx.Font(MAIN_FONTSIZE, wx.SWISS, wx.NORMAL, wx.NORMAL)

        # create the main sizer.
        gbs = wx.GridBagSizer(hgap=5, vgap=5)

        txtinfo = wx.StaticText(self, label="Fix the vagueness of each boundary.")
        txtinfo.SetFont( font )

        txtradius = wx.StaticText(self, label="  Value: ", size=(80, 24))
        txtradius.SetFont( font )

        self.field = wx.TextCtrl(self, -1, str(self.radius), size=(150, 24), validator=TextAsNumericValidator())
        self.field.SetFont(font)
        self.field.SetInsertionPoint(0)

        gbs.Add(txtinfo,    (0,0), (1,2), flag=wx.ALL, border=2)
        gbs.Add(txtradius,  (1,0), flag=wx.ALL, border=2)
        gbs.Add(self.field, (1,1), flag=wx.EXPAND, border=2)

        # the buttons for close, and cancellation
        Buttons = wx.StdDialogButtonSizer()
        ButtonClose = wx.Button(self, wx.ID_OK)
        Buttons.AddButton(ButtonClose)
        ButtonCancel = wx.Button(self, wx.ID_CANCEL)
        Buttons.AddButton(ButtonCancel)
        Buttons.Realize()
        gbs.Add(Buttons, (2,0), (1,2), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, border=5)

        self.SetMinSize((300, 120))
        self.SetSizer( gbs )
        self.Layout()
        self.Refresh()

    # End __init__
    #-------------------------------------------------------------------------


    def GetValue(self):
        """ Return the new radius value. """
        return self.field.GetValue()

    # End GetValue
    #-------------------------------------------------------------------------

# ----------------------------------------------------------------------------

