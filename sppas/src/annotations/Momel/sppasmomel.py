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
# File: sppasmomel.py
# ----------------------------------------------------------------------------

import sys

from annotations.sppasbase import sppasBase

from annotationdata.transcription import Transcription
from annotationdata.annotation import Annotation
from annotationdata.ptime.point import TimePoint
from annotationdata.label.label import Label
import annotationdata.io

from annotationdata.pitch import Pitch
from annotations.Momel.momel import Momel

# ---------------------------------------------------------------------------

class sppasMomel( sppasBase ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      SPPAS integration of Momel.

    """
    def __init__(self, logfile=None):
        """
        Constructor.

        @param logfile (sppasLog) is a log file utility class member.

        """
        sppasBase.__init__(self, logfile)

        self.momel = Momel()
        self.PAS_TRAME = 10.

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """
        Fix all options.

        @param options (option)

        """
        for opt in options:

            key = opt.get_key()

            if "lfen1" == key:
                self.momel.set_option_win1( opt.get_value() )
                self._options['lfen1'] = opt.get_value()

            elif "hzinf" == key:
                self.momel.set_option_lo( opt.get_value() )
                self._options['hzinf'] = opt.get_value()

            elif "hzsup" == key:
                self.momel.set_option_hi( opt.get_value() )
                self._options['hzsup'] = opt.get_value()

            elif "maxec" == opt.get_key():
                self.momel.set_option_maxerr( opt.get_value() )
                self._options['maxec'] = opt.get_value()

            elif "lfen2" == opt.get_key():
                self.momel.set_option_win2( opt.get_value() )
                self._options['lfen2'] = opt.get_value()

            elif "seuildiff_x" == opt.get_key():
                self.momel.set_option_mind( opt.get_value() )
                self._options['seuildiff_x'] = opt.get_value()

            elif "seuildiff_y" == opt.get_key():
                self.momel.set_option_minr( opt.get_value() )
                self._options['seuildiff_y'] = opt.get_value()

            elif "glitch" == opt.get_key():
                self.momel.set_option_elim_glitch( opt.get_value() )
                self._options['glitch'] = opt.get_value()

    # ------------------------------------------------------------------------

    def set_pitch(self, inputfilename):
        """
        Load pitch values from a file.

        @return A list of pitch values (one value each 10 ms).

        """
        pitch = annotationdata.io.read( inputfilename )
        pitchlist = pitch.get_pitch_list()
        if len(pitchlist) == 0:
            raise IOError('Error while reading '+inputfilename+'\nEmpty pitch tier.\n')
        return pitchlist

    # ------------------------------------------------------------------

    def __print_tgts(self, targets, output):
        for i in range(len(targets)):
            output.write( str( "%g"%(targets[i].get_x() * self.PAS_TRAME) ) )
            output.write( " " )
            output.write( str( "%g"%targets[i].get_y() ) )
            output.write( "\n" )

    def print_targets(self, targets, outputfile=None, trs=None):
        """
        Print the set of selected targets.

        """
        if outputfile is not None:
            if outputfile is "STDOUT":
                output=sys.stdout
                self.__print_tgts(targets, output)
            elif outputfile.lower().endswith('momel') is True:
                output = open(outputfile,"w")
                self.__print_tgts(targets, output)
                output.close()

        if trs is not None:
            # Attention: time in targets is in milliseconds!
            tier = trs.NewTier(name="Momel")
            for i in range(len(targets)):
                try:
                    _time  = targets[i].get_x() * (0.001*self.PAS_TRAME)
                    _label = str("%d"%(targets[i].get_y()))
                    tier.Append(Annotation(TimePoint(_time), Label(_label)))
                except Exception:
                    if self.logfile is not None:
                        self.logfile.print_message("Ignore target: time="+str(_time)+" and value="+_label, indent=2,status=3)

            if outputfile is not None and outputfile.lower().endswith('.pitchtier'):
                trsp=Transcription()
                trsp.Add(tier)
                try:
                    annotationdata.io.write(outputfile, trsp)
                except Exception:
                    if self.logfile is not None:
                        self.logfile.print_message("Can't write PitchTier output file.",status=-1)
            return tier

    # ------------------------------------------------------------------

    def run(self, inputfilename, trsoutput=None, outputfile=None):
        """
        Apply momel from a pitch file.

        """
        self.print_options()
        self.print_diagnosis( inputfilename )

        # Get pitch values from the input
        pitch = self.set_pitch( inputfilename )
        # Selected values (Target points) for this set of pitch values
        targets = []

        # List of pitch values of one **estimated** Inter-Pausal-Unit (ipu)
        ipupitch = []
        # Number of consecutive null F0 values
        nbzero  = 0
        # Current time value
        curtime = 0
        # For each f0 value of the wav file
        for p in pitch:
            if p == 0:
                nbzero += 1
            else:
                nbzero = 0
            ipupitch.append( p )

            # If the number of null values exceed 300ms,
            # we consider this is a silence and estimate Momel
            # on the recorded list of pitch values of the **estimated** IPU.
            if (nbzero*self.PAS_TRAME) > 299:
                if len(ipupitch)>0 and ( len(ipupitch) > nbzero):
                    # Estimates the real start time of the IPU
                    ipustarttime = curtime - ( len(ipupitch) ) + 1
                    try:
                        # It is supposed ipupitch starts at time = 0.
                        iputargets = self.momel.annotate( ipupitch )
                    except Exception as e:
                        if self.logfile is not None:
                            self.logfile.print_message('No Momel annotation between time '+ str(ipustarttime*0.01) +" and "+ str(curtime*0.01)+" due to the following error: " +str(e),indent=2,status=-1)
                        else:
                            print "Momel Error: " + str(e)
                        iputargets = []
                        pass
                    # Adjust time values in the targets
                    for i in range( len(iputargets) ):
                        x = iputargets[i].get_x()
                        iputargets[i].set_x( ipustarttime + x )
                    # add this targets to the targets list
                    targets = targets + iputargets
                    del ipupitch[:]

            curtime += 1

        # last ipu
        if len(ipupitch)>0 and ( len(ipupitch) > nbzero):
            try:
                iputargets = self.momel.annotate( ipupitch )
            except Exception as e:
                if self.logfile is not None:
                    self.logfile.print_message('No Momel annotation between time '+ str(ipustarttime*0.01) +" and "+ str(curtime*0.01)+" due to the following error: " +str(e),indent=2,status=-1)
                else:
                    print "error: " + str(e)
                    iputargets = []
                pass
            ipustarttime = curtime - ( len(ipupitch) )
            # Adjust time values
            for i in range( len(iputargets) ):
                x = iputargets[i].get_x()
                iputargets[i].set_x(ipustarttime + x)
            targets = targets + iputargets


        # Print results and/or estimate INTSINT (if any)
        if trsoutput:
            trsm = Transcription("TrsMomel")
            if outputfile:
                momeltier = self.print_targets(targets, outputfile, trs=trsm)
            else:
                momeltier = self.print_targets(targets, outputfile=None, trs=trsm)
            if self.logfile is not None:
                self.logfile.print_message(str(len(targets))+ " targets found.",indent=2,status=3)

            momeltier.SetRadius(0.005) # because one pitch estimation each 10ms...
            annotationdata.io.write( trsoutput, trsm )
        elif outputfile:
            self.print_targets(targets, outputfile, trs=None)
        else:
            self.print_targets(targets, outputfile='STDOUT', trs=None)

    # ------------------------------------------------------------------
