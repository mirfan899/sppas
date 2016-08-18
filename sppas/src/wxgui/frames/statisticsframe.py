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
# File: statisticsframe.py
# ----------------------------------------------------------------------------

import wx

from baseframe import ComponentFrame

from wxgui.sp_icons                 import STATISTICS_APP_ICON
from wxgui.cutils.imageutils        import spBitmap
from wxgui.clients.statisticsclient import StatisticsClient

# ----------------------------------------------------------------------------

class StatisticsFrame( ComponentFrame ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Statistics allows to estimates basic statistics on annotated files.

    """
    def __init__(self, parent, idc, prefsIO):

        arguments = {}
        arguments['files'] = []
        arguments['title'] = "SPPAS - DataStats"
        arguments['type']  = "DATAFILES"
        arguments['icon']  = STATISTICS_APP_ICON
        arguments['prefs'] = prefsIO

        ComponentFrame.__init__(self, parent, idc, arguments)

    # ------------------------------------------------------------------------

    def CreateClient(self, parent, prefsIO):
        """ Override. """

        return StatisticsClient( parent,prefsIO )

# ----------------------------------------------------------------------------
