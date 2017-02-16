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

    src.utils.audiodata
    ~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    Management of transcribed data.

    anndata is a free and open source Python library to access and
    search data from annotated data. It can convert file formats like Elan’s EAF,
    Praat's TextGrid and others into a Transcription() object and convert into
    any of these formats. Those objects allow unified access to linguistic data
    from a wide range sources.

    Details can be found in the following publication:

        Brigitte Bigi, Tatsuya Watanabe, Laurent Prévot (2014).
        Representing Multimodal Linguistics Annotated data,
        Proceedings of the 9th edition of the Language Resources and Evaluation
        Conference, 26-31 May 2014, Reykjavik, Iceland.

    Linguistics annotation, especially when dealing with multiple domains,
    makes use of different tools within a given project.
    Many tools and frameworks are available for handling rich media data.
    The heterogeneity of such annotations has been recognised as a key problem
    limiting the inter-operability and re-usability of NLP tools and linguistic
    data collections.

    In annotation tools, annotated data are mainly represented in the form of
    "tiers" or "tracks" of annotations.
    The genericity and flexibility of "tiers" is appropriate to represent any
    multimodal annotated data because it simply maps the annotations on the
    timeline.
    In most tools, tiers are series of intervals defined by:

        * a time point to represent the beginning of the interval;
        * a time point to represent the end of the interval;
        * a label to represent the annotation itself.

    In Praat, tiers can be represented by a time point and a label (such
    tiers are named PointTiers and IntervalTiers).
    Of course, depending on the annotation tool, the internal data representation
    and the file formats are different.
    For example, in Elan, unlabelled intervals are not represented nor saved.
    On the contrary, in Praat, tiers are made of a succession of consecutive
    intervals (labelled or un-labelled).

    The annotationdata API used for data representation is based on the
    common set of information all tool are currently sharing.
    This allows to manipulate all data in the same way, regardless of the file
    type.

    This API supports to merge data and annotation from a wide range of
    heterogeneous data sources for further analysis.

    To get the list of extensions currently supported for reading and writing:

        >>> ext = annotationdata.aio.extensions

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
