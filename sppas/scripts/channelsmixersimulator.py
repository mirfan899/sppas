from argparse import ArgumentParser
import os
import sys


PROGRAM = os.path.abspath(__file__)
WAVETOASTER = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ))
SRC = os.path.join(WAVETOASTER, "src" )
sys.path.append(SRC)

import signals
from signals.channelsmixer import ChannelsMixer
from signals.audio import Audio

sys.path.remove(SRC)

parser = ArgumentParser(usage="%s -w input files" % os.path.basename(PROGRAM), description="A script to get the maximum value of a mix between mono audio files")

parser.add_argument("-w", metavar="file", nargs='+', required=True,  help='Audio Input file names')


# ----------------------------------------------------------------------------

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()
    
# ----------------------------------------------------------------------------


mixer = ChannelsMixer()

for inputFile in args.w:
    audio = signals.open(inputFile)
    idx = audio.extract_channel(0)
    mixer.append_channel(audio.get_channel(idx))
    
print mixer.get_max()

# ----------------------------------------------------------------------------