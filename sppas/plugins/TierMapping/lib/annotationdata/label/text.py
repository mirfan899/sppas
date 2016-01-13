#!/usr/bin/env python2
# -*- coding: utf-8 -*-
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


class Text(object):
    def __init__(self, value, score=1):
        """
        Initialize a new Text instance.
        """
        if not isinstance(value, unicode):
            value = value.decode("utf-8")
        self._str = " ".join(value.split())
        self._score = float(score)

    def __repr__(self):
        return "Text(value=%s, score=%s)" % (self._str, self._score)

    def __str__(self):
        return self._str.encode("utf-8")

    @property
    def Value(self):
        """
        Return the value.
        Return: (str)
        """
        return self._str

    @property
    def Score(self):
        """
        Return the score.
        Return: (float)
        """
        return self._score
