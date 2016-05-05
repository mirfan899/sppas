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


class SearchModes:

    MD_EXACT=0      # the labels must strictly correspond,
    MD_CONTAINS=1   # the label of the tier contains the given label
    MD_STARTSWITH=2 # the label of the tier starts with the given label,
    MD_ENDSWITH=3   # the label of the tier ends with the given label
    MD_REGEXP=4

    __str = {}
    __str["MD_EXACT"]            = MD_EXACT
    __str["MD_CONTAINS"]         = MD_CONTAINS
    __str["MD_STARTSWITH"]       = MD_STARTSWITH
    __str["MD_ENDSWITH"]         = MD_ENDSWITH
    __str["MD_REGEXP"]           = MD_REGEXP
    __str["Exact Match"]         = MD_EXACT
    __str["Contains"]            = MD_CONTAINS
    __str["Starts with"]         = MD_STARTSWITH
    __str["Ends with"]           = MD_ENDSWITH
    __str["Regular expression"]  = MD_REGEXP

    __lst = ["Exact Match", "Contains", "Starts with", "Ends with", "Regular expression"]


    def get(self):
        return self.__str.values()

    def get_lst(self):
        return self.__lst

    def get_md(self,mdstr):
        return self.__str[mdstr]

    def get_lstmd(self,mdint):
        mdstr = self.__lst[mdint]
        return self.__str[mdstr]

