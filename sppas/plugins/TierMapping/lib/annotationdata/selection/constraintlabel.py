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

import re
from searchmodes import SearchModes
from annotationdata.label.textentry import TextEntry


class ConstraintLabel(object):
    """
    Performs match operations on an instance of Annotation.
    """

    def __init__(self, patterns, modes, options=[]):
        """ Create a new ConstraintLabel instance.
            Parameters:
                - patterns (list of strings) The patterns to find.
                - modes (list of SearchMode) Fix the modes search, in:
                    - MD_EXACT:      the labels must strictly correspond,
                    - MD_CONTAINS:   the label of the tier contains the given label,
                    - MD_STARTSWITH: the label of the tier starts with the given label,
                    - MD_ENDSWITH:   the label of the tier ends with the given label
                    - MD_REGEXP      Regular expression
                - options (list of options) Research parameter is case sensitive
        """
        self.patterns = patterns
        self.modes = modes
        self.options = options

    # End __init__
    # -----------------------------------------------------------------------

    #  __call__ allows instances to behave as if they were functions.
    #  >>> matcher = LabelMatcher("foo", modes=[0, 1], options=[])
    #  >>> matcher(annotation)
    #  >>> True

    def __call__(self, annotation):
        """ Performs match operations.
            Parameters:
                 - annotation (Annotation)
            Exception:   none
            Return:      Boolean
        """
        if not self.patterns:
            return True
        match = False
        label = annotation.TextValue
        for pattern in self.patterns:

            pattern = TextEntry( pattern ).Value

            if not "CASE_SENSITIVE" in self.options:
                pattern = pattern.lower()
                label = label.lower()

            if SearchModes.MD_REGEXP in self.modes:
                try:
                    if re.match(pattern, label):
                        match = True
                except:
                    raise Exception("Invalid regular expression.")

            if SearchModes.MD_EXACT in self.modes:
                if label == pattern:
                    match = True

            if SearchModes.MD_CONTAINS in self.modes:
                if pattern in label:
                    match = True

            if SearchModes.MD_STARTSWITH in self.modes:
                if label.startswith(pattern):
                    match = True

            if SearchModes.MD_ENDSWITH in self.modes:
                if label.endswith(pattern):
                    match = True
        return match

    # End __call__
    # -----------------------------------------------------------------------
