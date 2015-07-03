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


class ConstraintTime(object):
    """
    Performs match operations on an instance of Annotation.
    """

    def __init__(self, minduration=0, maxduration=0, mintime=0, maxtime=0, options=[]):
        """ Create a new TimeMatcher instance.
            Parameters:
                - minduration (float)
                - maxduration (float)
                - mintime (float)
                - maxtime (float)
        """
        self.minduration = minduration
        self.maxduration = maxduration
        self.mintime = mintime
        self.maxtime = maxtime
        self.options = options

    # End __init__
    # -----------------------------------------------------------------------

    #  __call__ allows instances to behave as if they were functions.
    #  >>> matcher = TimeMatcher(minduration=0.4, maxduration=10)
    #  >>> matcher(annotation)
    #  >>> True

    def __call__(self, annotation):
        """ Performs match operations.
            Parameters:
                 - annotation (Annotation)
            Exception:   none
            Return:      Boolean
        """
        match = True
        time = annotation.Time
        if time.IsInterval():
            mintime = time.Begin.Value
            maxtime = time.End.Value
        else:
            mintime = time.Value
            maxtime = time.Value

        if self.minduration and self.minduration > time.Duration():
            match = False
        if self.maxduration and time.Duration() > self.maxduration:
            match = False
        if self.mintime and self.mintime > maxtime:
            match = False
        if self.maxtime and mintime > self.maxtime:
            match = False

        if "REVERSE" in self.options:
            return not match
        else:
            return match

    # End __call__
    # -----------------------------------------------------------------------
