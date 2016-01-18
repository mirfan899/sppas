#!/usr/bin/env python2
# -*- coding: utf8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://www.lpl-aix.fr/~bigi/sppas
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2014  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# File: audiotoaster.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Nicolas Chazeau, Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

from argparse import ArgumentParser
import os
import sys
import time

PROGRAM = os.path.abspath(__file__)
WAVETOASTER = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ))
SRC = os.path.join(WAVETOASTER, "src" )
sys.path.append(SRC)

import signals
from signals       import extensionsul, audioutils
from signals.audio import Audio
from signals.channel           import Channel
from signals.channelsmixer     import ChannelsMixer
from signals.channelformatter  import ChannelFormatter
from signals.channelsequalizer import ChannelsEqualizer
from signals.channelfragmentextracter import ChannelFragmentExtracter
from term.textprogress       import TextProgress
from term.terminalcontroller import TerminalController

sys.path.remove(SRC)


# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------

def read_settings(filename):
    """
    Read the settings file, which contains:
        - the list of audio file names,
        - the speaker name or initials,
        - the volume of each audio source,
        - the orientation of each audio source.
    @param filename is often settings.txt
    @return a list of dictionaries with extracted information

    """
    channels = []
    # Settings file given as input:
    file = open(args.s, "r")
    #we remove the first line, the header
    titles = (file.readline()).split()
    lines = file.readlines()
    file.close()

    dirname = os.path.dirname(filename)
    total= len(lines)

    for i,line in enumerate(lines):
        linesplitted = line.split()
        if len(linesplitted)<4:
            raise Exception('Error: Corrupted file. Can not parse line %s'%line)
        channelparameter = {}
        channelparameter['file']      = os.path.join(dirname, linesplitted[0])
        channelparameter['speaker']   = linesplitted[1]
        channelparameter['volume']    = int(linesplitted[2])
        channelparameter['rms']       = 0
        channelparameter['factor']    = 0
        channelparameter['panoramic'] = 0

        panoramic = linesplitted[3]
        if panoramic[0] == 'L':
            channelparameter['panoramic'] = - int(panoramic[1:])
        elif panoramic[0] == 'R':
            channelparameter['panoramic'] = int(panoramic[1:])

        channels.append( channelparameter )
        if p: p.update(float(i)/total, "Audio " + str(i+1) + " of " + str(total))

    return channels

# ----------------------------------------------------------------------------

def check_files( settings ):
    """
    Check filenames of a list of channel parameters.
    @param settings: a list of dictionaries with extracted information from a settings file.
    @raise Exception if at least one file is not correct.

    """

    for f in settings:
        if not os.path.exists( f['file'] ):
            raise Exception('The file %s does not exist.'%f['file'])

# ----------------------------------------------------------------------------

def extract_channels( settings, factor=0, channel=0, p=None ):
    """
    Extract the first channel for each sound file of the settings.
    @param settings: a list of dictionaries with extracted information from a settings file.
    @param factor: coefficient to apply to the volume
    @param channel: index of the channel to extract
    @param p is a progress dialog

    """
    total = len( settings )

    for i,channelparameter in enumerate(settings):
        if p: p.update(float(i)/total, "Channel " + str(i+1) + " of " + str(total))

        audio = signals.open( channelparameter['file'] )

        # CHANNEL EXTRACTION
        idx = audio.extract_channel( channel )
        channelparameter['channel'] = audio.get_channel(idx)

        # RMS EXTRACTION
        if factor > 0:
            rms = audioutils.get_rms(channelparameter['channel'].frames, audio.get_sampwidth())
            rmswanted = audioutils.mel2db(audioutils.db2mel(rms)*factor)
            channelparameter['factor'] = rmswanted/rms

        audio.close()
        del audio

# ----------------------------------------------------------------------------

def equalize_channels( settings, p=None ):
    """
    Equalize channels of the settings.
    @param settings: a list of dictionaries with extracted information from a settings file.
    @param p is a progress dialog

    """
    equalizer = ChannelsEqualizer()

    if p: p.update(0.25, "Load channels to equalize. ")
    for channel in settings:
        equalizer.append_channel( channel['channel'] )

    if p: p.update(0.50, "Equalize each channel... ")
    equalizer.equalize()

    if p: p.update(0.90, "Save equalized channels. ")
    for i,channel in enumerate(settings):
        channel['channel'] = equalizer.get_channel(i)

# ----------------------------------------------------------------------------

def fragment_channels( settings, begin, end, p=None ):
    """
    Fragment channels of the settings.
    @param settings: a list of dictionaries with extracted information from a settings file.
    @param p is a progress dialog

    """

    for channel in settings:
        extracter = ChannelFragmentExtracter(channel['channel'])
        channel['channel'] = extracter.extract_fragment(begin*channel['channel'].get_framerate(), end*channel['channel'].get_framerate())
        del extracter

# ----------------------------------------------------------------------------

def mix_channels( settings, p=None ):
    """
    Mix channels of the settings.
    @param settings: a list of dictionaries with extracted information from a settings file.
    @param p is a progress dialog

    """
    #variables for displaying
    total = len(settings)

    mixerleft = ChannelsMixer()
    mixerright = ChannelsMixer()

    for i,channel in enumerate(settings):
        if p: p.update(float(i)/total, "Formatting channel " + str(i+1) + " of " + str(total))

        coeffLeft  = 50.
        coeffRight = 50.
        if channel['panoramic'] < 0:
            coeffLeft   = float( 100 - channel['panoramic'] )/2
            coeffRight = float( 100 - coeffLeft ) - channel['factor'] * channel['panoramic']
        elif channel['panoramic'] > 0:
            coeffRight = float( 100 + channel['panoramic'] )/2
            coeffLeft  = float( 100 - coeffRight ) + channel['factor'] * channel['panoramic']

        mixerleft.append_channel( channel['channel'], coeffLeft/100.  * (channel['volume'])/100.)
        mixerright.append_channel(channel['channel'], coeffRight/100. * (channel['volume'])/100.)

    return mixerleft,mixerright

# ----------------------------------------------------------------------------


def show_channels( settings ):
    """
    Print channel's information of the settings.
    @param settings: a list of dictionaries with extracted information from a settings file.
    """
    print "Show channels: "
    for channel in settings:
        print " - ",channel['file']
        print "     * sampwidth:    ",channel['channel'].get_sampwidth()
        print "     * framerate:    ",channel['channel'].get_framerate()
        print "     * nframes:      ",channel['channel'].get_nframes()
        print "     * rms:          ",channel['channel'].get_rms()

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -s settingfile -o outputfile [options]" % os.path.basename(PROGRAM), description="A script mix mono channel audio files")

parser.add_argument("-o", metavar="file", required=True, help='Audio Output file name')
parser.add_argument("-s", metavar="file", required=True, help='The file which contains settings')
parser.add_argument("-l", default=0, metavar="value", type=float, help='The factor to determine the amount of sound from a L or R channel heard in the other (default=0.5)')
parser.add_argument("-b", default=0, metavar="value", type=float, help='The position (in seconds) when begins the mix')
parser.add_argument("-e", default=0, metavar="value", type=float, help='The position (in seconds) when ends the mix')
parser.add_argument("-v", metavar="value", type=int, default=1, help="Verbosity level: 0, 1 or 2 (default=1)" )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

fileName, fileExtension = os.path.splitext(args.o)
if not fileExtension in extensionsul:
    print "Error: Unsupported output extension %s (must be one of: %s)"%(fileExtension,",".join(extensionsul))
    sys.exit(1)

verbose = args.v

#======================== READING THE PARAMETERS ============================#

if verbose > 1:
    print "Start process at: %s"%time.strftime('%d/%m/%y %H:%M:%S',time.localtime())
p=None
if verbose > 0:
    p = TextProgress()
    p.set_new()
    p.set_header("Reading parameters")
    p.update(0,"")

try:
    settings = read_settings( args.s )
except Exception as e:
    print e
    sys.exit(1)

if verbose > 0:
    p.update(1, "")
    del p
if verbose > 1:
    print "\nEnd reading at %s"%time.strftime('%d/%m/%y %H:%M:%S',time.localtime())

#========================  CHECKING FILENAMES   ============================#

try:
    check_files( settings )
except Exception as e:
    print e
    sys.exit(1)

#========================EXTRACTING THE CHANNELS============================#

#variables for displaying
p = None
if verbose > 0:
    p = TextProgress()
    p.set_new()
    p.set_header("Extracting channels")
    p.update(0,"")

if verbose > 1:
    print "\nBegin extracting channels at %s"%time.strftime('%d/%m/%y %H:%M:%S',time.localtime())

try:
    extract_channels( settings, factor=args.l, channel=0, p=p )
except Exception as e:
    print e
    sys.exit(1)

if verbose > 0:
    p.update(1, "")
    del p
if verbose > 1:
    print "\nEnd extracting channels at %s"%time.strftime('%d/%m/%y %H:%M:%S',time.localtime())
    show_channels( settings )

#========================CHANNELS EQUALIZATION============================#

if verbose > 0:
    p = TextProgress()
    p.set_new()
    p.set_header("Equalizing channels")
    p.update(0,"")

if verbose > 1:
    print "\nBegin equalizing channels at %s"%time.strftime('%d/%m/%y %H:%M:%S',time.localtime())

try:
    equalize_channels( settings, p )
except Exception as e:
    print e
    sys.exit(1)

if verbose > 0:
    p.update(1, "")
    del p
if verbose > 1:
    print "\nEnd equalizing channels at %s"%time.strftime('%d/%m/%y %H:%M:%S',time.localtime())
    show_channels( settings )

#========================FRAGMENT EXTRACTION============================#

if args.b != 0 or args.e != 0:
    p = None
    if verbose > 0:
        p = TextProgress()
        p.set_new()
        p.set_header("Extracting fragments")
        p.update(0,"")

    try:
        fragment_channels( settings, args.b, args.e, p )
    except Exception as e:
        print e
        sys.exit(1)

    if verbose > 0:
        p.update(1, "")
        del p

#========================OUTPUT CHANNELS LEFT AND RIGHT============================#
p = None
if verbose > 0:
    p = TextProgress()
    p.set_new()
    p.set_header("Preparing left and right output channels")
    p.update(0,"")

if verbose > 1:
    print "\nBegin preparing L/R channels at %s"%time.strftime('%d/%m/%y %H:%M:%S',time.localtime())

try:
    mixerleft,mixerright = mix_channels( settings, p )
    sampleswidth = settings[0]['channel'].get_sampwidth()
except Exception as e:
    print e
    sys.exit(1)

if verbose > 0:
    p.update(1, "")
    del p
if verbose > 1:
    print "\nEnd preparing L/R channels at %s"%time.strftime('%d/%m/%y %H:%M:%S',time.localtime())

#========================VERIFY CLIPPING============================#

p = None
if verbose > 0:
    p = TextProgress()
    p.set_new()
    p.set_header("Getting the factor to avoid clipping")

if verbose > 1:
    print "\nBegin getting factor at %s"%time.strftime('%d/%m/%y %H:%M:%S',time.localtime())

if p: p.update(0.1, "Left")
maxleft  = mixerleft.get_max()
if p: p.update(0.5, "Right")
maxright = mixerright.get_max()

if p: p.update(0.9, "Attenuator estimation")
maxval   = max(maxleft, maxright)
maxvalth = audioutils.get_maxval( sampleswidth )

if maxval > maxvalth:
    attenuator = float(maxvalth)/maxval*0.95
else:
    attenuator = 1

if verbose > 0:
    p.update(1, "")
    del p
if verbose > 1:
    print "\nEnd getting factor at %s"%time.strftime('%d/%m/%y %H:%M:%S',time.localtime())

# what's for????
#attenuator = 1


#========================MIX============================#

if verbose > 0:
    p = TextProgress()
    p.set_new()
    p.set_header("Mixing channels")
    p.set_fraction(0)
    p.update(0,"")

if p: p.set_text("Left")
newchannelleft = mixerleft.mix(attenuator)
if p: p.set_fraction(0.5)
del mixerleft

if p: p.set_text("Right")
newchannelright = mixerright.mix(attenuator)
del mixerright

del settings

if verbose > 0:
    p.update(1, "")
    del p
if verbose > 1:
    print "\nEnd mixing channels at %s"%time.strftime('%d/%m/%y %H:%M:%S',time.localtime())

#========================SAVE THE RESULT============================#
p = None
if verbose > 0:
    p = TextProgress()
    p.set_new()
    p.set_header("Saving the output file")
    p.set_fraction(0)
    p.update(0,"")

audio_out = Audio()
audio_out.append_channel( newchannelleft )
audio_out.append_channel( newchannelright )

signals.save( args.o, audio_out )

if verbose > 0:
    p.update(1, "")

# ----------------------------------------------------------------------------

if verbose > 1:
    print "\nEnd process at %s", time.strftime('%d/%m/%y %H:%M:%S',time.localtime())

# ----------------------------------------------------------------------------
