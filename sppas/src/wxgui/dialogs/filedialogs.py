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
# File: filedialogs.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os
import wx

from wxgui.cutils.dialogutils import create_wildcard, extend_path
from basedialog import ShowYesNoQuestion

import annotationdata.io as io
import signals
import sp_glob

# ----------------------------------------------------------------------------
# Open
# ----------------------------------------------------------------------------

def OpenAnnotationFiles(multiple=True):
    """
    Return a list of annotation file names.
    """
    wildcard  = create_wildcard("All files", io.extensionsul)
    wildcard += '|'+create_wildcard("SPPAS", io.ext_sppas)
    wildcard += '|'+create_wildcard("Praat", io.ext_praat)
    wildcard += '|'+create_wildcard("ELAN",  io.ext_elan)
    wildcard += '|'+create_wildcard("Transcriber", io.ext_transcriber)
    wildcard += '|'+create_wildcard("Phonedit", io.ext_phonedit)
    wildcard += '|'+create_wildcard("ASCII", io.ext_ascii)

    files = []
    if multiple is True:
        dlg = wx.FileDialog(None, "Select annotation file(s)", os.getcwd(), "", wildcard, wx.FD_OPEN | wx.MULTIPLE | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            files = dlg.GetPaths()

    else:
        dlg = wx.FileDialog(None, "Select annotation file", sp_glob.SAMPLES_PATH, "", wildcard, wx.FD_OPEN | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            files.append( dlg.GetPath() )

    dlg.Destroy()

    if multiple is False:
        return files[0]
    return files

# ----------------------------------------------------------------------------

def OpenSoundFiles():
    """
    Return a list of sound file names.
    """

    wildcard  = create_wildcard("Sound files", signals.extensionsul)
    wildcard += '|'+create_wildcard("All files", ['*', '*.*'])

    files = []
    dlg = wx.FileDialog(None, "Select sound file(s)", sp_glob.SAMPLES_PATH, "", wildcard, wx.FD_OPEN | wx.MULTIPLE | wx.FD_CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
        files = dlg.GetPaths()

    dlg.Destroy()

    return files

# ----------------------------------------------------------------------------

def OpenAnyFiles():
    """
    Return a list of annotation file names.
    """
    wildcard  = create_wildcard("All files", ['*', '*.*'])

    files = []
    dlg = wx.FileDialog(None, "Select file(s)", sp_glob.SAMPLES_PATH, "", wildcard, wx.FD_OPEN | wx.MULTIPLE | wx.FD_CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
        files = dlg.GetPaths()

    dlg.Destroy()
    return files

# ----------------------------------------------------------------------------
# Save
# ----------------------------------------------------------------------------

def SaveAsAnnotationFile(defaultdir=None,defaultfile=None):
    """
    Return an annotation file name.
    """
    if defaultdir is None:
        defaultdir = os.path.dirname(sp_glob.BASE_PATH)

    if defaultfile is None:
        defaultfile = "newfile.xra"

    file = None

    wildcard  = create_wildcard("All files", io.extensions_out)
    wildcard += '|'+create_wildcard("SPPAS", io.ext_sppas)
    wildcard += '|'+create_wildcard("Praat", io.ext_praat)
    wildcard += '|'+create_wildcard("ELAN",  io.ext_elan)
    wildcard += '|'+create_wildcard("Phonedit", io.ext_phonedit)
    wildcard += '|'+create_wildcard("ASCII", io.ext_ascii)

    dlg = wx.FileDialog(
        None, message = "Choose a file name...",
        defaultDir = defaultdir,
        defaultFile = defaultfile,
        wildcard = wildcard,
        style = wx.FD_SAVE | wx.FD_CHANGE_DIR )

    if dlg.ShowModal() == wx.ID_OK:
        file = dlg.GetPath()

    dlg.Destroy()

    return file

# ----------------------------------------------------------------------------

def SaveAsImageFile(preferences, image):
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

        if not os.path.exists(path) or ShowYesNoQuestion(dialog, preferences, overwrite_question) == wx.YES:
            image.SaveFile(path, extension_map[extension])
            saved = True

    dialog.Destroy()
    return saved

# ----------------------------------------------------------------------------

