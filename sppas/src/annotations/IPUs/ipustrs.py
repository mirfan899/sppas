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
# File: ipustrs.py
# ---------------------------------------------------------------------------

import annotationdata.aio
from annotationdata.transcription import Transcription

from utils.fileutils import format_filename

# ---------------------------------------------------------------------------

class IPUsTrs( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      An IPUs segmenter from an already annotated data file.

    IPUs - Inter-Pausal Units are blocks of speech bounded by silent pauses
    of more than X ms, and time-aligned on the speech signal.

    """
    def __init__(self, trs):
        """
        Creates a new IPUsTrs instance.

        @param trs (Transcription) Input transcription from which it's
        possible to extract IPUs.
        Expected tiers are:
            - first tier: the IPUs content
            - second tier: the IPUs file names

        """
        super(IPUsTrs, self).__init__()
        self.set_transcription(trs)
        self.reset()

    # ------------------------------------------------------------------

    def reset(self):
        """
        Set default values to members.

        """
        self.units = []  # List of the content of the units (if any)
        self.names = []  # List of file names for IPUs (if any)

    # ------------------------------------------------------------------

    def get_units(self):
        """
        Return the list of the content of the IPUs.

        """
        return self.units

    # ------------------------------------------------------------------

    def get_names(self):
        """
        Return the list of file names for IPUs.
        """
        return self.names

    # ------------------------------------------------------------------
    # Manage Transcription
    # ------------------------------------------------------------------

    def set_transcription(self, trs):
        """
        Set a new Transcription.

        @param trs (Transcription) Input transcription from which it's
        possible to extract IPUs.

        """
        if trs is not None:
            self.trsinput = trs
        else:
            self.trsinput = Transcription()

    # ------------------------------------------------------------------
    # Units search
    # ------------------------------------------------------------------

    def extract_bounds(self):
        """
        Return bound values.

        Bound values are boolean to know if we expect a silence at start
        or end of the given transcription. It is relevant only if the
        transcription was created from a non-aligned file.

        """
        # False means that I DON'T know if there is a silence:
        # It does not mean that there IS NOT a silence.
        # However, True means that there is a silence, for sure!
        bound_start = False
        bound_end   = False

        if len(self.trsinput) > 0:

            # Check tier
            tier = self.trsinput[0]
            if tier.GetSize() == 0:
                raise IOError('Got no utterances.')

            # Fix bounds
            if tier[0].GetLabel().IsSilence() is True:
                bound_start = True
            if tier[-1].GetLabel().IsSilence() is True and tier.GetSize()>1:
                bound_end = True

        return (bound_start,bound_end)

    # ------------------------------------------------------------------

    def extract(self):
        """
        Extract units and if any extract tracks and silences.

        @return tracks and silences, with time as seconds.

        """
        self.units = []
        self.names = []

        if self.trsinput.GetSize() == 0:
            return ([],[])

        trstier = self.trsinput[0]
        nametier = None
        if self.trsinput.GetSize() == 2:
            nametier = self.trsinput[1]

        tracks = []
        silences = []
        if trstier.GetSize() == 0:
            raise IOError('Got no utterances.')

        if trstier[0].GetLocation().GetValue().IsTimeInterval():
            (tracks,silences) = self.extract_aligned(trstier,nametier)
        else:
            self.extract_units()
        return (tracks,silences)

    # ------------------------------------------------------------------

    def extract_units(self):
        """
        Extract IPUs content from a non-aligned transcription file.

        """
        self.units = []
        self.names = []

        tier = self.trsinput[0]
        if tier.GetSize() == 0:
            raise IOError('Got no utterances.')

        i = 0
        for ann in tier:
            if ann.GetLabel().IsSilence() is False:
                self.units.append( ann.GetLabel().GetValue() )
                self.names.append( "track_%.06d" % (i+1) )
                i = i+1

    # ------------------------------------------------------------------

    def extract_aligned(self, trstier, nametier):
        """
        Extract from a time-aligned transcription file.

        @param inputfilename is the input transcription file name
        @return a tuple with tracks and silences lists

        """
        trstracks = []
        silences  = []
        self.units = []
        self.names = []

        i = 0
        last = trstier.GetSize()
        while i < last:
            # Set the current annotation values
            ann = trstier[i]

            # Save information
            if ann.GetLabel().IsSilence():
                start = ann.GetLocation().GetBegin().GetMidpoint()
                end   = ann.GetLocation().GetEnd().GetMidpoint()
                # Verify next annotations (concatenate all silences between 2 tracks)
                if (i + 1) < last:
                    nextann = trstier[i + 1]
                    while (i + 1) < last and nextann.GetLabel().IsSilence():
                        end = nextann.GetLocation().GetEnd().GetMidpoint()
                        i = i + 1
                        if (i + 1) < last:
                            nextann = trstier[i + 1]
                silences.append([start,end])
            else:
                start = ann.GetLocation().GetBegin().GetMidpoint()
                end   = ann.GetLocation().GetEnd().GetMidpoint()
                trstracks.append([start,end])
                self.units.append( ann.GetLabel().GetValue() )

                if nametier is not None:
                    aname = nametier.Find(ann.GetLocation().GetBegin().GetMidpoint(), ann.GetLocation().GetEnd().GetMidpoint(), True)
                    if len(aname) == 0:
                        trstracks.pop()
                        self.units.pop()
                    else:
                        self.names.append( format_filename(aname[0].GetLabel().GetValue()) )

            # Continue
            i = i + 1

        return (trstracks,silences)

    # ------------------------------------------------------------------
