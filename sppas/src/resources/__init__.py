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

    src.resources.__init__py
    ~~~~~~~~~~~~~~~~~~~~~~~~

    resources is a free and open source Python library to access and manage
    linguistic resources like lexicons, dictionaries, etc.

"""
from sppas.src.utils.maketext import translate
t = translate("resources")

from .dictpron import sppasDictPron
from .dictrepl import sppasDictRepl
from .mapping import sppasMapping
from .patterns import sppasPatterns
from .unigram import sppasUnigram
from .vocab import sppasVocabulary

# ---------------------------------

__all__ = [
    "sppasMapping",
    "sppasDictRepl",
    "sppasDictPron",
    "sppasPatterns",
    "sppasUnigram",
    "sppasVocabulary"
]
