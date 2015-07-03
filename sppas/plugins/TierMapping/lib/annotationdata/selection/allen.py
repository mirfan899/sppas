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


class Relations:

    REL_BEFORE=1
    REL_AFTER=2
    REL_MEETS=3
    REL_METBY=4
    REL_OVERLAPS=5
    REL_OVERLAPPED=6
    REL_STARTS=7
    REL_STARTEDBY=8
    REL_FINISHES=9
    REL_FINISHEDBY=10
    REL_CONTAINS=11
    REL_DURING=12
    REL_EQUALS=13

    __str = {}
    __str["REL_BEFORE"]     = REL_BEFORE
    __str["REL_AFTER"]      = REL_AFTER
    __str["REL_MEETS"]      = REL_MEETS
    __str["REL_METBY"]      = REL_METBY
    __str["REL_OVERLAPS"]   = REL_OVERLAPS
    __str["REL_OVERLAPPED"] = REL_OVERLAPPED
    __str["REL_STARTS"]     = REL_STARTS
    __str["REL_STARTEDBY"]  = REL_STARTEDBY
    __str["REL_FINISHES"]   = REL_FINISHES
    __str["REL_FINISHEDBY"] = REL_FINISHEDBY
    __str["REL_CONTAINS"]   = REL_CONTAINS
    __str["REL_DURING"]     = REL_DURING
    __str["REL_EQUALS"]     = REL_EQUALS


    def get(self):
        return self.__str.values()

    def get_str(self):
        return self.__str.keys()

    def get_rel(self,relstr):
        return self.__str[relstr]

    def get_name(self,value):
        for k,v in self.__str.items():
            if v==value:
                return k
        return None
