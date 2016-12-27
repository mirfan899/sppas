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

from textentry import TextEntry

class Silence(TextEntry):
    """
        Represents a silence in Annotation.
    """

    def __init__(self, label="#"):
        """ Creates a new Silence instance.
            A Silence is represented as a string.
        """
        TextEntry.__init__(self, label)

    # End __init__
    # -----------------------------------------------------------------------


    def IsLabel(self):
        """ Return True if the label is an instance of Label.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return False

    # End __IsLabel
    # -----------------------------------------------------------------------


    def IsSilence(self):
        """ Return True if the label is an instance of Silence.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return True

    # End __Silence
    # -----------------------------------------------------------------------
