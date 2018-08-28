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

    src.annotations.infotier.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import datetime

from sppas.src.config import sg

from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.ptime.point import TimePoint
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.structs.metainfo import sppasMetaInfo

# ---------------------------------------------------------------------------


class sppasMetaInfoTier(sppasMetaInfo):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Meta information manager about SPPAS.

    Manager of meta information about SPPAS.
    Allows to create a tier with activated meta-information.

    """
    def __init__(self):
        """Creates a new sppasMetaInfoTier instance.
        Add and activate all known information about SPPAS.

        """
        sppasMetaInfo.__init__(self)

        self.add_metainfo('author', sg.__author__)
        self.add_metainfo('contact', sg.__contact__)
        self.add_metainfo('program', sg.__name__)
        self.add_metainfo('version', sg.__version__)
        self.add_metainfo('copyright', sg.__copyright__)
        self.add_metainfo('url', sg.__url__)
        self.add_metainfo('license', sg.__license__)
        self.add_metainfo('date', str(datetime.date.today()))

    # ------------------------------------------------------------------------

    def create_time_tier(self, begin, end):
        """Return a tier with activated information as annotations.

        :param begin: (float) Begin midpoint value
        :param end: (float) End midpoint value
        :returns: sppasTier

        """
        active_keys = self.keys_enabled()
        if len(active_keys) == 0:
            return None

        tier_dur = float(end) - float(begin)
        ann_dur = round(tier_dur / float(len(active_keys)), 3)
        radius = 0.001

        tier = Tier("MetaInformation")
        ann_begin = round(begin, 3)
        ann_end = begin + ann_dur
        for key in active_keys:
            value = self.get_metainfo(key)
            label = key + "=" + value
            tier.Append(Annotation(TimeInterval(TimePoint(ann_begin, radius), TimePoint(ann_end, radius)), Label(label)))
            ann_begin = ann_end
            ann_end = ann_begin + ann_dur

        tier[-1].GetLocation().SetEnd(TimePoint(end))
        return tier
