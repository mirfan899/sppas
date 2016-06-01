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

from sp_glob import author, contact, program, version, copyright, url, license

from annotationdata.tier           import Tier
from annotationdata.annotation     import Annotation
from annotationdata.label.label    import Label
from annotationdata.ptime.point    import TimePoint
from annotationdata.ptime.interval import TimeInterval

# ---------------------------------------------------------------------------

class InfoTier( object ):
    """
    @authors:      Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Create a tier with information about SPPAS.

    """
    def __init__(self):
        """
        Creates a new InfoTier instance.

        """
        super(InfoTier, self).__init__()
        self.reset_options()


    def reset_options(self):
        self._options = {}
        self._options['author']    = [True,author]
        self._options['contact']   = [True,contact]
        self._options['program']   = [True,program]
        self._options['version']   = [True,version]
        self._options['copyright'] = [True,copyright]
        self._options['url']       = [True,url]
        self._options['license']   = [True,license]
        self._options['date']      = [True,str(datetime.date.today())]

    # ------------------------------------------------------------------------

    def is_active_option(self, key):
        """
        Return the option status of a given key or raise an Exception.

        """
        return self._options[key][0]

    # ------------------------------------------------------------------------

    def get_option(self, key):
        """
        Return the option value of a given key or raise an Exception.

        """
        return self._options[key][1]

    # ------------------------------------------------------------------------

    def activate_option(self, key, value):
        """
        Activate/Disable an option.

        @param key (str)
        @param value (bool)

        """
        if not str(key) in self._options.keys():
            raise KeyError('%s is not an option.'%key)
        self._options[str(key)][0] = bool(value)

    # ------------------------------------------------------------------------

    def add_option(self, key, strv):
        """
        Fix an option.

        @param key (str)
        @param strv (str)

        """
        if str(key) in self._options.keys():
            raise KeyError('%s is already an option.'%key)
        self._options[str(key)] = [True,strv]

    # ------------------------------------------------------------------------

    def pop_option(self, key):
        """
        Fix an option.

        @param key (str)

        """
        if not str(key) in self._options.keys():
            raise KeyError('%s is not an option.'%key)
        del self._options[str(key)]

    # ------------------------------------------------------------------------

    def create_time_tier(self, begin, end):
        """
        Return a tier with activated information as annotation.

        """
        # how many information are activated
        nbinfo = sum([1 for v in self._options.values() if v[0] is True])
        if nbinfo == 0:
            return None

        tierdur = float(end) - float(begin)
        anndur  = tierdur / float(nbinfo)

        tier = Tier("MetaInformation")
        annbegin = begin
        annend   = anndur
        for key in self._options.keys():
            (activated,value) = self._options[key]
            if activated is True:
                label = key+"="+value
                tier.Append(Annotation(TimeInterval(TimePoint(annbegin), TimePoint(annend)), Label(label)))
                annbegin = annend
                annend = annend + anndur

        tier[-1].GetLocation().SetEnd(TimePoint(end))
        return tier

    # ------------------------------------------------------------------------

