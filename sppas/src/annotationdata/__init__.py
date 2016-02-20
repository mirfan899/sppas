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

from annotationdata.transcription  import Transcription
from annotationdata.tier           import Tier
from annotationdata.annotation     import Annotation
from annotationdata.label.label    import Label
from annotationdata.label.text     import Text
from annotationdata.ptime.disjoint import TimeDisjoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point    import TimePoint

from annotationdata.filter.predicate import Sel
from annotationdata.filter.predicate import Rel
from annotationdata.filter.filters   import Filter
from annotationdata.filter.filters   import SingleFilter
from annotationdata.filter.filters   import RelationFilter

import annotationdata.io as io

__all__ = [
'Transcription',
'Tier',
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
'RelationFilter',
'io'
]
