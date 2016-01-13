#!/usr/bin/env python2
# -*- coding: utf-8 -*-
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

from annotationdata.utils.tierutils import TierUtils
from annotationdata.transcription import Transcription
from annotationdata.tier import Tier
import annotationdata.io


def overlaps(a1, a2):
    """
    Return True if a1 overlaps with a2.
    Parameters:
        - a1 (Annotation)
        - a2 (Annotation)
    Exception: none
    Return: bool
    """
    if a1.IsInterval():
        s1 = a1.Begin
        e1 = a1.End
    else:
        s1 = a1.Time
        e1 = a1.Time
    if a2.IsInterval():
        s2 = a2.Begin
        e2 = a2.End
    else:
        s2 = a2.Time
        e2 = a2.Time
    return s2 < e1 and s1 < e2


class TrsUtils(object):

    """
    Provides utility methods for Transcription instances.
    """

    @staticmethod
    def Split(transcription, ref_tier):
        """
        Split a transcription into multiple small transcription.
        Parameters:
            - transcription (Transcription)
            - ref_tier (Tier)
        Exception: none
        Return: list of transcription
        """
        result = []
        for a1 in ref_tier:
            if a1.Text.IsEmpty():
                continue
            new_trs = Transcription()
            for tier in transcription:
                new_tier = TierUtils.Select(tier, lambda x: overlaps(a1, x))
                if new_tier is not None:
                    if new_tier[0].IsInterval():
                        new_tier[0].BeginValue = a1.BeginValue
                        new_tier[-1].EndValue = a1.EndValue
                    new_trs.Append(new_tier)

            if not new_trs.IsEmpty():
                result.append(new_trs)
        return result


    @staticmethod
    def Shift(transcription, n):
        """
        Shift all time points by n in the transcription.
        Parameters:
            - transcription (Transcription)
            - n (float)
        Exception: none
        Return: None
        """
        if n == 0:
            return

        for tier in transcription:
            if tier.IsInterval():
                for a in tier:
                    begin = a.BeginValue - n
                    begin = begin if begin > 0 else 0
                    end = a.EndValue - n
                    if end <= 0:
                        tier.Remove(a.BeginValue, a.EndValue)
                    else:
                        a.BeginValue = begin
                        a.EndValue =  end
            else: # PointTier
                for a in tier:
                    time = a.Time.Value - n
                    if time > 0:
                        a.Time.Value = time
                    else:
                        # Remove
                        pass
