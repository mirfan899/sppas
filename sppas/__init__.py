# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    __init__.py
    ~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS global variables.

"""
import sys
import os.path
from .meta import *

# ---------------------------------------------------------------------------
# Define paths
# ---------------------------------------------------------------------------

# SPPAS base directory
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# SPPAS folders
PLUGIN_PATH = os.path.join(os.path.dirname(BASE_PATH), "plugins")
RESOURCES_PATH = os.path.join(os.path.dirname(BASE_PATH), "resources")
SAMPLES_PATH = os.path.join(os.path.dirname(BASE_PATH), "samples")
DOCUMENTATION_PATH = os.path.join(os.path.dirname(BASE_PATH), "documentation")

# etcetera
SPPAS_CONFIG_DIR = os.path.join(BASE_PATH, "etc")
ICONS_PATH = os.path.join(BASE_PATH, "etc", "icons")
TIPS_FILE = os.path.join(BASE_PATH, "etc", "tips.txt")
SETTINGS_FILE = os.path.join(BASE_PATH, "etc", "settings.dump")

# ---------------------------------------------------------------------------

# Default input/output encoding
encoding = 'utf-8'
reload(sys)
sys.setdefaultencoding(encoding)
