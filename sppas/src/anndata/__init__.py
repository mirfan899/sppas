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

anndata: Manage transcribed data.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      develop@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi

anndata is a free and open source Python library to access and
search data from annotated data. It can convert file formats like Elan’s EAF,
Praat's TextGrid and others into a sppasTranscription() object and convert
into any of these formats. Those objects allow unified access to linguistic
data from a wide range sources.

To get the list of extensions currently supported for reading and/or writing:

>>> ext = aio.extensions

"""
from .aio import aioutils
from .aio.readwrite import sppasRW
from .metadata import sppasMetaData
from .transcription import sppasTranscription
from .tier import sppasTier
from .annotation import sppasAnnotation
from .ctrlvocab import sppasCtrlVocab
from .media import sppasMedia
from .hierarchy import sppasHierarchy
from .annlabel import sppasLabel
from .annlabel import sppasTag
from .annlocation import sppasLocation
from .annlocation import sppasDuration
from .annlocation import sppasInterval
from .annlocation import sppasPoint
from .annlocation import sppasDisjoint
from .filters import sppasFilters
from .filters import sppasAnnSet

__all__ = (
    'sppasMetaData',
    'sppasRW',
    'sppasTranscription',
    'sppasTier',
    'sppasAnnotation',
    'sppasCtrlVocab',
    'sppasMedia',
    'sppasHierarchy',
    'sppasLabel',
    'sppasTag',
    'sppasLocation',
    'sppasDuration',
    'sppasDisjoint',
    'sppasInterval',
    'sppasPoint',
    'sppasFilters',
    'sppasAnnSet',
    'aioutils'
)
