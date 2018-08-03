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

annotationdata
~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      brigitte.bigi@gmail.com
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2017  Brigitte Bigi

Management of transcribed data.
ONLY FOR SPPAS VERSION 1+.

Details can be found in the following reference:

Brigitte Bigi, Tatsuya Watanabe, Laurent Prévot (2014).
Representing Multimodal Linguistics Annotated data,
Proceedings of the 9th edition of the Language Resources and Evaluation
Conference, 26-31 May 2014, Reykjavik, Iceland.

"""

from .transcription import Transcription
from .tier import Tier
from .media import Media
from .hierarchy import Hierarchy
from .ctrlvocab import CtrlVocab

from .annotation import Annotation
from .label.label import Label
from .label.text import Text
from .ptime.disjoint import TimeDisjoint
from .ptime.interval import TimeInterval
from .ptime.point import TimePoint

from .filter.predicate import Sel
from .filter.predicate import Rel
from .filter.filters import Filter
from .filter.filters import SingleFilter
from .filter.filters import RelationFilter

#import annotationdata.aio

__all__ = [
    'Transcription',
    'Tier',
    'Media',
    'Hierarchy',
    'CtrlVocab',
    'Annotation',
    'Label',
    'Text',
    'TimeDisjoint',
    'TimeInterval',
    'TimePoint',
    'Sel',
    'Rel',
    'Filter',
    'SingleFilter',
    'RelationFilter'
]
