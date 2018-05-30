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
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS global variables.

"""
import sys
import os.path
try:
    reload  # Python 2.7
except NameError:
    try:
        from importlib import reload  # Python 3.4+
    except ImportError:
        from imp import reload  # Python 3.0 - 3.3

from .meta import __version__
from .meta import __author__
from .meta import __contact__
from .meta import __copyright__
from .meta import __license__
from .meta import __docformat__
from .meta import __name__
from .meta import __url__
from .meta import __summary__
from .meta import __title__

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
# Global variables
# ---------------------------------------------------------------------------

# Default input/output encoding
encoding = 'utf-8'
reload(sys)
try:
    sys.setdefaultencoding(encoding)
except AttributeError:  # Python 2.7
    pass

# Default symbols used by annotations and resources
unk_stamp = "<UNK>"

# ---------------------------------------------------------------------------
# Symbols used by SPPAS to represent an event:

# Symbols in an orthographic transcription, or after a text normalization:
ORTHO_SYMBOLS = {
    '#': "silence",
    '+': "pause",
    '*': "noise",
    '@': "laugh",
    'dummy': 'dummy'
}

# All possible symbols:
SYMBOLS = {
    '#': "silence",
    'sil': "silence",
    '+': "pause",
    'sp': "pause",
    '*': "noise",
    'noise': "noise",
    '@': "laugh",
    'laugh': "laugh",
    'dummy': 'dummy'
}
