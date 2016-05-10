from argparse import ArgumentParser
import os
import sys


PROGRAM = os.path.abspath(__file__)
WAVETOASTER = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ))
SRC = os.path.join(WAVETOASTER, "src" )
sys.path.append(SRC)

import audiodata
from audiodata.audio import AudioPCM

sys.path.remove(SRC)

parser = ArgumentParser(usage="%s -w input file -o output file -c channel" % os.path.basename(PROGRAM), description="A script to extract a channel from an audio file")

parser.add_argument("-w", metavar="file", required=True,  help='Audio Input file name')
parser.add_argument("-o", metavar="file", required=True,  help='Audio Output file name')
parser.add_argument("-c", metavar="value", type=int, required=True, help='Numero of the channel to extract')


# ----------------------------------------------------------------------------

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

audio = audiodata.open(args.w)

if args.c == 0 or args.c > audio.get_nchannels():
    print "Wrong channel value (must be > 0 and < number of channels)"
    sys.exit(1)

idx = audio.extract_channel(args.c-1)



# Save the converted channel
audio_out = AudioPCM()
audio_out.append_channel( audio.get_channel(idx) )
audiodata.save( args.o, audio_out )

# ----------------------------------------------------------------------------