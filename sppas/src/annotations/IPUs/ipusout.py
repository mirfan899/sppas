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

    src.annotations.ipusout.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import codecs
import os

import sppas
from sppas.src.audiodata.autils import frames2times
import sppas.src.audiodata.aio
import sppas.src.annotationdata.aio
from sppas.src.audiodata.audio import sppasAudioPCM
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotationdata.ptime.point import TimePoint
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.annotation import Annotation

# ---------------------------------------------------------------------------


class IPUsOut(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Writer for IPUs.

    """
    def __init__(self, tracks):
        """ Creates a new IPUsOut instance.

        :param tracks: (List of tuples)

        """
        super(IPUsOut, self).__init__()

        self.tracks = list()
        self.set_tracks(tracks)

    # ------------------------------------------------------------------
    # Manage Tracks
    # ------------------------------------------------------------------

    @staticmethod
    def check_tracks(tracks):
        """ Checks if the given list of tracks is okay.
        Raise exception if error.

        :param tracks: List of tuples (from_pos,to_pos)

        """
        return [(int(s), int(e)) for (s, e) in tracks]

    # ------------------------------------------------------------------

    def set_tracks(self, tracks):
        """ Set a new list of tracks.

        :param tracks: List of tuples (from_pos,to_pos)

        """
        if tracks is not None:
            self.tracks = IPUsOut.check_tracks(tracks)
        else:
            self.tracks = list()

    # ------------------------------------------------------------------
    # Convert methods
    # ------------------------------------------------------------------

    def tracks2transcription(self, ipustrs, ipusaudio, add_ipu_idx=False):
        """ Create a Transcription object from tracks.

        :param ipustrs: (IPUsTrs)
        :param ipusaudio: (IPUsAudio)
        :param add_ipu_idx: (bool)

        """
        if len(self.tracks) == 0:
            raise IOError('No IPUs to write.\n')

        # Extract the info we need from IPUsAudio
        framerate = ipusaudio.get_channel().get_framerate()
        end_time = ipusaudio.get_channel().get_duration()

        # Extract the info we need from ipustrs
        try:
            medialist = ipustrs.trsinput.GetMedia()
            if len(medialist) > 0:
                media = medialist[0]
            else:
                media = None
        except Exception:
            media = None
        units = ipustrs.get_units()
        if len(units) != 0:
            if len(self.tracks) != len(units):
                raise Exception('Inconsistent number of tracks and units. '
                                'Got %d audio tracks, and %d units.\n' % (len(self.tracks), len(units)))

        # Create the transcription and tiers
        trs = Transcription("IPU-Segmentation")
        tieripu = trs.NewTier("IPUs")
        tier = trs.NewTier("Transcription")
        radius = ipusaudio.get_win_length() / 8.
        # vagueness is win_length divided by 4 (see "refine" method of sppasChannelSilence class)
        # radius is vagueness divided by 2

        # Convert the tracks: from frames to times
        tracks_times = frames2times(self.tracks, framerate)
        i = 0
        to_prec = 0.

        for (from_time, to_time) in tracks_times:

            # From the previous track to the current track: silence
            if to_prec < from_time:
                begin = to_prec
                end = from_time
                a = Annotation(TimeInterval(TimePoint(begin, radius), TimePoint(end, radius)), Label("#"))
                tieripu.Append(a)
                tier.Append(a.Copy())

            # New track with speech
            begin = from_time
            end = to_time

            # ... IPU tier
            label = "ipu_%d" % (i+1)
            a = Annotation(TimeInterval(TimePoint(begin, radius), TimePoint(end, radius)), Label(label))
            tieripu.Append(a)

            # ... Transcription tier
            if add_ipu_idx is False:
                label = ""
            if len(units) > 0:
                label = label + " " + units[i]
            a = Annotation(TimeInterval(TimePoint(begin, radius), TimePoint(end, radius)), Label(label))
            tier.Append(a)

            # Go to the next
            i += 1
            to_prec = to_time

        # The end is a silence?
        if to_prec < end_time:
            begin = TimePoint(to_prec, radius)
            end = TimePoint(end_time, radius)
            if begin < end:
                a = Annotation(TimeInterval(begin, end), Label("#"))
                tieripu.Append(a)
                tier.Append(a.Copy())

        # Link both tiers: IPU and Transcription
        try:
            trs.GetHierarchy().add_link('TimeAssociation', tieripu, tier)
        except Exception:
            pass

        # Set media
        if media is not None:
            trs.AddMedia(media)
            for tier in trs:
                tier.SetMedia(media)

        return trs

    # ------------------------------------------------------------------
    # Writer methods
    # ------------------------------------------------------------------

    def write_list(self, filename, ipustrs, ipusaudio):
        """ Write the list of tracks: from_time to_time (in seconds).
        Last line is the audio file duration.

        :param filename: (str) Name of the file to write the list
        :param ipustrs: (IPUsTrs)
        :param ipusaudio: (IPUsAudio)

        """
        # Convert the tracks: from frames to times
        tracks_times = frames2times(self.tracks, ipusaudio.get_channel().get_framerate())

        with codecs.open(filename, 'w', sppas.__encoding__) as fp:
            idx = 0

            for (from_time, to_time) in tracks_times:
                fp.write("%.4f %.4f " % (from_time, to_time))

                # if we assigned a filename to this tracks...
                if len(ipustrs.get_names()) > 0 and idx < len(ipustrs.get_names()):
                    # ustr = ipustrs.get_names()[idx].encode('utf8')
                    # fp.write(ustr.decode(encoding)+"\n")
                    fp.write(ipustrs.get_names()[idx] + "\n")
                else:
                    fp.write("\n")

                idx += 1

            # Finally, print audio duration
            fp.write("%.4f\n" % ipusaudio.get_channel().get_duration())

    # ------------------------------------------------------------------

    def write_tracks(self, ipustrs, ipusaudio, output, extension_trs, extension_audio):
        """ Write tracks in an output directory.
        Print only errors in a log file.

        :param ipustrs: (IPUsTrs)
        :param ipusaudio: (IPUsAudio)
        :param output: (str) Directory name
        :param extension_trs: (str) Extension of the file name for track units (or None)
        :param extension_audio: (str) Extension of the file name for audio tracks

        """
        if not os.path.exists(output):
            os.mkdir(output)

        if extension_trs is not None:
            self.write_text_tracks(ipustrs, ipusaudio, output, extension_trs)

        if extension_audio is not None:
            self.write_audio_tracks(ipustrs, ipusaudio, output, extension_audio)

    # ------------------------------------------------------------------

    def write_text_tracks(self, ipustrs, ipusaudio, output, extension):
        """ Write the units in track files.

        :param ipustrs: (IPUsTrs)
        :param ipusaudio: (IPUsAudio)
        :param output: (str) Directory name
        :param extension: (str) Extension of the file name for track units (or None)

        """
        if not os.path.exists(output):
            os.mkdir(output)

        if extension is None:
            raise IOError('An extension is required to write units.')

        # Get units and names
        units = ipustrs.get_units()
        names = ipustrs.get_names()

        # Convert the tracks: from frames to times
        tracks_times = frames2times(self.tracks, ipusaudio.get_channel().get_framerate())

        # Write text tracks
        for i, track in enumerate(tracks_times):
            track_basename = ""
            if len(names) > 0 and len(names[i]) > 0:
                # Specific names are given
                track_basename = os.path.join(output, names[i])
            else:
                track_basename = os.path.join(output, "track_%.06d" % (i+1))

            track_txtname = track_basename+"."+extension
            if extension.lower() == "txt":
                IPUsOut.__write_txt_track(track_txtname, units[i])
            else:
                d = track[1] - track[0]
                IPUsOut.__write_trs_track(track_txtname, units[i], d)

    # ------------------------------------------------------------------

    def write_audio_tracks(self, ipustrs, ipusaudio, output, extension):
        """ Write the audio in track files.

        :param ipustrs: (IPUsTrs)
        :param ipusaudio: (IPUsAudio)
        :param output: (str) Directory name
        :param extension: (str) Extension of the file name for audio tracks

        """
        if not os.path.exists(output):
            os.mkdir(output)

        if extension is None:
            raise IOError('An extension is required to write audio tracks.')

        if ipusaudio.get_channel() is None:
            return

        try:
            split_tracks = ipusaudio.get_track_data(self.tracks)
        except Exception as e:
            raise Exception('Split into tracks failed: %s' % e)

        names = ipustrs.get_names()

        # Write audio tracks
        for i, split_track in enumerate(split_tracks):
            track_basename = ""
            if len(names) > 0 and len(names[i])>0:
                # Specific names are given
                track_basename = os.path.join(output, names[i])
            else:
                track_basename = os.path.join(output, "track_%.06d" % (i+1))

            track_wavname = track_basename+"."+extension
            audio_out = sppasAudioPCM()
            audio_out.append_channel(ipusaudio.get_channel())
            try:
                sppas.src.audiodata.aio.save_fragment(track_wavname, audio_out, split_track)
            except Exception as e:
                raise Exception("Can't write track: %s. Error is %s" % (track_wavname, e))

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def __write_txt_track(track_filename, track_content):
        with codecs.open(track_filename,"w", sppas.__encoding__) as fp:
            fp.write(track_content)

    # ------------------------------------------------------------------

    @staticmethod
    def __write_trs_track(track_filename, track_content, duration):
        begin = TimePoint(0.)
        end = TimePoint(duration)
        ann = Annotation(TimeInterval(begin, end), Label(track_content))
        trs = Transcription()
        tier = trs.NewTier("Transcription")
        tier.Append(ann)
        sppas.src.annotationdata.aio.write(track_filename, trs)
