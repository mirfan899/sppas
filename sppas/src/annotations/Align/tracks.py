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
# File: tracks.py
# ---------------------------------------------------------------------------

import os
import codecs

from sp_glob import encoding

from annotations.Align.aligners.alignerio import AlignerIO

import annotationdata.io
from annotationdata.transcription  import Transcription
from annotationdata.tier           import Tier
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point    import TimePoint
from annotationdata.annotation     import Annotation
from annotationdata.label.label    import Label
from annotationdata.label.text     import Text

import audiodata.autils as autils

# ---------------------------------------------------------------------------

class TrackNamesGenerator():
    def __init__(self):
        pass

    def audiofilename(self, trackdir, tracknumber):
        return os.path.join(trackdir, "track_%.06d.wav" % tracknumber)

    def phonesfilename(self, trackdir, tracknumber):
        return os.path.join(trackdir, "track_%.06d.pron" % tracknumber)

    def tokensfilename(self, trackdir, tracknumber):
        return os.path.join(trackdir, "track_%.06d.term" % tracknumber)

    def alignfilename(self, trackdir, tracknumber, ext=None):
        if ext is None:
            return os.path.join(trackdir, "track_%.06d" % tracknumber)
        return os.path.join(trackdir, "track_%.06d.%s" % (tracknumber,ext))

# ----------------------------------------------------------------------------

class TrackSplitter( Transcription ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Write tokenized-phonetized segments from Tiers.

    """
    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new TrackSplitter instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)
        self._radius = 0.005
        self._tracknames = TrackNamesGenerator()
        self._aligntrack = None

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def set_tracksnames( self, tracknames ):
        """
        Set the TrackNamesGenerator().

        """
        self._tracknames = tracknames

    # ------------------------------------------------------------------------

    def set_trackalign( self, ta ):
        """
        Set the aligner, required to create tracks (if any).

        """
        self._aligntrack = ta

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    def split(self, inputaudio, phontier, toktier, diralign):
        """
        Main method to write tracks from the given data.

        @param inputaudio (src - IN) File name of the audio file.
        @param phontier  (Tier - IN) Tier with phonetization to split.
        @param toktier   (Tier - IN) Tier with tokenization to split.
        @param diralign   (str - IN) Directory to put units.

        @return List of tracks with (start-time end-time)

        """
        if phontier.IsTimeInterval() is False:
            raise TypeError('Only a tier with time-aligned phonetization (in ipus, chunks, tracks,...) can be aligned at phones level.')
        if toktier.IsTimeInterval() is False:
            toktier = None

        tracks = self.write_text_tracks(phontier, toktier, diralign)
        self.write_audio_tracks(inputaudio, tracks, diralign)

        return tracks

    # ------------------------------------------------------------------------

    def write_text_tracks(self, phontier, toktier, diralign):
        """
        Write tokenization and phonetization of tiers into separated track files.

        @param phontier (Tier - IN) time-aligned tier with phonetization to split
        @param toktier  (Tier - IN) time-aligned tier with tokenization to split
        @param diralign (str - IN) the directory to write tracks.

        """
        tokens = True
        if toktier is None:
            toktier = phontier.Copy()
            tokens = False
        if phontier.GetSize() != toktier.GetSize():
            raise IOError('Inconsistency between the number of intervals of tokenization (%d) and phonetization (%d) tiers.'%(phontier.GetSize(),toktier.GetSize()))

        units = []
        for annp,annt in zip(phontier,toktier):

            b = annp.GetLocation().GetBegin().GetMidpoint()
            e = annp.GetLocation().GetEnd().GetMidpoint()
            units.append( (b,e) )

            # Here we write only the text-label with the best score,
            # we don't care about alternative text-labels
            fnp = self._tracknames.phonesfilename(diralign, len(units))
            textp = annp.GetLabel().GetValue()
            self._write_text_track( fnp, textp )

            fnt = self._tracknames.tokensfilename(diralign, len(units))
            label = annt.GetLabel()
            if tokens is False and label.IsSpeech() is True:
                textt = " ".join( ["w_"+str(i+1) for i in range(len(textp.split()))] )
            else:
                textt = label.GetValue()
            self._write_text_track( fnt, textt )

        return units

    # ------------------------------------------------------------------------

    def write_audio_tracks(self, inputaudio, units, diralign, silence=0.):
        """
        Write the first channel of an audio file into separated track files.
        Re-sample to 16000 Hz, 16 bits.

        @param inputaudio (src - IN) File name of the audio file.
        @param units     (list - IN) List of tuples (start-time,end-time) of tracks.
        @param diralign   (str - IN) Directory to write audio tracks.
        @param silence   float - IN) Duration of a silence to surround the tracks.

        """
        channel = autils.extract_audio_channel( inputaudio,0 )
        channel = autils.format_channel( channel,16000,2 )

        for track,u in enumerate(units):
            (s,e) = u
            trackchannel = autils.extract_channel_fragment( channel, s, e, silence)
            trackname    = self._tracknames.audiofilename(diralign, track+1)
            autils.write_channel(trackname, trackchannel)


    # ------------------------------------------------------------------------

    def _write_text_track(self, trackname, trackcontent):
        """
        Write a raw text in a file.

        """
        with codecs.open(trackname,"w", encoding) as fp:
            fp.write(trackcontent)

# ----------------------------------------------------------------------------

class TracksReader( Transcription ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Read time-aligned segments, convert into Tier.

    """
    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new SegmentsIn instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)
        self.alignerio = AlignerIO()
        self._radius = 0.005
        self._tracknames = TrackNamesGenerator()

    # ------------------------------------------------------------------------

    def set_tracksnames( self, tracknames ):
        self._tracknames = tracknames

    # ------------------------------------------------------------------------

    def read(self, dirname, units):
        """
        Read a set of alignment files and set as tiers.

        @param dirname (str - IN) the input directory containing a set of unit
        @param units (list - IN) List of units with start/end times

        """
        # Verify if the directory exists
        if os.path.exists( dirname ) is False:
            raise IOError("Missing directory: " + dirname+".\n")

        # Create new tiers
        itemp = self.NewTier("PhonAlign")
        itemw = self.NewTier("TokensAlign")

        # Explore each unit to get alignments
        for track in range(len(units)):

            # Get real start and end time values of this unit.
            unitstart,unitend = units[track]

            basename = self._tracknames.alignfilename(dirname, track+1)
            (_phonannots,_wordannots) = self.alignerio.read_aligned(basename)

            # Append alignments in tiers
            self._append_tuples(itemp, _phonannots, unitstart, unitend)
            self._append_tuples(itemw, _wordannots, unitstart, unitend)

        # Adjust Radius
        if itemp.GetSize()>1:
            itemp[-1].GetLocation().SetEndRadius(0.)
        if itemw.GetSize()>1:
            itemw[-1].GetLocation().SetEndRadius(0.)
            try:
                self._hierarchy.addLink('TimeAlignment', itemp, itemw)
            except Exception:
                pass

    # ------------------------------------------------------------------------

    def _append_tuples(self, tier, tdata, delta, unitend):
        """
        Append a list of (start,end,text,score) into the tier.
        Shift start/end of a delta value and set the last end value.

        """
        try:

            for i,t in enumerate(tdata):
                (loc_s,loc_e,lab,scr) = t
                loc_s += delta
                loc_e += delta
                if i==(len(tdata)-1):
                    loc_e = unitend

                # prepare the code in case we'll find a solution with
                # alternatives phonetizations/tokenization....
                #lab = [lab]
                #scr = [scr]
                #label = Label()
                #for l,s in zip(lab,scr):
                #    label.AddValue(Text(l,s))
                label = Label( Text(lab,scr) )
                annotationw = Annotation(TimeInterval(TimePoint(loc_s,self._radius), TimePoint(loc_e,self._radius)), label)
                tier.Append(annotationw)

        except Exception:
            pass

    # ------------------------------------------------------------------------
