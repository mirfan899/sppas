#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import csv


class CSVReader(object):
    """
    UTF8 CSVReader.
    """
    def __init__(self, f, dialect=csv.excel, **kwargs):
        self.reader = csv.reader(f, dialect=dialect, **kwargs)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8").replace('"', '') for s in row]

    def __iter__(self):
        return self
