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

    src.annotations.Momel.sppasmomel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os

from sppas import sppasRW
from sppas import sppasTranscription
from sppas import sppasTier
from sppas import sppasLocation
from sppas import sppasPoint
from sppas import sppasLabel
from sppas import sppasTag

from sppas.src.config import annots

from ..baseannot import sppasBaseAnnotation
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyInputError
from ..annotationsexc import NoInputError

from .momel import Momel

# ---------------------------------------------------------------------------


class sppasMomel(sppasBaseAnnotation):
    """SPPAS integration of Momel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, logfile=None):
        """Create a new sppasMomel instance.

        :param logfile: (sppasLog)

        """
        super(sppasMomel, self).__init__(logfile, "Momel")
        self.momel = Momel()

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - lfen1
            - hzinf
            - hzsup
            - maxec
            - lfen2
            - seuildiff_x
            - seuildiff_y
            - glitch

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()

            if "win1" == key:
                self.momel.set_option_win1(opt.get_value())

            elif "lo" == key:
                self.momel.set_option_lo(opt.get_value())

            elif "hi" == key:
                self.momel.set_option_hi(opt.get_value())

            elif "maxerr" == opt.get_key():
                self.momel.set_option_maxerr(opt.get_value())

            elif "win2" == opt.get_key():
                self.momel.set_option_win2(opt.get_value())

            elif "mind" == opt.get_key():
                self.momel.set_option_mind(opt.get_value())

            elif "minr" == opt.get_key():
                self.momel.set_option_minr(opt.get_value())

            elif "elim_glitch" == opt.get_key():
                self.momel.set_option_elim_glitch(opt.get_value())

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_pitch(input_filename):
        """Load pitch values from a file.

        It is supposed that the given file contains a tier with name "Pitch"
        with a pitch value every 10ms, or a tier with name "PitchTier".

        :returns: A list of pitch values (one value each 10 ms).

        """
        parser = sppasRW(input_filename)
        trs = parser.read()
        pitch_tier = trs.find("Pitch")
        if pitch_tier is None:
            pitch_tier = trs.find("PitchTier")
            if pitch_tier is not None:
                pitch_list = trs.to_pitch()
            else:
                raise NoInputError
        else:
            pitch_list = [round(a.get_best_tag().get_typed_content(), 6)
                          for a in pitch_tier]

        if len(pitch_list) == 0:
            raise EmptyInputError(name="Pitch")

        return pitch_list

    # -----------------------------------------------------------------------

    def estimate_momel(self, ipu_pitch, current_time):
        """Estimate momel on an IPU.

        :param ipu_pitch: (list of float) Pitch values of an IPU.
        :param current_time: (float) Time value of the last pitch value
        :returns: (list of Anchor)

        """
        # Estimates the real start time of the IPU
        ipu_start_time = current_time - (len(ipu_pitch)) + 1

        # Search for anchors
        try:
            anchors = self.momel.annotate(ipu_pitch)
        except Exception as e:
            self.print_message(
                    'No anchors found between time ' +
                    str(ipu_start_time * 0.01) + " and time " +
                    str(current_time * 0.01) + ": " + str(e),
                    indent=2, status=annots.warning)
            anchors = list()
            pass

        # Adjust time values in the anchors
        for i in range(len(anchors)):
            anchors[i].x += ipu_start_time

        return anchors

    # -----------------------------------------------------------------------

    @staticmethod
    def anchors_to_tier(anchors):
        """Transform anchors to a sppasTier.

        Anchors are stored in frames. It is converted to seconds (a frame is
        during 10ms).

        :param anchors: (List of Anchor)
        :returns: (sppasTier)

        """
        tier = sppasTier('Momel')
        for anchor in anchors:
            tier.create_annotation(
                sppasLocation(sppasPoint(anchor.x * 0.01, 0.005)),
                sppasLabel(sppasTag(anchor.y, "float"))
            )

        return tier

    # -----------------------------------------------------------------------

    def convert(self, pitch):
        """Search for momel anchors.

        :param pitch: (list of float) pitch values samples at 10ms
        :returns: sppasTier

        """
        # Selected values (anchor points) for this set of pitch values
        targets = list()

        # List of pitch values of one **estimated** Inter-Pausal-Unit (ipu)
        ipu_pitch = []
        # Number of consecutive null F0 values
        nbzero = 0
        # Current time value
        curtime = 0
        # For each f0 value of the wav file
        for p in pitch:
            if p == 0.:
                nbzero += 1
            else:
                nbzero = 0
            ipu_pitch.append(p)

            # If the number of 0. values exceed 250ms,
            # we consider this is a silence and we estimate Momel
            # on the recorded list of pitch values of the **estimated** IPU.
            if (nbzero * 10) > 249:
                if len(ipu_pitch) > 0 and (len(ipu_pitch) > nbzero):
                    ipu_anchors = self.estimate_momel(ipu_pitch, curtime)
                    # add this targets to the targets list
                    targets.extend(ipu_anchors)
                    ipu_pitch = list()

            curtime += 1

        # last ipu
        ipu_anchors = self.estimate_momel(ipu_pitch, curtime)
        targets.extend(ipu_anchors)

        return sppasMomel.anchors_to_tier(targets)

    # -----------------------------------------------------------------------

    def run(self, input_filename, output_filename=None):
        """Apply momel from a pitch file.

        :param input_filename: (str)
        :param output_filename: (str)

        """
        # Get pitch values from the input
        pitch = self.fix_pitch(input_filename)

        # Search for anchors
        anchors_tier = self.convert(pitch)
        self.print_message(str(len(anchors_tier)) +
                           " anchors found.", indent=2, status=annots.info)

        # Fix result
        trs_output = sppasTranscription("Momel")
        trs_output.append(anchors_tier)
        trs_output.set_meta('annotation_result_of', input_filename)

        if output_filename is not None:
            parser = sppasRW(output_filename)
            parser.write(trs_output)

        return trs_output

    # -----------------------------------------------------------------------

    def get_out_name(self, filename, output_format):
        """Fix the output file name from the input one.

        :param filename: (str) Name of the input file
        :param output_format: (str) Extension of the output file

        """
        return os.path.splitext(filename)[0] + '-momel' + output_format
