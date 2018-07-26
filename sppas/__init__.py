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

    sppas
    ~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS global configuration.

"""

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
