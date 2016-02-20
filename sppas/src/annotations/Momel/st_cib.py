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
# File: st_cib.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------


class Targets:
    """ A class to store one selected target.
        A target is made of 2 or 3 values:
            - x: float ; required
            - y: float ; required
            - p: int   ; optionnal
        Use getters and setters to manipulate x, y and p
    """
    def __init__(self):
        """ Create a new Targets instance with default values.
        """
        self.__x = 0.
        self.__y = 0.
        self.__p = 0

    # End init
    # ------------------------------------------------------------------


    def set(self,x,y,p=0):
        """ Set new values to a target.
            Parameters:
                - x is a float
                - y is a float
                - p is an integer
            Exception:   TypeError
        """
        self.set_x(x)
        self.set_y(y)
        if p:
            self.set_p(p)

    # End set
    # ------------------------------------------------------------------


    def set_x(self,x):
        """ Set a new x value to a target.
            Parameters:
                - x is a float value
            Exception:   TypeError
        """
        self.__x = float(x)

    # End set_x
    # ------------------------------------------------------------------


    def set_y(self,y):
        """ Set a new y value to a target.
            Parameters:
                - y is a float value
            Exception:   TypeError
        """
        self.__y = float(y)

    # End set_y
    # ------------------------------------------------------------------


    def set_p(self,p):
        """ Set a new p value to a target.
            Parameters:
                - p is an int value
            Exception:   TypeError
        """
        self.__p = int(p)

    # End set_p
    # ------------------------------------------------------------------


    def get_x(self):
        """ Return the x value of a target.
            Parameters:  None
            Exception:   None
            Return:      a float
        """
        return self.__x

    # End get_x
    # ------------------------------------------------------------------


    def get_y(self):
        """ Return the y value of a target.
            Parameters:  None
            Exception:   None
            Return:      a float
        """
        return self.__y

    # End get_y
    # ------------------------------------------------------------------


    def get_p(self):
        """ Return the p value of a target.
            Parameters:  None
            Exception:   None
            Return:      a float
        """
        return self.__p

    # End get_p
    # ------------------------------------------------------------------


    def print_cib(self,output,pasx=1,pasy=1):
        toprint = str(self.__x * pasx)+" "+str(self.__y * pasy)
        output.write(toprint+"\n")

    # End print
    # ------------------------------------------------------------------

