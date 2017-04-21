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

import sys

from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.ptime.point import TimePoint
from sppas.src.annotationdata.label.label import Label
import sppas.src.annotationdata.aio

from ..baseannot import sppasBaseAnnotation
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyInputError

from .momel import Momel

# ---------------------------------------------------------------------------


class sppasMomel(sppasBaseAnnotation):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS integration of Momel.

    """
    def __init__(self, logfile=None):
        """ Create a new sppasMomel instance.

        :param logfile: (sppasLog)

        """
        sppasBaseAnnotation.__init__(self, logfile)

        self.momel = Momel()
        self.PAS_TRAME = 10.

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """ Fix all options. Available options are:

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

            if "lfen1" == key:
                self.momel.set_option_win1(opt.get_value())
                self._options['lfen1'] = opt.get_value()

            elif "hzinf" == key:
                self.momel.set_option_lo(opt.get_value())
                self._options['hzinf'] = opt.get_value()

            elif "hzsup" == key:
                self.momel.set_option_hi(opt.get_value())
                self._options['hzsup'] = opt.get_value()

            elif "maxec" == opt.get_key():
                self.momel.set_option_maxerr(opt.get_value())
                self._options['maxec'] = opt.get_value()

            elif "lfen2" == opt.get_key():
                self.momel.set_option_win2(opt.get_value())
                self._options['lfen2'] = opt.get_value()

            elif "seuildiff_x" == opt.get_key():
                self.momel.set_option_mind(opt.get_value())
                self._options['seuildiff_x'] = opt.get_value()

            elif "seuildiff_y" == opt.get_key():
                self.momel.set_option_minr(opt.get_value())
                self._options['seuildiff_y'] = opt.get_value()

            elif "glitch" == opt.get_key():
                self.momel.set_option_elim_glitch(opt.get_value())
                self._options['glitch'] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # ------------------------------------------------------------------------

    @staticmethod
    def set_pitch(input_filename):
        """ Load pitch values from a file.

        :returns: A list of pitch values (one value each 10 ms).

        """
        pitch = sppas.src.annotationdata.aio.read(input_filename)
        pitch_list = pitch.get_pitch_list()
        if len(pitch_list) == 0:
            raise EmptyInputError(name="Pitch")

        return pitch_list

    # ------------------------------------------------------------------

    def __print_tgts(self, targets, output):
        for i in range(len(targets)):
            output.write(str("%g" % (targets[i].get_x() * self.PAS_TRAME)))
            output.write(" ")
            output.write(str("%g" % targets[i].get_y()))
            output.write("\n")

    def print_targets(self, targets, output_filename=None, trs=None):
        """ Print the set of selected targets.

        :param targets:
        :param output_filename: (str)
        :param trs: (Transcription)

        """
        if output_filename is not None:
            if output_filename is "STDOUT":
                output = sys.stdout
                self.__print_tgts(targets, output)
            elif output_filename.lower().endswith('momel') is True:
                output = open(output_filename, "w")
                self.__print_tgts(targets, output)
                output.close()

        if trs is not None:
            # Attention: time in targets is in milliseconds!
            tier = trs.NewTier(name="Momel")
            for i in range(len(targets)):
                _time = targets[i].get_x() * (0.001*self.PAS_TRAME)
                _label = str("%d" % (targets[i].get_y()))
                try:
                    tier.Append(Annotation(TimePoint(_time), Label(_label)))
                except Exception:
                    if self.logfile is not None:
                        self.logfile.print_message("Ignore target: time=" + str(_time) + " and value="+_label, indent=2, status=3)

            if output_filename is not None and output_filename.lower().endswith('.pitchtier'):
                trsp = Transcription()
                trsp.Add(tier)
                try:
                    sppas.src.annotationdata.aio.write(output_filename, trsp)
                except Exception:
                    if self.logfile is not None:
                        self.logfile.print_message("Can't write PitchTier output file.", status=-1)
            return tier

    # ------------------------------------------------------------------

    def run(self, input_filename, trsoutput=None, outputfile=None):
        """
        Apply momel from a pitch file.

        """
        self.print_options()
        self.print_diagnosis(input_filename)

        # Get pitch values from the input
        pitch = self.set_pitch(input_filename)
        # Selected values (Target points) for this set of pitch values
        targets = []

        # List of pitch values of one **estimated** Inter-Pausal-Unit (ipu)
        ipupitch = []
        # Number of consecutive null F0 values
        nbzero = 0
        # Current time value
        curtime = 0
        # For each f0 value of the wav file
        for p in pitch:
            if p == 0:
                nbzero += 1
            else:
                nbzero = 0
            ipupitch.append(p)

            # If the number of null values exceed 300ms,
            # we consider this is a silence and estimate Momel
            # on the recorded list of pitch values of the **estimated** IPU.
            if (nbzero*self.PAS_TRAME) > 299:
                if len(ipupitch)>0 and (len(ipupitch) > nbzero):
                    # Estimates the real start time of the IPU
                    ipustarttime = curtime - (len(ipupitch)) + 1
                    try:
                        # It is supposed ipupitch starts at time = 0.
                        iputargets = self.momel.annotate(ipupitch)
                    except Exception as e:
                        if self.logfile is not None:
                            self.logfile.print_message('No Momel annotation between time ' +
                                                       str(ipustarttime*0.01) +
                                                       " and " +
                                                       str(curtime*0.01) +
                                                       " due to the following error: " +
                                                       str(e), indent=2, status=-1)
                        else:
                            print("Momel Error: " + str(e))
                        iputargets = []
                        pass
                    # Adjust time values in the targets
                    for i in range(len(iputargets)):
                        x = iputargets[i].get_x()
                        iputargets[i].set_x(ipustarttime + x)
                    # add this targets to the targets list
                    targets = targets + iputargets
                    del ipupitch[:]

            curtime += 1

        # last ipu
        iputargets = []
        if len(ipupitch) > 0 and (len(ipupitch) > nbzero):
            try:
                iputargets = self.momel.annotate(ipupitch)
            except Exception as e:
                if self.logfile is not None:
                    self.logfile.print_message('No Momel annotation between time ' +
                                               str(ipustarttime*0.01) +
                                               " and " +
                                               str(curtime*0.01) +
                                               " due to the following error: " +
                                               str(e), indent=2, status=-1)
                else:
                    print("error: " + str(e))
                    iputargets = []
                pass
            ipustarttime = curtime - (len(ipupitch))
            # Adjust time values
            for i in range(len(iputargets)):
                x = iputargets[i].get_x()
                iputargets[i].set_x(ipustarttime + x)
            targets = targets + iputargets

        # Print results and/or estimate INTSINT (if any)
        if trsoutput:
            trsm = Transcription("TrsMomel")
            if outputfile:
                momeltier = self.print_targets(targets, outputfile, trs=trsm)
            else:
                momeltier = self.print_targets(targets, output_filename=None, trs=trsm)
            if self.logfile is not None:
                self.logfile.print_message(str(len(targets)) + " targets found.", indent=2, status=3)

            momeltier.SetRadius(0.005) # because one pitch estimation each 10ms...
            sppas.src.annotationdata.aio.write(trsoutput, trsm)
        elif outputfile:
            self.print_targets(targets, outputfile, trs=None)
        else:
            self.print_targets(targets, output_filename='STDOUT', trs=None)
