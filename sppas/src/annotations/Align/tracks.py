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

    src.annotations.Align.tracks.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import os
import codecs

from sppas.src.config import sg

from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.ptime.point import TimePoint
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.label.text import Text
import sppas.src.audiodata.autils as autils

from ..annotationsexc import BadInputError
from ..annotationsexc import SizeInputsError
from ..annotationsexc import NoDirectoryError
from .aligners.alignerio import AlignerIO

# ---------------------------------------------------------------------------


class TrackNamesGenerator(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Manage the filenames for the tracks.

    """
    def __init__(self):
        pass

    def audio_filename(self, trackdir, tracknumber):
        return os.path.join(trackdir, "track_%.06d.wav" % tracknumber)

    def phones_filename(self, trackdir, tracknumber):
        return os.path.join(trackdir, "track_%.06d.pron" % tracknumber)

    def tokens_filename(self, trackdir, tracknumber):
        return os.path.join(trackdir, "track_%.06d.term" % tracknumber)

    def align_filename(self, trackdir, tracknumber, ext=None):
        if ext is None:
            return os.path.join(trackdir, "track_%.06d" % tracknumber)
        return os.path.join(trackdir, "track_%.06d.%s" % (tracknumber, ext))

# ----------------------------------------------------------------------------


class TrackSplitter(Transcription):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Write tokenized-phonetized segments from Tiers.

    """
    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """Creates a new TrackSplitter instance.

        :param name: (str)

        """
        super(TrackSplitter, self).__init__(name, mintime, maxtime)
        self._radius = 0.005
        self._tracknames = TrackNamesGenerator()
        self._aligntrack = None

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def set_tracksnames(self, track_names):
        """Set the TrackNamesGenerator().

        """
        self._tracknames = track_names

    # ------------------------------------------------------------------------

    def set_trackalign( self, ta):
        """Set the aligner, required to create tracks (if any).

        :param ta:

        """
        self._aligntrack = ta

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    def split(self, inputaudio, phontier, toktier, diralign):
        """Main method to write tracks from the given data.

        :param inputaudio: (src) File name of the audio file.
        :param phontier: (Tier) Tier with phonetization to split.
        :param toktier: (Tier) Tier with tokenization to split.
        :param diralign: (str) Directory to put units.

        :returns: List of tracks with (start-time end-time)

        """
        if phontier.IsTimeInterval() is False:
            raise BadInputError
        if toktier is not None:
            if toktier.IsTimeInterval() is False:
                toktier = None

        tracks = self.write_text_tracks(phontier, toktier, diralign)
        self.write_audio_tracks(inputaudio, tracks, diralign)

        return tracks

    # ------------------------------------------------------------------------

    def write_text_tracks(self, phontier, toktier, diralign):
        """Write tokenization and phonetization of tiers into separated track files.

        :param phontier: (Tier) time-aligned tier with phonetization to split
        :param toktier:  (Tier) time-aligned tier with tokenization to split
        :param diralign: (str) the directory to write tracks.

        """
        tokens = True
        if toktier is None:
            toktier = phontier.Copy()
            tokens = False
        if phontier.GetSize() != toktier.GetSize():
            raise SizeInputsError(phontier.GetSize(), toktier.GetSize())

        units = []
        for annp, annt in zip(phontier, toktier):

            b = annp.GetLocation().GetBegin().GetMidpoint()
            e = annp.GetLocation().GetEnd().GetMidpoint()
            units.append((b, e))

            # Here we write only the text-label with the best score,
            # we don't care about alternative text-labels
            fnp = self._tracknames.phones_filename(diralign, len(units))
            textp = annp.GetLabel().GetValue()
            textp = textp.replace('\n', ' ')
            self._write_text_track(fnp, textp)

            fnt = self._tracknames.tokens_filename(diralign, len(units))
            label = annt.GetLabel()
            if tokens is False and label.IsSpeech() is True:
                textt = " ".join(["w_"+str(i+1) for i in range(len(textp.split()))])
            else:
                textt = label.GetValue()
                textt = textt.replace('\n', ' ')

            self._write_text_track(fnt, textt)

        return units

    # ------------------------------------------------------------------------

    def write_audio_tracks(self, inputaudio, units, diralign, silence=0.):
        """Write the first channel of an audio file into separated track files.
        Re-sample to 16000 Hz, 16 bits.

        :param inputaudio: (src) File name of the audio file.
        :param units: (list) List of tuples (start-time,end-time) of tracks.
        :param diralign: (str) Directory to write audio tracks.
        :param silence: (float) Duration of a silence to surround the tracks.

        """
        channel = autils.extract_audio_channel(inputaudio, 0)
        channel = autils.format_channel(channel, 16000, 2)

        for track, u in enumerate(units):
            (s, e) = u
            trackchannel = autils.extract_channel_fragment( channel, s, e, silence)
            trackname = self._tracknames.audio_filename(diralign, track+1)
            autils.write_channel(trackname, trackchannel)

    # ------------------------------------------------------------------------

    def _write_text_track(self, trackname, trackcontent):
        """Write a raw text in a file.

        """
        with codecs.open(trackname, "w", sg.__encoding__) as fp:
            fp.write(trackcontent)

# ----------------------------------------------------------------------------


class TracksReader(Transcription):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Read time-aligned segments, convert into Tier.

    """
    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new SegmentsIn instance.

        """
        super(TracksReader, self).__init__(name, mintime, maxtime)
        self.alignerio = AlignerIO()
        self._radius = 0.005
        self._tracknames = TrackNamesGenerator()

    # ------------------------------------------------------------------------

    def set_tracksnames(self, tracknames):
        self._tracknames = tracknames

    # ------------------------------------------------------------------------

    def read(self, dirname, units):
        """Read a set of alignment files and set as tiers.

        :param dirname: (str) the input directory containing a set of unit
        :param units: (list) List of units with start/end times

        """
        # Verify if the directory exists
        if os.path.exists(dirname) is False:
            raise NoDirectoryError(dirname=dirname)

        # Create new tiers
        itemp = self.NewTier("PhonAlign")
        itemw = self.NewTier("TokensAlign")

        # Explore each unit to get alignments
        for track in range(len(units)):

            # Get real start and end time values of this unit.
            unitstart, unitend = units[track]

            basename = self._tracknames.align_filename(dirname, track+1)
            _phonannots,_wordannots = self.alignerio.read_aligned(basename)

            # Append alignments in tiers
            self._append_tuples(itemp, _phonannots, unitstart, unitend)
            self._append_tuples(itemw, _wordannots, unitstart, unitend)

        # Adjust Radius
        if itemp.GetSize() > 1:
            itemp[-1].GetLocation().SetEndRadius(0.)
        if itemw.GetSize() > 1:
            itemw[-1].GetLocation().SetEndRadius(0.)
            try:
                self._hierarchy.add_link('TimeAlignment', itemp, itemw)
            except Exception:
                pass

    # ------------------------------------------------------------------------

    def _append_tuples(self, tier, tdata, delta, unitend):
        """Append a list of (start,end,text,score) into the tier.
        Shift start/end of a delta value and set the last end value.

        """
        try:

            for i,t in enumerate(tdata):
                (loc_s, loc_e, lab, scr) = t
                loc_s += delta
                loc_e += delta
                if i == (len(tdata)-1):
                    loc_e = unitend

                # prepare the code in case we'll find a solution with
                # alternatives phonetizations/tokenization....
                #lab = [lab]
                #scr = [scr]
                #label = Label()
                #for l,s in zip(lab,scr):
                #    label.AddValue(Text(l,s))
                label = Label(Text(lab, scr))
                annotationw = Annotation(TimeInterval(TimePoint(loc_s, self._radius), TimePoint(loc_e, self._radius)),
                                         label)
                tier.Append(annotationw)

        except Exception:
            pass
