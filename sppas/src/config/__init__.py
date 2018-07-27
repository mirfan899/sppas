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

    config: SPPAS configuration for global things.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    :Example:

        >>> from sppas.src.config import sg, paths
        >>> sg.__encoding
        >>> paths.resources

"""
import sys
try:
    reload  # Python 2.7
except NameError:
    try:
        from importlib import reload  # Python 3.4+
    except ImportError:
        from imp import reload  # Python 3.0 - 3.3

from .settings import sppasBaseSettings
from .sglobal import sppasGlobalSettings
from .sglobal import sppasPathSettings
from .sglobal import sppasSymbolSettings
from .sglobal import sppasSeparatorSettings

# ---------------------------------------------------------------------------
# Fix the global un-modifiable settings
# ---------------------------------------------------------------------------

sg = sppasGlobalSettings()
paths = sppasPathSettings()
symbols = sppasSymbolSettings()
separators = sppasSeparatorSettings()

# ---------------------------------------------------------------------------

# Default input/output encoding
reload(sys)
try:
    sys.setdefaultencoding(sg.__encoding__)
except AttributeError:  # Python 2.7
    pass

# ---------------------------------------------------------------------------

__all__ = [
    "sppasBaseSettings",
    "sg",
    "paths",
    "symbols",
    "separators"
]
