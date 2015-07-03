#!/usr/bin/env python2
# encoding: utf-8

from utils.deprecated import deprecated


class MetaObject(object):

    def __init__(self):
        self.metadata = {}

    # End __init__
    # ------------------------------------------------------------------------------------

    @deprecated
    def GetMetadata(self, key):
        if(key not in self.metadata):
            return ''
        else:
            return self.metadata[key]

    # End GetMetadata
    # ------------------------------------------------------------------------------------

    @deprecated
    def SetMetadata(self, key, value):
        self.metadata[key] = value

    # End SetMetadata
    # ------------------------------------------------------------------------------------

    # End MetaObject
    # ------------------------------------------------------------------------------------
