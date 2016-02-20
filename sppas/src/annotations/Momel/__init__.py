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

"""
    This package includes the SPPAS implementation of Momel and INTSINT.

    Different versions of the Momel and Intsint algorithms have been developed
    in the LPL in Aix en Provence over the last twenty years and have been
    used for the phonetic modelling and symbolic coding of the intonation
    patterns of a number of languages (including English, French, Italian,
    Catalan, etc).
    The last implementation is presented as a Praat plugin. The modelling
    and coding algorithms have been implemented as a set of Praat scripts,
    each corresponding to a specific step in the process.

    The quality of the F0 modelling crucially depends on the quality of
    the F0 detected.

    Momel:
    The quadratic spline function used to model the macro-melodic component
    is defined by a sequence of target points, (couples <s, Hz>) each pair
    of which is linked by two monotonic parabolic curves with the spline
    knot occurring (by default) at the midway point between the two targets.
    The first derivative of the curve thus defined is zero at each target
    point and the two parabolas have the same value and same derivative at
    the spline knot. This, in fact, defines the most simple mathematical
    function for which the curves are both continuous and smooth.

    INTSINT:
    SPPAS implements the first version of INTSINT. In this version of the
    INTSINT algorithm, the estimation is based on a statistical analysis
    of the distribution of target points based on their local configuration.
    This requires the optimisation of 10 different parameters followed
    by a recoding of the targets when this improved the fit.

"""
__all__ = ['momel', 'intsint']
