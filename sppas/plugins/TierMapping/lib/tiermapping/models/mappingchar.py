#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013  Tatsuya Watanabe
#
# This file is part of TierMapping.
#
# TierMapping is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TierMapping is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TierMapping.  If not, see <http://www.gnu.org/licenses/>.

from collections import OrderedDict


class MappingChar(OrderedDict):

    def __init__(self, name, source, *args, **kwargs):
        OrderedDict.__init__(self, *args, **kwargs)
        self._source = " ".join(source.split())
        self._name = name

    def __setitem__(self, key, value):
        if self.has_key(key):
            value = u"{0}|{1}".format(self.get(key), value)
        super(MappingChar, self).__setitem__(key, value)

    def GetName(self):
        return self._name

    def GetSourceTier(self):
        return self._source
