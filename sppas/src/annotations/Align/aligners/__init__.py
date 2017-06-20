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

    src.annotations.Align.aligners.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from .basicalign import BasicAligner
from .juliusalign import JuliusAligner
from .hvitealign import HviteAligner

from .basicalign import BASIC_EXT_OUT
from .juliusalign import JULIUS_EXT_OUT
from .hvitealign import HVITE_EXT_OUT

# ---------------------------------------------------------------------------

__all__ = [
'JuliusAligner',
'HviteAligner',
'BasicAligner'
]

# ---------------------------------------------------------------------------

# List of supported aligner and related class name
ALIGNERS_TYPES = {
    "basic": BasicAligner,
    "julius": JuliusAligner,
    "hvite": HviteAligner
}

# List of supported aligner and related class name
TRACKS_ALIGNERS_TYPES = {
    "julius": JuliusAligner,
}

# Identifier name of the default aligner
DEFAULT_ALIGNER = "basic"

# Identifier name of the default aligner
DEFAULT_TRACK_ALIGNER = "julius"

# List of extensions each aligner is able to write
ALIGNERS_EXT_OUT = {
    "basic": BASIC_EXT_OUT,
    "julius": JULIUS_EXT_OUT,
    "hvite": HVITE_EXT_OUT
}

# ---------------------------------------------------------------------------


def aligner_names():
    """ Return the list of aligner names. """

    return ALIGNERS_TYPES.keys()

# ---------------------------------------------------------------------------


def check(alignername):
    """ Check whether the aligner name is known or not.

    :param alignername: (str) Name of the aligner. Expect one of the ALIGNERS list.
    :returns: formatted alignername

    """
    alignername = alignername.lower()
    if alignername not in ALIGNERS_TYPES.keys():
        raise ValueError('Unknown aligner name %s.' % alignername)

    return alignername

# ---------------------------------------------------------------------------


def instantiate(modeldir, alignername=DEFAULT_ALIGNER):
    """ Instantiate an aligner to the appropriate Aligner system from its name.
    If an error occurred, the basic aligner is returned.

    :param alignername: (str) Name of the aligner. Expect one of the ALIGNERS list.
    :param modeldir: (str) Directory of the acoustic model
    :returns: an Aligner instance.

    """
    alignername = alignername.lower()

    try:
        a = ALIGNERS_TYPES[alignername](modeldir)
    except KeyError:
        a = BasicAligner(None)

    return a
