from argparse import ArgumentParser
import os
import sys


PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ) )
sys.path.append(SPPAS)

import audiodata
from audiodata.channelsmixer import ChannelsMixer
from audiodata.audio import Audio


parser = ArgumentParser(usage="%s -w input file -o output file [options]" % os.path.basename(PROGRAM), description="A script to mix all channels from multi audio files in one channel")

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
    for i in xrange(audio.get_nchannels()):
        idx = audio.extract_channel(i)
        audio.rewind()
        mixer.append_channel(audio.get_channel(idx))

newchannel = mixer.mix()


# Save the converted channel
audio_out = Audio()
audio_out.append_channel( newchannel )
audiodata.save( args.o, audio_out )

# ----------------------------------------------------------------------------