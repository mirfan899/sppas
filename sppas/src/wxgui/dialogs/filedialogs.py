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

import os
import wx

import sppas
import sppas.src.annotationdata.aio
import sppas.src.audiodata.aio

from sppas.src.wxgui.cutils.dialogutils import create_wildcard, extend_path
from .msgdialogs import ShowYesNoQuestion

# ----------------------------------------------------------------------------
# Open
# ----------------------------------------------------------------------------


def OpenAnnotationFiles(multiple=True):
    """
    Return a list of annotation file names.
    """
    wildcard  = create_wildcard("All files", sppas.src.annotationdata.aio.extensionsul)
    wildcard += '|'+create_wildcard("SPPAS", sppas.src.annotationdata.aio.ext_sppas)
    wildcard += '|'+create_wildcard("Praat", sppas.src.annotationdata.aio.ext_praat)
    wildcard += '|'+create_wildcard("ELAN",  sppas.src.annotationdata.aio.ext_elan)
    wildcard += '|'+create_wildcard("Transcriber", sppas.src.annotationdata.aio.ext_transcriber)
    wildcard += '|'+create_wildcard("Phonedit", sppas.src.annotationdata.aio.ext_phonedit)
    wildcard += '|'+create_wildcard("ASCII", sppas.src.annotationdata.aio.ext_ascii)

    files = []
    if multiple is True:
        dlg = wx.FileDialog(None, "Select annotation file(s)", os.getcwd(), "", wildcard, wx.FD_OPEN | wx.MULTIPLE | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            files = dlg.GetPaths()

    else:
        dlg = wx.FileDialog(None, "Select annotation file", sppas.SAMPLES_PATH, "", wildcard, wx.FD_OPEN | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            files.append(dlg.GetPath())

    dlg.Destroy()

    if multiple is False:
        return files[0]
    return files

# ----------------------------------------------------------------------------


def OpenSoundFiles():
    """
    Return a list of sound file names.
    """

    wildcard = create_wildcard("Sound files", sppas.src.audiodata.aio.extensionsul)
    wildcard += '|'+create_wildcard("All files", ['*', '*.*'])

    files = []
    dlg = wx.FileDialog(None, "Select sound file(s)", sppas.SAMPLES_PATH, "", wildcard, wx.FD_OPEN | wx.MULTIPLE | wx.FD_CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
        files = dlg.GetPaths()

    dlg.Destroy()

    return files

# ----------------------------------------------------------------------------


def OpenAnyFiles():
    """
    Return a list of file names.
    """
    wildcard  = create_wildcard("All files", ['*', '*.*'])

    files = []
    dlg = wx.FileDialog(None, "Select file(s)", sppas.SAMPLES_PATH, "", wildcard, wx.FD_OPEN | wx.MULTIPLE | wx.FD_CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
        files = dlg.GetPaths()

    dlg.Destroy()
    return files

# ----------------------------------------------------------------------------


def OpenSpecificFiles(name, extensions):
    """
    Return a list of file names with specific extensions.
    """
    wildcard = create_wildcard(name, extensions)

    afile = ""
    dlg = wx.FileDialog(None, "Select a file", os.getcwd(), "", wildcard, wx.FD_OPEN | wx.FD_CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
        afile = dlg.GetPath()

    dlg.Destroy()
    return afile

# ----------------------------------------------------------------------------
# Save
# ----------------------------------------------------------------------------


def SaveAsAnnotationFile(defaultdir=None,
                         defaultfile=None):
    """
    Return an annotation file name.
    """
    if defaultdir is None:
        defaultdir = os.path.dirname(sppas.BASE_PATH)

    if defaultfile is None:
        defaultfile = "newfile.xra"

    file = None

    wildcard  = create_wildcard("All files", sppas.src.annotationdata.aio.extensions_out)
    wildcard += '|'+create_wildcard("SPPAS", sppas.src.annotationdata.aio.ext_sppas)
    wildcard += '|'+create_wildcard("Praat", sppas.src.annotationdata.aio.ext_praat)
    wildcard += '|'+create_wildcard("ELAN",  sppas.src.annotationdata.aio.ext_elan)
    wildcard += '|'+create_wildcard("Phonedit", sppas.src.annotationdata.aio.ext_phonedit)
    wildcard += '|'+create_wildcard("ASCII", sppas.src.annotationdata.aio.ext_ascii)
    wildcard += '|'+create_wildcard("AnnotationPro", sppas.src.annotationdata.aio.ext_annotationpro)
    wildcard += '|'+create_wildcard("Subtitles", sppas.src.annotationdata.aio.ext_subtitles)

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


def SaveAsAudioFile(defaultdir=None,
                    defaultfile=None):
    """
    Return an audio file name.
    """
    if defaultdir is None:
        defaultdir = os.path.dirname(sppas.BASE_PATH)

    if defaultfile is None:
        defaultfile = "newfile.wav"

    file = None

    wildcard = create_wildcard("All files", sppas.src.audiodata.aio.extensions)
    wildcard += '|'+create_wildcard("Wave", sppas.src.audiodata.aio.ext_wav)
    wildcard += '|'+create_wildcard("Aiff", sppas.src.audiodata.aio.ext_aiff)
    wildcard += '|'+create_wildcard("SunAu",  sppas.src.audiodata.aio.ext_sunau)

    dlg = wx.FileDialog(
        None, message = "Choose a file name...",
        defaultDir  = defaultdir,
        defaultFile = defaultfile,
        wildcard = wildcard,
        style = wx.FD_SAVE | wx.FD_CHANGE_DIR )

    if dlg.ShowModal() == wx.ID_OK:
        file = dlg.GetPath()

    dlg.Destroy()

    return file

# ----------------------------------------------------------------------------


def SaveAsImageFile(preferences,
                    image):
    """
    Save the current image as a PNG picture.

    """
    extension_map = {"png": wx.BITMAP_TYPE_PNG}
    extensions = extension_map.keys()
    wildcard = create_wildcard("Image files", extensions)

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


def SaveAsAnyFile(defaultdir=None,
                  defaultfile=None):
    """
    """
    if defaultdir is None:
        defaultdir = os.path.dirname(sppas.BASE_PATH)

    if defaultfile is None:
        defaultfile = "newfile.txt"

    file = None
    wildcard = create_wildcard("All files", ['*', '*.*'])
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
