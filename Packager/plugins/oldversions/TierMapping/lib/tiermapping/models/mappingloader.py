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

import csv
import os

from mappingchar import MappingChar


class MappingCharLoader(object):
    def __init__(self):
        pass

    def Load(self, filename, *args, **kwargs):
        basename = os.path.splitext(os.path.basename(filename))[0]
        with open(filename, 'r') as f:
            reader = CSVReader(f, *args, **kwargs)
            header = next(reader)
            nb_col = len(header)
            if nb_col < 2:
                msg = u'File must contain at least two columns: {0}'
                raise IOError(msg.format(filename))
            header = [" ".join(col.split()) for col in header]
            maps = [MappingChar(name=u"{0}".format(col), source=header[0]) for col in header[1:]]
            for row in reader:
                if len(row) != nb_col:
                    continue
                src = " ".join(row[0].split())
                targets = row[1:]
                for mapchar, target in zip(maps, targets):
                    mapchar[src] = target
            return maps


class CSVReader(object):

    def __init__(self, f, dialect=csv.excel, delimiter=";", **kwargs):
        encoding = kwargs.pop("encoding", "utf-8")
        self.reader = csv.reader(f, dialect=dialect, delimiter=delimiter, **kwargs)
        self.encoding = encoding

    def next(self):
        row = self.reader.next()
        row =  [unicode(s, self.encoding).replace('"', '') for s in row]
        return [" ".join(s.split()) for s in row]

    def __iter__(self):
        return self
