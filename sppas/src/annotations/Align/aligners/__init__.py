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

from juliusalign import JuliusAligner
from hvitealign  import HviteAligner
from basicalign  import BasicAligner

# ---------------------------------------------------------------------------

__all__ = [
'JuliusAligner',
'HviteAligner',
'BasicAligner'
]

# ---------------------------------------------------------------------------

# List of supported aligner names
DEFAULT_ALIGNER = "basic"

ALIGNERS_TYPES = {
    "julius":JuliusAligner,
    "hvite":HviteAligner,
    "basic":BasicAligner
}

# ---------------------------------------------------------------------------

def aligner_names():
    """
    Return the list of aligner names.

    """
    return ALIGNERS_TYPES.keys()

# ---------------------------------------------------------------------------

def check( alignername ):
    """
    Check whether the alignername is known or not.

    @param alignername (str - IN) Name of the aligner. Expect one of the ALIGNERS list.
    @return formatted alignername

    """
    alignername = alignername.lower()
    if not alignername in ALIGNERS_TYPES.keys():
        raise ValueError('Unknown aligner name.')
    return alignername

# ---------------------------------------------------------------------------

def instantiate( modeldir, alignername=DEFAULT_ALIGNER ):
    """
    Instantiate an aligner to the appropriate Aligner system.

    @param alignername (str - IN) Name of the aligner. Expect one of the ALIGNERS list.
    @param modeldir (str - IN) Directory of the acoustic model
    @return an Aligner instance. If an error occurred,
    the default aligner is returned.

    """
    alignername = alignername.lower()

    try:
        return ALIGNERS_TYPES[alignername](modeldir)
    except KeyError:
        return ALIGNERS_TYPES[DEFAULT_ALIGNER](None)

# ---------------------------------------------------------------------------
