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
# File: tiertga.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------

import logging
from calculus.timegroupanalysis import TimeGroupAnalysis

from annotationdata.transcription import Transcription
from annotationdata.tier          import Tier
from annotationdata.annotation    import Annotation
from annotationdata.label.label   import Label
from annotationdata.ptime.interval import TimeInterval

# ----------------------------------------------------------------------------

class TierTGA( object ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Estimates TGA on a tier.

    Create time groups then map them into a dictionary where:
    - key is a label assigned to the time group
    - value is the list of observed durations of segments in this time group

    """
    TG_LABEL = "tg_"

    def __init__(self, tier=None, withradius=0):
        """
        Create a new TierTGA instance.

        @param tier (Tier)
        @param withradius (int): 0 means to use Midpoint, negative value means to use R-, positive radius means to use R+

        """
        self.tier         = tier
        self.__withradius = withradius
        self.__separators = []

    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_withradius(self):
        return self.__withradius

    # ------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------

    def set_withradius(self, withradius):
        """
        Set the withradius option, used to estimate the duration:
            - 0 means to use Midpoint,
            - negative value means to use R-,
            - positive radius means to use R+
        """
        self.__withradius = int(withradius)

    def remove_separators(self):
        """
        Remove all time group separators.
        """
        self.__separators = []

    def append_separator(self, sepstr):
        """
        Append a time group separator.
        """
        if not sepstr in self.__separators:
            self.__separators.append(sepstr)

    # ------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------

    def tga(self):
        """
        Create then return the TimeGroupAnalysis object corresponding to the tier.
        @return TimeGroupAnalysis
        """
        items = self.__tier_to_tg()
        return TimeGroupAnalysis( items )

    def labels(self):
        """
        Create then return the sequence of labels of each tg of the tier.
        @return dict: a dictionary with key=time group name and value=list of labels
        """
        lbls = self.__tier_to_labels()
        return lbls

    def deltadurations(self):
        """
        Create then return the sequence of deltadurations of each tg of the tier.
        @return dict: a dictionary with key=time group name and value=list of delta values
        """
        lbls = self.__tier_to_deltadurations()
        return lbls

    def tga_as_transcription(self):
        """
        Create then return the sequence of labels of each tg of the tier as a Transcription() object.
        @return Transcription()
        """
        trs = self.__tier_to_transcription()
        return trs

    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def __tier_to_tg(self):
        """
        Return a dict of tg_label/duration pairs.
        """
        i = 1
        tglabel = "tg_1"
        tg = {}

        for a in self.tier:
            alabel = a.GetLabel().GetValue()

            # a TG separator (create a new tg if previous tg was used!)
            if a.GetLabel().IsSilence() or a.GetLabel().IsDummy() or alabel in self.__separators:
                if tglabel in tg.keys():
                    i = i+1
                    tglabel = TierTGA.TG_LABEL+str(i)

            # a TG continuum
            else:
                # Get the duration
                duration = a.GetLocation().GetDuration().GetValue()
                if a.GetLocation().IsInterval():
                    if self.__withradius < 0:
                        duration = duration + a.GetLocation().GetDuration().GetMargin()
                    elif self.__withradius > 0:
                        duration = duration - a.GetLocation().GetDuration().GetMargin()
                # Append in the list of values of this TG
                if not tglabel in tg.keys():
                    tg[tglabel] = []
                tg[tglabel].append( duration )

        return tg

    def __tier_to_labels(self):
        """
        Return a dict of tg_label/labels pairs.
        """
        i = 1
        tglabel = "tg_1"
        labels = {}

        for a in self.tier:
            alabel = a.GetLabel().GetValue()

            # a TG separator (create a new tg if previous tg was used!)
            if a.GetLabel().IsSilence() or a.GetLabel().IsDummy() or alabel in self.__separators:
                if tglabel in labels.keys():
                    i = i+1
                    tglabel = TierTGA.TG_LABEL+str(i)

            # a TG continuum
            else:
                if not tglabel in labels.keys():
                    labels[tglabel] = []
                labels[tglabel].append( alabel )

        return labels

    def __tier_to_deltadurations(self):
        """
        Return a dict of tg_label/delta pairs.
        """
        i = 1
        tglabel = "tg_1"
        labels = {}
        previousduration = 0.

        for a in self.tier:
            alabel = a.GetLabel().GetValue()

            # a TG separator (create a new tg if previous tg was used!)
            if a.GetLabel().IsSilence() or a.GetLabel().IsDummy() or alabel in self.__separators:
                if tglabel in labels.keys():
                    i = i+1
                    tglabel = TierTGA.TG_LABEL+str(i)
                previousduration = 0.

            # a TG continuum
            else:
                # Get the duration
                duration = a.GetLocation().GetDuration()
                if a.GetLocation().IsInterval():
                    if self.__withradius < 0:
                        duration = duration + a.GetLocation().GetBegin().GetRadius() + a.GetLocation().GetEnd().GetRadius()
                    elif self.__withradius > 0:
                        duration = duration - a.GetLocation().GetBegin().GetRadius() - a.GetLocation().GetEnd().GetRadius()

                if not tglabel in labels.keys():
                    labels[tglabel] = []
                    logging.debug('... %s is first segment of this TG'%alabel)
                else:
                    logging.debug('... %s is segment prec=%f dur=%f'%(alabel,previousduration.GetValue(),duration.GetValue()))
                    # delta=duration(i)-duration(i+1)
                    #   positive => deceleration
                    #   negative => acceleration
                    labels[tglabel].append( previousduration.GetValue()-duration.GetValue() )

                previousduration = duration

        return labels

    def __tier_to_transcription(self):
        """
        Return a Transcription() of tiers with tg_labels.
        """
        i = 1
        tglabel = "tg_1"
        seglabels = ""
        tgann = None
        tgtier   = Tier('TGA-TimeGroups')
        segstier = Tier('TGA-Segments')

        for a in self.tier:
            alabel = a.GetLabel().GetValue()

            # a TG separator (create a new tg if previous tg was used!)
            if a.GetLabel().IsSilence() or a.GetLabel().IsDummy() or alabel in self.__separators:
                if len(seglabels)>0:
                    newa = Annotation(TimeInterval(tgann.GetLocation().GetEnd(),a.GetLocation().GetBegin()), Label(tglabel))
                    tgtier.Append( newa )
                    newa = Annotation(TimeInterval(tgann.GetLocation().GetEnd(),a.GetLocation().GetBegin()), Label( " ".join( seglabels )))
                    segstier.Append( newa )
                    i = i+1
                    tglabel = TierTGA.TG_LABEL+str(i)
                    seglabels = ""
                tgann = a
            # a TG continuum
            else:
                seglabels += alabel + " "

        ds = self.tga()
        occurrences = ds.len()
        total       = ds.total()
        mean        = ds.mean()
        median      = ds.median()
        stdev       = ds.stdev()
        npvi        = ds.nPVI()
        regressp    = ds.intercept_slope_original()
        regresst    = ds.intercept_slope()

        lentier    = Tier('TGA-occurrences')
        totaltier  = Tier('TGA-total')
        meantier   = Tier('TGA-mean')
        mediantier = Tier('TGA-median')
        stdevtier  = Tier('TGA-stdev')
        npvitier   = Tier('TGA-npvi')
        interceptptier = Tier('TGA-intercept-with-X-as-position')
        slopeptier     = Tier('TGA-slope-with-X-as-position')
        interceptttier = Tier('TGA-intercept-with-X-as-timestamp')
        slopettier     = Tier('TGA-slope-with-X-as-timestamp')

        for a in tgtier:
            alabel = a.GetLabel().GetValue()
            anew = a.Copy()
            anew.GetLabel().SetValue( str(occurrences[alabel]) )
            lentier.Append( anew )
            anew = a.Copy()
            anew.GetLabel().SetValue( str(total[alabel]) )
            totaltier.Append( anew )
            anew = a.Copy()
            anew.GetLabel().SetValue( str(mean[alabel]) )
            meantier.Append( anew )
            anew = a.Copy()
            anew.GetLabel().SetValue( str(median[alabel]) )
            mediantier.Append( anew )
            anew = a.Copy()
            anew.GetLabel().SetValue( str(stdev[alabel]) )
            stdevtier.Append( anew )
            anew = a.Copy()
            anew.GetLabel().SetValue( str(npvi[alabel]) )
            npvitier.Append( anew )
            anew = a.Copy()
            anew.GetLabel().SetValue( str(regressp[alabel][0]) )
            interceptptier.Append( anew )
            anew = a.Copy()
            anew.GetLabel().SetValue( str(regressp[alabel][1]) )
            slopeptier.Append( anew )
            anew = a.Copy()
            anew.GetLabel().SetValue( str(regresst[alabel][0]) )
            interceptttier.Append( anew )
            anew = a.Copy()
            anew.GetLabel().SetValue( str(regresst[alabel][1]) )
            slopettier.Append( anew )

        trs = Transcription("TGA")
        trs.Append( tgtier )
        trs.Append( segstier )
        trs.Append( lentier )
        trs.Append( totaltier )
        trs.Append( meantier )
        trs.Append( mediantier )
        trs.Append( stdevtier )
        trs.Append( npvitier )
        trs.Append( interceptptier )
        trs.Append( slopeptier )
        trs.Append( interceptttier )
        trs.Append( slopettier )

        return trs

# ---------------------------------------------------------------------------
