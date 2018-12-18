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

    src.annotations.FillIPUs.sppasfillipus.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import os

import sppas.src.audiodata.aio
from sppas.src.config import symbols
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasMedia
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.config import annots
import sppas.src.anndata.aio

from ..SearchIPUs.sppassearchipus import sppasSearchIPUs
from ..annotationsexc import AnnotationOptionError
from ..baseannot import sppasBaseAnnotation

from .fillipus import FillIPUs

# ---------------------------------------------------------------------------

SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]

# ---------------------------------------------------------------------------


class sppasFillIPUs(sppasBaseAnnotation):
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
        super(sppasFillIPUs, self).__init__(logfile, "SearchIPUs")

        # List of options to configure this automatic annotation
        f = FillIPUs(None, [])
        self._options = dict()
        self._options['min_ipu'] = f.get_min_ipu_dur()
        self._options['min_sil'] = f.get_min_sil_dur()

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def get_min_sil(self):
        return self._options['min_sil']

    def get_min_ipu(self):
        return self._options['min_ipu']

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
            if "min_sil" == key:
                self.set_min_sil(opt.get_value())

            elif "min_ipu" == key:
                self.set_min_ipu(opt.get_value())

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_min_sil(self, value):
        """Fix the initial minimum duration of a silence.

        :param value: (float) Duration in seconds.

        """
        self._options['min_sil'] = value

    # -----------------------------------------------------------------------

    def set_min_ipu(self, value):
        """Fix the initial minimum duration of an IPU.

        :param value: (float) Duration in seconds.

        """
        self._options['min_ipu'] = value

    # -----------------------------------------------------------------------

    def _set_meta(self, filler, tier):
        """Set meta values to the tier."""
        tier.set_meta('threshold_volume',
                      str(filler.get_vol_threshold()))
        tier.set_meta('minimum_silence_duration',
                      str(filler.get_min_sil_dur()))
        tier.set_meta('minimum_ipus_duration',
                      str(filler.get_min_ipu_dur()))

        self.print_message("Information: ", indent=2)
        m1 = "Threshold volume value:     {:d}" \
             "".format(filler.get_vol_threshold())
        m2 = "Threshold silence duration: {:.3f}" \
             "".format(filler.get_min_sil_dur())
        m3 = "Threshold speech duration:  {:.3f}" \
             "".format(filler.get_min_ipu_dur())
        for m in (m1, m2, m3):
            self.print_message(m, indent=3)

    # -----------------------------------------------------------------------

    def fill_in(self, input_audio_filename, input_filename):
        """Return a tier with transcription aligned to the audio.

        :param input_audio_filename: (str) Input audio file
        :param input_filename: (str) Input transcription file

        """
        # Get audio and the channel we'll work on
        audio_speech = sppas.src.audiodata.aio.open(input_audio_filename)
        idx = audio_speech.extract_channel()
        channel = audio_speech.get_channel(idx)

        # Get the units we'll work on
        parser = sppasRW(input_filename)
        trs = parser.read()
        if len(trs) > 1:
            pass
        if len(trs[0]) == 0:
            pass
        units = list()
        for a in trs[0]:
            units.append(a.serialize_labels())
        ipus = [u for u in units if u != SIL_ORTHO]

        # Create the instance to fill in IPUs
        filler = FillIPUs(channel, units)
        filler.set_min_ipu(self._options['min_ipu'])
        filler.set_min_sil(self._options['min_sil'])
        n = filler.fix_threshold_durations()
        if n != len(ipus):
            return

        # Process the data.
        tracks = filler.get_tracks(time_domain=True)
        tier = sppasSearchIPUs.tracks_to_tier(
            tracks,
            channel.get_duration(),
            filler.get_vagueness()
        )
        tier.set_name('Transcription')
        self._set_meta(filler, tier)
        i = 0
        for a in tier:
            if a.get_best_tag().is_silence() is False:
                a.set_labels([sppasLabel(sppasTag(ipus[i]))])
                i += 1
        return tier

    # -----------------------------------------------------------------------
    # Apply the annotation on one or several given files
    # -----------------------------------------------------------------------

    def run(self, input_audio_filename, input_filename, output_filename=None):
        """Perform the search of IPUs process.

        :param input_audio_filename: (str) Input audio file
        :param input_filename: (str) Input transcription file
        :param output_filename: (str) Resulting annotated file with IPUs
        :returns: (sppasTranscription)

        """
        tier = self.fill_in(input_audio_filename, input_filename)
        if tier is None:
            msg = "Unable to align the audio with the given transcription."
            self.print_message(msg, indent=2, status=-1)
            return

        # Create the transcription to put the result
        trs_output = sppasTranscription(self.__class__.__name__)
        trs_output.set_meta('fill_ipus_result_of', input_audio_filename)
        trs_output.set_meta('fill_ipus_result_of_trs', input_filename)
        trs_output.append(tier)

        extm = os.path.splitext(input_audio_filename)[1].lower()[1:]
        media = sppasMedia(os.path.abspath(input_audio_filename),
                           mime_type="audio/"+extm)
        tier.set_media(media)

        # Save in a file
        if output_filename is not None:
            parser = sppasRW(output_filename)
            parser.write(trs_output)

        return trs_output

    # -----------------------------------------------------------------------

    def run_for_batch_processing(self, filename, output_format):
        """Perform the annotation on a file.

        :param filename: (str) Name of the input file to annotate (audio)
        :param output_format: (str) Output file extension
        :returns: output file name or None

        """
        # Fix input/output file name
        in_name = os.path.splitext(filename)[0] + ".txt"
        out_name = self.get_out_name(filename, output_format)

        # there is already an existing transcription
        if os.path.exists(in_name) is False:
            self.print_message(
                "File not found. "
                "This annotation expects a file with name {:s}. "
                "".format(in_name), indent=1, status=4)
            return None

        self.print_diagnosis(in_name)

        # Is there already an existing IPU-seg (in any format)!
        ext = []
        for e in sppas.src.anndata.aio.extensions_in:
            if e not in ('.txt', '.hz', '.PitchTier'):
                ext.append(e)
        exist_out_name = self._get_filename(filename, ext)

        # it's existing... but not in the expected format: we convert!
        if exist_out_name is not None:
            if exist_out_name == out_name:
                self.print_message(
                    "A file with name {:s} is already existing."
                    "".format(exist_out_name), indent=2, status=annots.info)
                return None

            else:
                try:
                    parser = sppasRW(exist_out_name)
                    t = parser.read()
                    parser.set_filename(out_name)
                    parser.write(t)
                    self.print_message(
                        "A file with name {:s} was already existing."
                        'This file was exported to {:s}'
                        ''.format(exist_out_name, out_name), indent=2, status=annots.info)
                    return None
                except:
                    pass
        else:
            # Create annotation instance, fix options, run.
            try:
                self.run(filename, in_name, out_name)
            except Exception as e:
                out_name = None
                self.print_message(
                    "{:s} for file {:s}\n".format(str(e), out_name),
                    indent=2, status=-1)

        return out_name
