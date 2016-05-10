from argparse import ArgumentParser
import os
import sys


PROGRAM = os.path.abspath(__file__)
WAVETOASTER = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ))
SRC = os.path.join(WAVETOASTER, "src" )
sys.path.append(SRC)

import audiodata
from audiodata.audio import Audio
from audiodata.channelfragmentextracter import ChannelFragmentExtracter

sys.path.remove(SRC)

parser = ArgumentParser(usage="%s -w input file -o output file [OPTIONS]" % os.path.basename(PROGRAM), description="A script to extract fragment from an audio file")

parser.add_argument("-w", metavar="file", required=True,  help='Audio Input file name')
parser.add_argument("-o", metavar="file", required=True,  help='Audio Output file name')
parser.add_argument("-bs", default=0, metavar="value", type=float, help='The position (in seconds) when begins the mix, don\'t use with -bf')
parser.add_argument("-es", default=0, metavar="value", type=float, help='The position (in seconds) when ends the mix, don\'t use with -ef')
parser.add_argument("-bf", default=0, metavar="value", type=float, help='The position (in number of frames) when begins the mix, don\'t use with -bs')
parser.add_argument("-ef", default=0, metavar="value", type=float, help='The position (in number of frames) when ends the mix, don\'t use with -es')

# ----------------------------------------------------------------------------

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

audio_out = Audio()
audio = audiodata.open(args.w)

if args.bf and args.bs:
    print "bf option and bs option can't be used at the same time !"
    sys.exit(1)

if args.ef and args.es:
    print "ef option and es option can't be used at the same time !"
    sys.exit(1)

if args.bf:
    begin = args.bf
elif args.bs:
    begin = args.bs*audio.get_framerate()
else:
    begin = 0
if args.ef:
    end = args.ef
elif args.es:
    end = args.es*audio.get_framerate()
else:
    end = 0

for i in xrange(audio.get_nchannels()):
    idx = audio.extract_channel(i)
    audio.rewind()
    channel = audio.get_channel(idx)
    extracter = ChannelFragmentExtracter(channel)
    audio_out.append_channel(extracter.extract_fragment(begin, end))

audiodata.save(args.o, audio_out)