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

    src.annotations.Align.aligntrack.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import codecs

from sppas.src.config import sg
from sppas.src.utils.makeunicode import sppasUnicode

from .. import t
from .aligners import DEFAULT_ALIGNER
from .aligners import instantiate as aligners_instantiate
from .aligners import check as aligners_check

# ----------------------------------------------------------------------------

MSG_EMPTY_INTERVAL = (t.gettext(":INFO 1222: "))

# ----------------------------------------------------------------------------


class AlignTrack(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Automatic segmentation of a segment of speech.

    Speech segmentation of a unit of speech (an IPU/utterance/sentence/segment)
    at phones and tokens levels.
    This class is mainly an interface with aligners.

    It is expected that all the following data were previously properly
    fixed:
        - audio file: 1 channel, 16000 Hz, 16 bits;
        - tokenization: UTF-8 encoding file (optional);
        - phonetization: UTF-8 encoding file;
        - acoustic model: HTK-ASCII (Julius and HVite expect this model format);
        and that:
        - both the AC and phonetization are based on the same phone set;
        - both the tokenization and phonetization contain the same number of words.

    """
    def __init__(self, model, alignername=DEFAULT_ALIGNER):
        """ Create a AlignTrack instance.

        :param model: (str) Name of the directory of the acoustic model.
        It is expected to contain at least a file with name "hmmdefs".
        It can also contain:
            - tiedlist file;
            - monophones.repl file;
            - config file.
        Any other file will be ignored.
        :param alignername: (str) The identifier name of the aligner.

        """
        # Options, must be fixed before to instantiate the aligner
        self._infersp = False

        # The acoustic model directory
        self._modeldir = model

        # The automatic alignment system, and the "basic".
        # The basic aligner is used:
        #   - when the track segment contains only one phoneme;
        #   - when the track segment does not contain phonemes.
        self._alignerid = None
        self._aligner = None
        self.set_aligner(alignername)
        self._basicaligner = aligners_instantiate(None)
        self._instantiate_aligner()

    # ------------------------------------------------------------------------

    def set_model(self, model):
        """ Fix an acoustic model to perform time-alignment.

        :param model: (str) Name of the directory of the acoustic model.

        """
        self._modeldir = model
        self._instantiate_aligner()

    # ----------------------------------------------------------------------

    def set_aligner(self, alignername):
        """ Fix the name of the aligner, one of aligners.ALIGNERS_TYPES.

        :param alignername: (str) Case-insensitive name of an aligner system.

        """
        alignername = aligners_check(alignername)
        self._alignerid = alignername
        self._instantiate_aligner()

    # ----------------------------------------------------------------------

    def set_infersp(self, infersp):
        """ Fix the automatic inference of short pauses.

        :param infersp: (bool) If infersp is set to True, a short pause is
        added at the end of each token, and the automatic aligner will infer
        if it is relevant or not.

        """
        self._infersp = infersp
        self._aligner.set_infersp(infersp)

    # ----------------------------------------------------------------------

    def get_aligner(self):
        """ Return the aligner name identifier. """

        return self._alignerid

    # ----------------------------------------------------------------------

    def get_aligner_ext(self):
        """ Return the output file extension the aligner will use. """

        return self._aligner.get_outext()

    # ----------------------------------------------------------------------

    def set_aligner_ext(self, ext):
        """ Fix the output file extension the aligner will use. """

        self._aligner.set_outext(ext)

    # ----------------------------------------------------------------------

    def get_model(self):
        """ Return the model directory name. """

        return self._modeldir

    # ------------------------------------------------------------------------

    def segmenter(self, audio_filename, phonname, tokenname, alignname):
        """ Call an aligner to perform speech segmentation and manage errors.

        :param audio_filename: (str) the audio file name of an IPU
        :param phonname: (str) the file name with the phonetization
        :param tokenname: (str) the file name with the tokenization
        :param alignname: (str) the file name to save the result WITHOUT extension

        :returns: A message of the aligner in case of any problem, or
        an empty string if success.

        """
        # Get the phonetization and tokenization strings to time-align.
        phones = ""
        tokens = ""

        if phonname is not None:
            phones = self._readline(phonname)
        self._aligner.set_phones(phones)
        self._basicaligner.set_phones(phones)

        if tokenname is not None:
            tokens = self._readline(tokenname)
        self._aligner.set_tokens(tokens)
        self._basicaligner.set_tokens(tokens)

        # Do not align nothing!
        if len(phones) == 0:
            self._basicaligner.run_alignment(audio_filename, alignname)
            return MSG_EMPTY_INTERVAL

        # Do not align only one phoneme!
        if len(phones.split()) <= 1 and "-" not in phones:
            self._basicaligner.run_alignment(audio_filename, alignname)
            return ""

        # Execute Alignment
        ret = self._aligner.check_data()
        ret += self._aligner.run_alignment(audio_filename, alignname)

        return ret

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _instantiate_aligner(self):
        """ Instantiate self._aligner to the appropriate Aligner system. """

        self._aligner = aligners_instantiate(self._modeldir, self._alignerid)
        self._aligner.set_infersp(self._infersp)

    # ------------------------------------------------------------------------

    def _readline(self, filename):
        """ Read the first line of filename, and return it as a unicode formatted string. """

        line = ""
        try:
            with codecs.open(filename, 'r', sg.__encoding__) as fp:
                sp = sppasUnicode(fp.readline())
                line = sp.to_strip()
        except Exception:
            return ""

        return line
