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

    src.annotations.SearchIPUs.sppassearchipus.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import os

from sppas.src.config import annotations_translation
from sppas.src.config import symbols

import sppas.src.audiodata.aio
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasMedia
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasRW

from ..annotationsexc import AnnotationOptionError
from ..baseannot import sppasBaseAnnotation
from .searchipus import SearchIPUs

# ---------------------------------------------------------------------------

SIL_ORTHO = list(
    symbols.ortho.keys()
    )[list(symbols.ortho.values()).index("silence")]

_ = annotations_translation.gettext

# ---------------------------------------------------------------------------

MSG_NO_TIER = (_(":INFO 1264: "))

# ---------------------------------------------------------------------------


class sppasSearchIPUs(sppasBaseAnnotation):
    """SPPAS integration of the IPUs detection.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, logfile=None):
        """Create a new sppasSearchIPUs instance.

        :param logfile: (sppasLog)

        """
        super(sppasSearchIPUs, self).__init__(logfile, "SearchIPUs")

        self.__searcher = SearchIPUs(channel=None)

        # List of options to configure this automatic annotation
        self._options = dict()

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - threshold: volume threshold to decide a window is silence or not
            - win_length: length of window for a estimation or volume values
            - min_sil: minimum duration of a silence
            - min_ipu: minimum duration of an ipu
            - shift_start: start boundary shift value.
            - shift_end: end boundary shift value.
        
        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if "threshold" == key:
                self.set_threshold(opt.get_value())
                
            elif "win_length" == key:
                self.set_win_length(opt.get_value())
            
            elif "min_sil" == key:
                self.set_min_sil(opt.get_value())

            elif "min_ipu" == key:
                self.set_min_ipu(opt.get_value())

            elif "shift_start" == key:
                self.set_shift_start(opt.get_value())

            elif "shift_end" == key:
                self.set_shift_end(opt.get_value())

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def get_threshold(self):
        return self.__searcher.get_vol_threshold()

    def get_win_length(self):
        return self.__searcher.get_win_length()

    def get_min_sil(self):
        return self.__searcher.get_min_sil_dur()

    def get_min_ipu(self):
        return self.__searcher.get_min_ipu_dur()

    def get_shift_start(self):
        return self.__searcher.get_shift_start()

    def get_shift_end(self):
        return self.__searcher.get_shift_end()

    # -----------------------------------------------------------------------

    def set_threshold(self, value):
        """Fix the threshold volume.

        :param value: (int) RMS value used as volume threshold

        """
        self.__searcher.set_vol_threshold(value)

    # -----------------------------------------------------------------------

    def set_win_length(self, value):
        """Set a new length of window for a estimation or volume values.

        TAKE CARE:
        it cancels any previous estimation of volume and silence search.

        :param value: (float) generally between 0.01 and 0.04 seconds.

        """
        self.__searcher.set_win_length(value)

    # -----------------------------------------------------------------------

    def set_min_sil(self, value):
        """Fix the default minimum duration of a silence.

        :param value: (float) Duration in seconds.

        """
        self.__searcher.set_min_sil(value)

    # -----------------------------------------------------------------------

    def set_min_ipu(self, value):
        """Fix the default minimum duration of an IPU.

        :param value: (float) Duration in seconds.

        """
        self.__searcher.set_min_ipu(value)

    # -----------------------------------------------------------------------

    def set_shift_start(self, value):
        """Fix the start boundary shift value.

        :param value: (float) Duration in seconds.

        """
        self.__searcher.set_shift_start(value)

    # -----------------------------------------------------------------------

    def set_shift_end(self, value):
        """Fix the end boundary shift value.

        :param value: (float) Duration in seconds.

        """
        self.__searcher.set_shift_end(value)

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    @staticmethod
    def tracks_to_tier(tracks, end_time, vagueness):
        """Create a sppasTier object from tracks.

        :param tracks: (List of tuple) with (from, to) values in seconds
        :param end_time: (float) End-time of the tier
        :param vagueness: (float) vagueness used for silence search

        """
        if len(tracks) == 0:
            raise IOError('No IPUs to write.\n')

        tier = sppasTier("IPUs")
        tier.set_meta('number_of_ipus', str(len(tracks)))
        i = 0
        to_prec = 0.

        for (from_time, to_time) in tracks:

            if from_time == 0. or to_time == end_time:
                radius = 0.
            else:
                radius = vagueness / 2.

            # From the previous track to the current track: silence
            if to_prec < from_time:
                tier.create_annotation(
                    sppasLocation(
                        sppasInterval(sppasPoint(to_prec, radius),
                                      sppasPoint(from_time, radius))),
                    sppasLabel(
                        sppasTag(SIL_ORTHO))
                )

            # New track with speech
            tier.create_annotation(
                sppasLocation(
                    sppasInterval(sppasPoint(from_time, radius),
                                  sppasPoint(to_time, radius))),
                sppasLabel(
                    sppasTag("ipu_%d" % (i+1)))
            )

            # Go to the next
            i += 1
            to_prec = to_time

        # The end is a silence? Fill...
        begin = sppasPoint(to_prec, vagueness / 2.)
        if begin < end_time:
            tier.create_annotation(
                sppasLocation(
                    sppasInterval(begin, sppasPoint(end_time))),
                sppasLabel(
                    sppasTag(SIL_ORTHO))
            )

        return tier

    # -----------------------------------------------------------------------

    def _set_meta(self, tier):
        """Set meta values to the tier."""
        tier.set_meta('threshold_volume', str(self.__searcher.get_vol_threshold()))
        tier.set_meta('minimum_silence_duration', str(self.__searcher.get_min_sil_dur()))
        tier.set_meta('minimum_ipus_duration', str(self.__searcher.get_min_ipu_dur()))
        tier.set_meta('shift_ipus_start', str(self.__searcher.get_shift_start()))
        tier.set_meta('shift_ipus_end', str(self.__searcher.get_shift_end()))

        self.print_message("Information: ", indent=2)
        m1 = "Threshold volume value:     {:d}".format(self.__searcher.get_vol_threshold())
        m2 = "Threshold silence duration: {:.3f}".format(self.__searcher.get_min_sil_dur())
        m3 = "Threshold speech duration:  {:.3f}".format(self.__searcher.get_min_ipu_dur())
        m4 = "Number of IPUs found:       {:s}".format(tier.get_meta("number_of_ipus"))
        for m in (m4, m1, m2, m3):
            self.print_message(m, indent=3)

    # -----------------------------------------------------------------------

    def run(self, input_filename, output_filename=None):
        """Perform the search of IPUs process.

        :param input_filename: (str) Input audio file
        :param output_filename: (str) Resulting annotated file with IPUs
        :returns: (sppasTranscription)

        """
        self.print_filename(input_filename)
        self.print_diagnosis(input_filename)

        # Get audio and the channel we'll work on
        audio_speech = sppas.src.audiodata.aio.open(input_filename)
        idx = audio_speech.extract_channel()
        channel = audio_speech.get_channel(idx)
        self.__searcher.set_channel(channel)

        # Process the data.
        tracks = self.__searcher.get_tracks(time_domain=True)
        tier = self.tracks_to_tier(
            tracks,
            channel.get_duration(),
            self.__searcher.get_vagueness()
        )
        self._set_meta(tier)

        # Create the transcription to put the result
        trs_output = sppasTranscription(self.__class__.__name__)
        trs_output.set_meta('search_ipus_result_of', input_filename)
        trs_output.append(tier)

        extm = os.path.splitext(input_filename)[1].lower()[1:]
        media = sppasMedia(os.path.abspath(input_filename), mime_type="audio/"+extm)
        tier.set_media(media)

        # Save in a file
        if output_filename is not None:
            parser = sppasRW(output_filename)
            parser.write(trs_output)
            self.print_filename(output_filename, status=0)

        return trs_output

    # -----------------------------------------------------------------------

    def batch_processing(self, file_names, progress, output_format):
        """

        :param file_names:
        :param progress: ProcessProgressTerminal() or ProcessProgressDialog()
        :return:

        """
        if len(file_names) == 0:
            return 0
        total = len(file_names)
        files_processed_success = 0
        progress.set_header(self.__class__.__name__)
        progress.update(0, "")

        # Execute the annotation for each file in the list
        for i, f in enumerate(file_names):

            # Indicate the file to be processed
            progress.set_text(os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")")

            # Fix input/output file name
            out_name = os.path.splitext(f)[0] + output_format

            # Is there already an existing output file (in any format)!
            ext = []
            for e in sppas.src.anndata.aio.extensions_in:
                if e not in ('.txt', '.hz', '.PitchTier'):
                    ext.append(e)
            exist_out_name = self._get_filename(f, ext)

            # it's existing... but not in the expected format: convert!
            if exist_out_name is not None:
                self.print_message(
                    "A file with name {:s} is already existing."
                    "".format(exist_out_name), indent=2)
                if exist_out_name != out_name:
                    try:
                        parser = sppasRW(exist_out_name)
                        t = parser.read()
                        parser.set_filename(out_name)
                        parser.write(t)
                        # OK, it's done! just copy the file!
                        self.print_message(
                            'It was converted automatically to {:s}'
                            ''.format(out_name), indent=2)
                    except Exception:
                        pass
                self.print_message("No automatic annotation was done."
                                   "", indent=2, status=3)
            else:
                try:
                    # Execute annotation
                    self.run(f, out_name)
                    files_processed_success += 1
                except Exception as e:
                    self.print_message(
                        "{:s} for file {:s}\n".format(str(e), out_name),
                        indent=2, status=-1)

            # Indicate progress
            progress.set_fraction(float((i+1))/float(total))
            self.print_newline()

        # Indicate completed!
        progress.update(
            1,
            "Completed ({:d} files successfully over {:d} files).\n"
            "".format(files_processed_success, total)
        )
        progress.set_header("")

        return files_processed_success
