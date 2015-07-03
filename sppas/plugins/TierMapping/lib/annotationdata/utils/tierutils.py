#!/usr/bin/env python2
# -*- coding: utf8 -*-
#
# Copyright (C) 2013  Brigitte Bigi
#
# This file is part of SPPAS.
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
# along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.


from annotationdata.tier import Tier


class TierUtils(object):
    """
    Provides utility methods for Tier instances.
    """

    @staticmethod
    def Select(tier, function):
        """ Select all annotations of the tier for which the function returns true.
            Parameters:
                 - tier (Tier): the tier to iterate over.
                 - function (callable): the function to use.
            Exception:   none
            Return:      Tier or None
        """
        annotations = [a for a in tier if function(a)]
        if not annotations:
            return None
        newtier = Tier(tier.Name)
        for a in annotations:
            newtier.Add(a.Copy())
        return newtier

    @staticmethod
    def Rindex(tier , time):
        """ Return the index of the interval ending at the given time point.
            This relationship takes into account the radius.
            Parameters:
                 - tier (Tier): the tier to iterate over.
                 - time (float)
            Exception:   none
            Return:      index (int) or None
        """
        for i, a in enumerate(tier):
            if a.End == time:
                return i
        return None
