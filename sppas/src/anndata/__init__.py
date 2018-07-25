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

    anndata
    ~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Management of transcribed data. old version.

"""
from sppas.src.utils.maketext import translate
t = translate("anndata")

from .aio import aioutils
from .metadata import sppasMetaData
from .aio.readwrite import sppasRW
from .transcription import sppasTranscription
from .tier import sppasTier
from .annotation import sppasAnnotation
from .ctrlvocab import sppasCtrlVocab
from .media import sppasMedia
from .hierarchy import sppasHierarchy
from .annlabel.label import sppasLabel
from .annlabel.tag import sppasTag
from .annlocation import sppasLocation
from .annlocation import sppasDuration
from .annlocation import sppasInterval
from .annlocation import sppasPoint
from .annlocation import sppasDisjoint
from .filters import sppasFilters
from .filters import sppasAnnSet

__all__ = [
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
]
