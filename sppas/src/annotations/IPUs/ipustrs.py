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

    src.annotations.ipustrs.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------


class IPUsTrs(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      An IPUs segmentation from an already annotated data file.

    """
    def __init__(self, trs):
        """Creates a new IPUsTrs instance.

        :param trs: (Transcription) Input transcription from which it's
        possible to extract IPUs.
        Expected tiers are:
            - first tier: the IPUs content [required]
            - second tier: the IPUs file names [optional]

        """
        super(IPUsTrs, self).__init__()
        
        self._trsinput = Transcription()
        self._units = list()  # List of the content of the units (if any)
        self._names = list()  # List of file names for IPUs (if any)
        self.set_transcription(trs)

    # ------------------------------------------------------------------

    def get_units(self):
        """Return the list of the IPUs contents."""
        
        return self._units

    # ------------------------------------------------------------------

    def get_names(self):
        """Return the list of file names for IPUs."""

        return self._names

    # ------------------------------------------------------------------
    # Manage Transcription
    # ------------------------------------------------------------------

    def set_transcription(self, trs):
        """Set a new Transcription.

        :param trs: (Transcription) Input transcription from which it's
        possible to extract IPUs.

        """
        if trs is not None:
            self._trsinput = trs
        else:
            self._trsinput = Transcription()

    # ------------------------------------------------------------------
    # Units search
    # ------------------------------------------------------------------

    def extract_bounds(self):
        """Return bound values.

        Bound values are boolean to know if we expect a silence at start
        or end of the given transcription. It is relevant only if the
        transcription was created from a non-aligned file.

        """
        # False means that I DON'T know if there is a silence:
        # It does not mean that there IS NOT a silence.
        # However, True means that there is a silence, for sure!
        bound_start = False
        bound_end = False

        if len(self._trsinput) > 0:

            # Check tier
            tier = self._trsinput[0]
            if tier.GetSize() == 0:
                raise IOError('Got no utterances.')

            # Fix bounds
            if tier[0].GetLabel().IsSilence() is True:
                bound_start = True
            if tier[-1].GetLabel().IsSilence() is True and tier.GetSize() > 1:
                bound_end = True

        return bound_start, bound_end

    # ------------------------------------------------------------------

    def extract(self):
        """Extract units and (if any) extract tracks and silences.

        :returns: tracks and silences, with time as seconds.

        """
        self._units = list()
        self._names = list()

        if self._trsinput.GetSize() == 0:
            return [], []

        trstier = self._trsinput[0]
        nametier = None
        if self._trsinput.GetSize() == 2:
            nametier = self._trsinput[1]

        tracks = []
        silences = []
        if trstier.GetSize() == 0:
            raise IOError('Got no utterances.')

        if trstier[0].GetLocation().GetValue().IsTimeInterval():
            (tracks, silences) = self.extract_aligned(trstier, nametier)
        else:
            self.extract_units()

        return tracks, silences

    # ------------------------------------------------------------------

    def extract_units(self):
        """Extract IPUs content from a non-aligned transcription file.

        """
        self._units = []
        self._names = []

        tier = self._trsinput[0]
        if tier.GetSize() == 0:
            raise IOError('Got no utterances.')

        i = 0
        for ann in tier:
            if ann.GetLabel().IsSilence() is False:
                self._units.append(ann.GetLabel().GetValue())
                self._names.append("track_%.06d" % (i+1))
                i += 1

    # ------------------------------------------------------------------

    def extract_aligned(self, trstier, nametier):
        """Extract from a time-aligned transcription file.

        :returns: a tuple with tracks and silences lists

        """
        trstracks = []
        silences = []
        self._units = list()
        self._names = list()

        i = 0
        last = trstier.GetSize()
        while i < last:
            # Set the current annotation values
            ann = trstier[i]

            # Save information
            if ann.GetLabel().IsSilence():
                start = ann.GetLocation().GetBegin().GetMidpoint()
                end = ann.GetLocation().GetEnd().GetMidpoint()
                # Verify next annotations (concatenate all silences between 2 tracks)
                if (i + 1) < last:
                    nextann = trstier[i + 1]
                    while (i + 1) < last and nextann.GetLabel().IsSilence():
                        end = nextann.GetLocation().GetEnd().GetMidpoint()
                        i += 1
                        if (i + 1) < last:
                            nextann = trstier[i + 1]
                silences.append([start, end])
            else:
                start = ann.GetLocation().GetBegin().GetMidpoint()
                end = ann.GetLocation().GetEnd().GetMidpoint()
                trstracks.append([start, end])
                self._units.append(ann.GetLabel().GetValue())

                if nametier is not None:
                    aname = nametier.Find(ann.GetLocation().GetBegin().GetMidpoint(),
                                          ann.GetLocation().GetEnd().GetMidpoint(), True)
                    if len(aname) == 0:
                        trstracks.pop()
                        self._units.pop()
                    else:
                        sf = sppasFileUtils(aname[0].GetLabel().GetValue())
                        # We have to take care in case of duplicated names
                        filename = sf.clear_whitespace()
                        if len(filename) == 0:
                            filename = "unnamed_track"
                        new_name = filename
                        idx = 2
                        while new_name in self._names:
                            new_name = u"%s_%.06d" % (filename, idx)
                            idx += 1
                        self._names.append(new_name)

            # Continue
            i += 1

        return trstracks, silences
