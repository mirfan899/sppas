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
#           http://sldr.org/sldr00800/preview/
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
# ----------------------------------------------------------------------------
# File: sp_glob.py
# ----------------------------------------------------------------------------

import os.path


# ---------------------------------------------------------------------------
# Define the base path of SPPAS sources
# ---------------------------------------------------------------------------

BASE_PATH = os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) )


# ---------------------------------------------------------------------------
# Define all paths (relatively to BASE_SPPAS)
# ---------------------------------------------------------------------------

PLUGIN_PATH    = os.path.join( BASE_PATH, "plugins" )
ICONS_PATH     = os.path.join( BASE_PATH, "etc", "icons" )
TIPS_ICON_PATH = os.path.join( BASE_PATH, "etc","tips", "christmast") #
TIPS_FILE      = os.path.join( BASE_PATH, "etc","tips","tips.txt")
SETTINGS_FILE  = os.path.join( BASE_PATH, "etc", "settings.dump")

RESOURCES_PATH = os.path.join( os.path.dirname(BASE_PATH), "resources" )
SAMPLES_PATH   = os.path.join( os.path.dirname(BASE_PATH), "samples" )


# ---------------------------------------------------------------------------
# Define configuration
# ---------------------------------------------------------------------------

ANNOTATIONS_LIST_FILE = os.path.join( BASE_PATH, "etc", "annotations.conf")

# Default output extension must be one of the list:
#  annotationdata.io.extensions_out_multitiers
DEFAULT_OUTPUT_EXTENSION = ".xra"

# Default output encoding
encoding = 'utf-8'


# ---------------------------------------------------------------------------
# Constants: ID
# ---------------------------------------------------------------------------

# Annotation log status (TO BE USED... TODO!):
ERROR_ID   = -1
INFO_ID    = 3
IGNORE_ID  = 2
WARNING_ID = 1
OK_ID      = 0


# ---------------------------------------------------------------------------
# Constants: SPPAS Information
# ---------------------------------------------------------------------------

author     = "Brigitte Bigi"
contact    = "brigite.bigi@gmail.com"
program    = "SPPAS"
version    = "1.7.5"
copyright  = "Copyright (C) 2011-2015 Brigitte Bigi"
url        = "http://sldr.org/sldr000800/preview/"
brief      = "SPPAS produces automatically annotations\nfrom a recorded speech sound and its transcription\nand helps to perform the analysis of annotated data."
docformat  = "epytext"
license    = "GNU Public License, version 3"
license_text = """
------------------------------------------------------------

By using SPPAS, you agree to cite a reference in your publications.
See the documentation to get the list of references, or get the PDF
files in the documentation/references sub-folder.

------------------------------------------------------------

SPPAS is free software; you can redistribute
it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 3 of the License,
or (at your option) any later version.

SPPAS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details. You should have
received a copy of the GNU General Public License along with File Hunter;
if not, write to the Free Software Foundation, Inc., 59 Temple Place,
Suite 330, Boston, MA  02111-1307  USA

------------------------------------------------------------"""
