# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.calculus.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    calculus is a free and open source Python library to perform some math
    on data. Basically, calculus package was created to estimates descriptive
    statistics on annotated data.

"""
from sppas.src.utils.maketext import translate
t = translate("calculus")

from .descriptivesstats import sppasDescriptiveStatistics
from .kappa import sppasKappa
from .timegroupanalysis import sppasTimeGroupAnalysis
from .geometry.distances import squared_euclidian, euclidian, manathan, minkowski, chi_squared
from .stats.central import fsum, fmult, fmin, fmax, fmean, fgeometricmean, fharmonicmean
from .stats.frequency import freq, percent, percentile, quantile
from .stats.linregress import tga_linear_regression, tansey_linear_regression
from .stats.linregress import gradient_descent, gradient_descent_linear_regression, compute_error_for_line_given_points
from .stats.moment import lmoment, lvariation, lskew, lkurtosis
from .stats.variability import lvariance, lstdev, lz, rPVI, nPVI
from .scoring.ubpa import ubpa

# ---------------------------------

__all__ = [
    "sppasDescriptiveStatistics",
    "sppasKappa",
    "sppasTimeGroupAnalysis",
    "squared_euclidian", "euclidian", "manathan", "minkowski", "chi_squared",
    "fsum", "fmult", "fmin", "fmax", "fmean", "fgeometricmean", "fharmonicmean",
    "freq", "percent", "percentile", "quantile",
    "tga_linear_regression", "tansey_linear_regression",
    "gradient_descent", "gradient_descent_linear_regression", "compute_error_for_line_given_points",
    "lmoment", "lvariation", "lskew", "lkurtosis",
    "lvariance", "lstdev", "lz", "rPVI", "nPVI",
    "ubpa"
]
