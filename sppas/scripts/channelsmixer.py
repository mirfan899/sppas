from argparse import ArgumentParser
import os
import sys


PROGRAM = os.path.abspath(__file__)
WAVETOASTER = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ))
SRC = os.path.join(WAVETOASTER, "src" )
sys.path.append(SRC)

import audiodata
from audiodata.channelsmixer import ChannelsMixer
from audiodata.audio import AudioPCM

sys.path.remove(SRC)

parser = ArgumentParser(usage="%s -w input file -o output file [options]" % os.path.basename(PROGRAM), description="A script to mix channels from mono audio files in one channel")

parser.add_argument("-w", metavar="file", nargs='+', required=True,  help='Audio Input file name')
parser.add_argument("-o", metavar="file", required=True,  help='Audio Output file name')


# ----------------------------------------------------------------------------

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------


mixer = ChannelsMixer()

for inputFile in args.w:
    audio = audiodata.open(inputFile)
    idx = audio.extract_channel(0)
    mixer.append_channel(audio.get_channel(idx))

newchannel = mixer.mix()


# Save the converted channel
audio_out = AudioPCM()
audio_out.append_channel( newchannel )
audiodata.save( args.o, audio_out )

# ----------------------------------------------------------------------------