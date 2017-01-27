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
# File: infotier.py
# ----------------------------------------------------------------------------

import datetime

from sppas.src.sp_glob import author, contact, program, version, copyright, url, license

from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.ptime.point import TimePoint
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.structs.metainfo import sppasMetaInfo

# ---------------------------------------------------------------------------


class sppasMetaInfoTier(sppasMetaInfo):
    """
    @authors:      Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Meta informations manager about SPPAS.

    Manager of meta information about SPPAS that allows to create a tier with
    such activated information.

    """
    def __init__(self):
        """
        Creates a new sppasMetaInfoTier instance.
        Add and activate all known information about SPPAS.

        """
        sppasMetaInfo.__init__(self)

        self.add_metainfo('author', author)
        self.add_metainfo('contact', contact)
        self.add_metainfo('program', program)
        self.add_metainfo('version', version)
        self.add_metainfo('copyright', copyright)
        self.add_metainfo('url', url)
        self.add_metainfo('license', license)
        self.add_metainfo('date', str(datetime.date.today()))

    # ------------------------------------------------------------------------

    def create_time_tier(self, begin, end):
        """
        Return a tier with activated information as annotations.

        @param begin (float) Begin time value (seconds)
        @param end (float) End time value (seconds)
        @return Tier

        """
        activekeys = self.keys_activated()
        if len(activekeys) == 0:
            return None

        tierdur = float(end) - float(begin)
        anndur  = tierdur / float(len(activekeys))

        tier = Tier("MetaInformation")
        annbegin = begin
        annend   = begin+anndur
        for key in activekeys:
            value = self.get_metainfo(key)
            label = key+"="+value
            tier.Append(Annotation(TimeInterval(TimePoint(annbegin), TimePoint(annend)), Label(label)))
            annbegin = annend
            annend = annbegin + anndur

        tier[-1].GetLocation().SetEnd(TimePoint(end))
        return tier

    # ------------------------------------------------------------------------
