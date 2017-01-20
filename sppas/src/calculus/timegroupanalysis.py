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

    src.calculus.timegroupanalysis.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TGA: Time Group Analyzer is an online tool for speech annotation mining
    written by Dafydd Gibbon (Universität Bielefeld).

    See: <http://wwwhomes.uni-bielefeld.de/gibbon/TGA/>

"""

from descriptivesstats import DescriptiveStatistics
import stats.linregress
import stats.variability

# ----------------------------------------------------------------------------


class TimeGroupAnalysis(DescriptiveStatistics):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    :summary:      TGA estimator class.

    This class estimates TGA on a set of data values, stored in a dictionary:

        - key is the name of the time group;
        - value is the list of durations of each segments in the time group.

    >>> d = { 'tg1':[1.0, 1.2, 3.2, 4.1] , 'tg2':[2.9, 3.3, 3.6, 5.8] }
    >>> tga = TimeGroupAnalysis(d)
    >>> total = tga.total()
    >>> slope = tga.slope()
    >>> print slope['tg_1']
    >>> print slope['tg_2']
    >>>

    """
    def __init__(self, dict_items):
        """ TGA - The Time Group Analyzer

        :param dict_items: (dict) a dict of a list of durations.

        """
        DescriptiveStatistics.__init__(self, dict_items)

    # -----------------------------------------------------------------------
    # Specific estimators for rythm analysis
    # -----------------------------------------------------------------------

    def rPVI(self):
        """ Estimates the Raw Pairwise Variability Index of data values.

        :returns: (dict) a dictionary of (key, nPVI) of float values

        """
        return dict((key, stats.variability.rPVI(values)) for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def nPVI(self):
        """ Estimates the Normalized Pairwise Variability Index of data values.

        :returns: (dict) a dictionary of (key, nPVI) of float values

        """
        return dict((key, stats.variability.nPVI(values)) for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def intercept_slope_original(self):
        """ Estimates the intercept like the original TGA of data values.

        :returns: (dict) a dictionary of (key, (intercept,slope)) of float values

        """
        # Create the list of points (x,y) of each TG where:
        #  x is the position
        #  y is the duration
        linreg = []
        for key, values in self._items.items():
            points = [(position, duration) for position, duration in enumerate(values)]
            linreg.append((key, (stats.linregress.tga_linear_regression(points))))

        return dict(linreg)

    # -----------------------------------------------------------------------

    def intercept_slope(self):
        """ Estimates the intercept like AnnotationPro of data values.

        :returns: (dict) a dictionary of (key, (intercept,slope)) of float values

        """
        # Create the list of points (x,y) of each TG where:
        # x is the timestamps
        # y is the duration
        linreg = []
        for key, values in self._items.items():
            points = []
            timestamp = 0.
            for duration in values:
                points.append((timestamp, duration))
                timestamp += duration
            linreg.append((key, (stats.linregress.tga_linear_regression(points))))

        return dict(linreg)
