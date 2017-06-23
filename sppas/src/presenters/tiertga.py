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

    src.presenters.tiertga.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sppas.src.calculus.timegroupanalysis import TimeGroupAnalysis

from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.ptime.interval import TimeInterval

# ----------------------------------------------------------------------------


class TierTGA(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Estimates TGA on a tier.

    Create time groups then map them into a dictionary where:

        - key is a label assigned to the time group;
        - value is the list of observed durations of segments in this time group.

    """
    TG_LABEL = "tg_"

    def __init__(self, tier=None, with_radius=0):
        """ Create a new TierTGA instance.

        :param tier: (Tier)
        :param with_radius: (int) 0 to use Midpoint, negative value to use R-, positive value to use R+

        """
        self.tier = tier
        self._with_radius = with_radius
        self.__separators = list()

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_with_radius(self):
        """ Returns how to use the radius in duration estimations.
        0 means to use Midpoint, negative value means to use R-, and
        positive value means to use R+.

        """
        return self._with_radius

    # ------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------

    def set_with_radius(self, with_radius):
        """ Set the with_radius option, used to estimate the duration.

        :param with_radius: (int)
            - 0 means to use Midpoint;
            - negative value means to use R-;
            - positive radius means to use R+.

        """
        self._with_radius = int(with_radius)

    # ------------------------------------------------------------------

    def remove_separators(self):
        """ Remove all time group separators. """

        self.__separators = list()

    # ------------------------------------------------------------------

    def append_separator(self, symbol):
        """ Append a time group separator.

        :param symbol: (str) A symbol separator.
        """
        if symbol not in self.__separators:
            self.__separators.append(symbol)

    # ------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------

    def tga(self):
        """ Create a TimeGroupAnalysis object corresponding to the tier.

        :returns: (TimeGroupAnalysis)

        """
        i = 1
        tg_label = "tg_1"
        tg = dict()

        for ann in self.tier:
            ann_label = ann.GetLabel().GetValue()

            # a TG separator (create a new tg if previous tg was used!)
            if ann.GetLabel().IsSilence() or ann.GetLabel().IsDummy() or ann_label in self.__separators:
                if tg_label in tg.keys():
                    i += 1
                    tg_label = TierTGA.TG_LABEL + str(i)

            # a TG continuum
            else:
                # Get the duration
                duration = ann.GetLocation().GetDuration().GetValue()
                if ann.GetLocation().IsInterval():
                    if self._with_radius < 0:
                        duration = duration + ann.GetLocation().GetDuration().GetMargin()
                    elif self._with_radius > 0:
                        duration = duration - ann.GetLocation().GetDuration().GetMargin()
                # Append in the list of values of this TG
                if tg_label not in tg.keys():
                    tg[tg_label] = []
                tg[tg_label].append(duration)

        return TimeGroupAnalysis(tg)

    # ------------------------------------------------------------------

    def labels(self):
        """ Create the sequence of labels of each tg of the tier.

        :returns: a dictionary with key=time group name and value=list of labels

        """
        i = 1
        tg_label = "tg_1"
        labels = {}

        for ann in self.tier:
            ann_label = ann.GetLabel().GetValue()

            # a TG separator (create a new tg if previous tg was used!)
            if ann.GetLabel().IsSilence() or ann.GetLabel().IsDummy() or ann_label in self.__separators:
                if tg_label in labels.keys():
                    i += 1
                    tg_label = TierTGA.TG_LABEL + str(i)

            # a TG continuum
            else:
                if tg_label not in labels.keys():
                    labels[tg_label] = list()
                labels[tg_label].append(ann_label)

        return labels

    # ------------------------------------------------------------------

    def delta_durations(self):
        """ Create the sequence of delta durations of each tg of the tier.

        :returns:  dictionary with key=time group name and value=list of delta values

        """
        i = 1
        tg_label = "tg_1"
        labels = dict()
        previous_duration = 0.

        for ann in self.tier:
            ann_label = ann.GetLabel().GetValue()

            # a TG separator (create a new tg if previous tg was used!)
            if ann.GetLabel().IsSilence() or ann.GetLabel().IsDummy() or ann_label in self.__separators:
                if tg_label in labels.keys():
                    i += 1
                    tg_label = TierTGA.TG_LABEL + str(i)
                previous_duration = 0.

            # a TG continuum
            else:
                # Get the duration
                duration = ann.GetLocation().GetDuration()
                if ann.GetLocation().IsInterval():
                    if self._with_radius < 0:
                        duration = duration + \
                                   ann.GetLocation().GetBegin().GetRadius() + \
                                   ann.GetLocation().GetEnd().GetRadius()
                    elif self._with_radius > 0:
                        duration = duration - \
                                   ann.GetLocation().GetBegin().GetRadius() - \
                                   ann.GetLocation().GetEnd().GetRadius()

                if tg_label not in labels.keys():
                    labels[tg_label] = list()
                else:
                    # delta=duration(i)-duration(i+1)
                    #   positive => deceleration
                    #   negative => acceleration
                    labels[tg_label].append(previous_duration.GetValue()-duration.GetValue())

                previous_duration = duration

        return labels

    # ------------------------------------------------------------------

    def tga_as_transcription(self):
        """ Create the sequence of labels of each tg of the tier as a Transcription() object.

        :returns: (Transcription)

        """
        i = 1
        tg_label = "tg_1"
        seg_labels = ""
        tg_ann = None
        tg_tier = Tier('TGA-TimeGroups')
        segs_tier = Tier('TGA-Segments')

        for ann in self.tier:
            ann_label = ann.GetLabel().GetValue()

            # a TG separator (create a new tg if previous tg was used!)
            if ann.GetLabel().IsSilence() or ann.GetLabel().IsDummy() or ann_label in self.__separators:
                if len(seg_labels) > 0:
                    if tg_ann is not None:
                        new_a = Annotation(TimeInterval(tg_ann.GetLocation().GetEnd(), ann.GetLocation().GetBegin()), 
                                           Label(tg_label))
                        tg_tier.Append(new_a)
                        new_a = Annotation(TimeInterval(tg_ann.GetLocation().GetEnd(), ann.GetLocation().GetBegin()), 
                                           Label(" ".join(seg_labels)))
                        segs_tier.Append(new_a)
                        i += 1
                        tg_label = TierTGA.TG_LABEL+str(i)
                    seg_labels = ""
                tg_ann = ann
            # a TG continuum
            else:
                seg_labels += ann_label + " "

        ds = self.tga()
        occurrences = ds.len()
        total = ds.total()
        mean = ds.mean()
        median = ds.median()
        stdev = ds.stdev()
        npvi = ds.nPVI()
        regressp = ds.intercept_slope_original()
        regresst = ds.intercept_slope()

        len_tier = Tier('TGA-occurrences')
        total_tier = Tier('TGA-total')
        mean_tier = Tier('TGA-mean')
        median_tier = Tier('TGA-median')
        stdev_tier = Tier('TGA-stdev')
        npvi_tier = Tier('TGA-npvi')
        interceptp_tier = Tier('TGA-intercept-with-X-as-position')
        slopep_tier = Tier('TGA-slope-with-X-as-position')
        interceptt_tier = Tier('TGA-intercept-with-X-as-timestamp')
        slopet_tier = Tier('TGA-slope-with-X-as-timestamp')

        for a in tg_tier:
            ann_label = a.GetLabel().GetValue()
            ann_new = a.Copy()
            ann_new.GetLabel().SetValue(str(occurrences[ann_label]))
            len_tier.Append(ann_new)
            ann_new = a.Copy()
            ann_new.GetLabel().SetValue(str(total[ann_label]))
            total_tier.Append(ann_new)
            ann_new = a.Copy()
            ann_new.GetLabel().SetValue(str(mean[ann_label]))
            mean_tier.Append(ann_new)
            ann_new = a.Copy()
            ann_new.GetLabel().SetValue(str(median[ann_label]))
            median_tier.Append(ann_new)
            ann_new = a.Copy()
            ann_new.GetLabel().SetValue(str(stdev[ann_label]))
            stdev_tier.Append(ann_new)
            ann_new = a.Copy()
            ann_new.GetLabel().SetValue(str(npvi[ann_label]))
            npvi_tier.Append(ann_new)
            ann_new = a.Copy()
            ann_new.GetLabel().SetValue(str(regressp[ann_label][0]))
            interceptp_tier.Append(ann_new)
            ann_new = a.Copy()
            ann_new.GetLabel().SetValue(str(regressp[ann_label][1]))
            slopep_tier.Append(ann_new)
            ann_new = a.Copy()
            ann_new.GetLabel().SetValue(str(regresst[ann_label][0]))
            interceptt_tier.Append(ann_new)
            ann_new = a.Copy()
            ann_new.GetLabel().SetValue(str(regresst[ann_label][1]))
            slopet_tier.Append(ann_new)

        trs = Transcription("TGA")
        trs.Append(tg_tier)
        trs.Append(segs_tier)
        trs.Append(len_tier)
        trs.Append(total_tier)
        trs.Append(mean_tier)
        trs.Append(median_tier)
        trs.Append(stdev_tier)
        trs.Append(npvi_tier)
        trs.Append(interceptp_tier)
        trs.Append(slopep_tier)
        trs.Append(interceptt_tier)
        trs.Append(slopet_tier)

        return trs
