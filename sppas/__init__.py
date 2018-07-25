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
    :summary:      SPPAS global configuration.

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

from sppas.src.config import sppasGlobals

# ---------------------------------------------------------------------------
# Fix the global settings variables
# ---------------------------------------------------------------------------

with sppasGlobals() as sg:
    __version__ = sg.__version__
    __author__ = sg.__author__
    __contact__ = sg.__contact__
    __copyright__ = sg.__copyright__
    __license__ = sg.__license__
    __docformat__ = sg.__docformat__
    __name__ = sg.__name__
    __url__ = sg.__url__
    __summary__ = sg.__summary__
    __title__ = sg.__title__
    __encoding__ = sg.__encoding__

# ---------------------------------------------------------------------------

# Default input/output encoding
encoding = __encoding__  # will be removed in a future version
reload(sys)
try:
    sys.setdefaultencoding(__encoding__)
except AttributeError:  # Python 2.7
    pass


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
# Symbols used by SPPAS to represent an event:

# Default symbols used by annotations and resources
unk_stamp = "<UNK>"

# Symbols in an orthographic transcription, or after a text normalization:
ORTHO_SYMBOLS = {
    '#': "silence",
    '+': "pause",
    '*': "noise",
    '@': "laugh",
    'dummy': 'dummy'
}

PHONE_SYMBOLS = {
    'sil': "silence",
    'sp': "pause",
    'noise': "noise",
    'laugh': "laugh",
    'dummy': 'dummy'
}

# All possible symbols:
SYMBOLS = dict()
SYMBOLS.update(ORTHO_SYMBOLS)
SYMBOLS.update(PHONE_SYMBOLS)

# ---------------------------------------------------------------------------
# Symbols used by SPPAS to serialize the data (labels/tags)

PHONEMES_SEPARATOR = "-"    # X-SAMPA standard
SYLLABLES_SEPARATOR = "."   # X-SAMPA standard
VARIANTS_SEPARATOR = "|"    # used for all alternative tags
