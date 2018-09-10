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

    src.annotations.Align.aligners.basicalign.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import sppas.src.audiodata.aio

from .basealigner import BaseAligner
from .alignerio import AlignerIO

# ---------------------------------------------------------------------------

BASIC_EXT_OUT = ["palign"]
DEFAULT_EXT_OUT = BASIC_EXT_OUT[0]

# ----------------------------------------------------------------------------


class BasicAligner(BaseAligner):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Basic automatic alignment system.

    This segmentation assign the same duration to each phoneme.
    In case of phonetic variants, the first shortest pronunciation is
    selected.

    """
    def __init__(self, model_dir=None):
        """Create a BasicAligner instance.

        This class allows to align one inter-pausal unit with the same
        duration for each phoneme. It selects the shortest in case of variants.

        :param model_dir: (str) Ignored.

        """
        super(BasicAligner, self).__init__()

        self._extensions = ["palign"]
        self._outext = self._extensions[0]
        self._name = "basic"

    # -----------------------------------------------------------------------

    def run_alignment(self, input_wav, output_align):
        """Perform the speech segmentation.

        Assign the same duration to each phoneme.

        :param input_wav: (str/float) audio input file name, or its duration
        :param output_align: (str) the output file name

        :returns: Empty string.

        """
        if isinstance(input_wav, float) is True:
            duration = input_wav
        else:
            try:
                wav_speech = sppas.src.audiodata.aio.open(input_wav)
                duration = wav_speech.get_duration()
            except:
                duration = 0.

        self.run_basic(duration, output_align)

        return ""

    # ------------------------------------------------------------------------

    def run_basic(self, duration, outputalign=None):
        """Perform the speech segmentation.
        Assign the same duration to each phoneme.

        :param duration: (float) the duration of the audio input
        :param outputalign: (str) the output file name

        :returns: the List of tuples (begin, end, phone)

        """
        # Remove variants: Select the first-shorter pronunciation of each token
        phoneslist = []
        phonetization = self._phones.strip().split()
        tokenization  = self._tokens.strip().split()
        selectphonetization = []
        delta = 0.
        for pron in phonetization:
            token = BasicAligner.select_shortest(pron)
            phoneslist.extend(token.split("-"))
            selectphonetization.append(token.replace("-", " "))

        # Estimate the duration of a phone (in centi-seconds)
        if len(phoneslist) > 0:
            delta = (duration / float(len(phoneslist))) * 100.

        # Generate the result
        if delta < 1. or len(selectphonetization) == 0:
            return self.gen_alignment([], [], [], int(duration*100.), outputalign)

        return self.gen_alignment(selectphonetization, tokenization, phoneslist, int(delta), outputalign)

    # ------------------------------------------------------------------------

    def gen_alignment(self, phonetization, tokenization, phoneslist, phonesdur, outputalign=None):
        """Write an alignment in an output file.

        :param phonetization: (list) phonetization of each token
        :param tokenization: (list) each token

        :param phoneslist: (list) each phone
        :param phonesdur: (int) the duration of each phone in centi-seconds
        :param outputalign: (str) the output file name

        """
        timeval = 0
        alignments = []
        for phon in phoneslist:
            tv1 = timeval
            tv2 = timeval + phonesdur - 1
            alignments.append((tv1, tv2, phon))
            timeval = tv2 + 1

        if len(alignments) == 0:
            alignments = [(0, int(phonesdur), "")]

        if outputalign is not None:
            outputalign = outputalign + "." + self._outext
            alignio = AlignerIO()
            alignio.write_palign(phonetization, tokenization, alignments, outputalign)

        return alignments

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    @staticmethod
    def select_shortest(pron):
        """Return the first of the shortest pronunciations of an entry.

        :param pron: (str) The phonetization of a token
        :returns: (str) pronunciation
        
        """
        if len(pron) == 0:
            return ""

        tab = pron.split("|")
        if len(tab) == 1:
            return pron

        i = 0
        m = len(tab[0])
        for n, p in enumerate(tab):
            if len(p) < m:
                i = n
                m = len(p)

        return tab[i].strip()
