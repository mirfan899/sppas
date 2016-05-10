from argparse import ArgumentParser
import os
import sys
import time

PROGRAM = os.path.abspath(__file__)
WAVETOASTER = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ))
SRC = os.path.join(WAVETOASTER, "src" )
sys.path.append(SRC)

import audiodata
from audiodata.channelformatter import ChannelFormatter
from audiodata.audio import Audio

sys.path.remove(SRC)

parser = ArgumentParser(usage="%s -w input file -o output file [options]" % os.path.basename(PROGRAM), description="A script to reformat audio files")

parser.add_argument("-w", metavar="file", required=True,  help='Audio Input file name')
parser.add_argument("-o", metavar="file", required=True,  help='Audio Output file name')
parser.add_argument("-s", metavar="value", type=int, help='Sample width for the output file. Possible values are 1,2,4')
parser.add_argument("-c", metavar="value", default=1, type=int, help='the channel to extract (default: 1)')
parser.add_argument("-r", metavar="value", type=int, help='The framerate expected of the output audio file')
parser.add_argument("-m", metavar="value", type=int, help='Multiply the frames of the channel by the factor')
parser.add_argument("-b", metavar="value", type=int, help='Bias the frames of the channel by the factor')


# ----------------------------------------------------------------------------

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

audio = audiodata.open(args.w)

# Get the expected channel
idx = audio.extract_channel(args.c-1)

# Do the job (do not modify the initial channel).
formatter = ChannelFormatter( audio.get_channel(idx) )

if args.r:
    formatter.set_framerate(args.r)
else:
    formatter.set_framerate(audio.get_framerate())


if args.b:
    if not args.b in [1,2,4]:
        print "Wrong bitrate value"
        sys.exit(1)
    formatter.set_sampwidth(args.b)
else:
    formatter.set_sampwidth(audio.get_sampwidth())

formatter.convert()

# no more need of input data, can close
audio.close()

if args.m:
    formatter.mul(args.m)

if args.b:
    formatter.bias(args.b)

# Save the converted channel
audio_out = Audio()
audio_out.append_channel( formatter.channel )
audiodata.save( args.o, audio_out )

# ----------------------------------------------------------------------------