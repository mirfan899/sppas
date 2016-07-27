#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
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
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: tips.py
# ----------------------------------------------------------------------------

import codecs
import random
from sp_glob import TIPS_FILE

# ----------------------------------------------------------------------------

class Tips( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Manage SPPAS tips.

    """
    def __init__(self):
        """
        Constructor.

        """
        self.current = 0
        try:
            with codecs.open(TIPS_FILE, 'r', 'utf-8') as f:
                self.tips = f.readlines()
        except Exception:
            self.tips = ["Thanks for using SPPAS."]

    # ------------------------------------------------------------------------

    def get(self):
        """
        Return a random message.

        """
        if len(self.tips) == 1:
            self.current = 0
            return self.tips[0]

        pround = 0
        new = self.current
        while new == self.current and pround<3:
            new = random.randint( 0, len(self.tips)-1 )
            pround = pround + 1

        self.current = new
        return self.tips[self.current]

    # ------------------------------------------------------------------------
