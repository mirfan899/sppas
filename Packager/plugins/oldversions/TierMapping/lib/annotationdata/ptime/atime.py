#!/usr/bin/env python2
# -*- coding:utf-8 -*-
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


class Time(object):
    def __init__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        raise NotImplementedError

    def __lt__(self, other):
        raise NotImplementedError

    def __le__(self, other):
        raise NotImplementedError

    def __gt__(self, other):
        raise NotImplementedError

    def __ge__(self, other):
        raise NotImplementedError

    def Duration(self):
        raise NotImplementedError

    def IsPoint(self):
        """ Return True if this object is an instance of TimePoint.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return False

    # End IsPoint
    # -----------------------------------------------------------------------

    def IsInterval(self):
        """ Return True if this object is an instance of TimeInterval.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return False

    # End IsInterval
    # -----------------------------------------------------------------------


    def IsDisjoint(self):
        """ Return True if this object is an instance of TimeDisjoint.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return False

    # End IsDisjoint
    # -----------------------------------------------------------------------
