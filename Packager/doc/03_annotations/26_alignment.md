## Alignment

### Overview

Alignment, also called phonetic segmentation, is the process of aligning
speech with its corresponding transcription at the phone level.
The alignment problem consists in a time-matching between a given speech
unit along with a phonetic representation of the unit.

SPPAS is based on the Julius Speech Recognition Engine (SRE).
Speech Alignment also requires an Acoustic Model in order to align speech.
An acoustic model is a file that contains statistical representations of each
of the distinct sounds of one language. Each phoneme is represented by one
of these statistical representations.

Speech segmentation was evaluated for French: in average, automatic speech
segmentation is 95% of times within 40ms compared to the manual segmentation
and was tested on read speech and on conversational speech (Bigi 2014).

![SPPAS alignment output example](./etc/screenshots/alignment.png)

### Adapt Alignment

For Speech segmentation, the better Acoustic Model, the better results. In order
to get a better result, any user can append or replace the models included in
SPPAS in the "models" folder of the "resources" directory.
SPPAS only supports HTK-ASCII acoustic models, trained from 16 bits
16000 Hz WAVE files.
The models can be improved if they are re-trained with more data. So, any new
data is welcome (send an e-mail to the author).

### Perform Alignment with the GUI

The Alignment process takes as input one or two files that strictly match the
audio file name except for the extension and that "-phon" is appended for the
first one and "-tokens" for the optionnal second one. For example,
if the audio file name is "oriana1.wav", the expected input file name is
"oriana1-phon.xra" with phonetization and optionnally  "oriana1-tokens.xra"
with tokenization, if .xra is the default extension for annotations.

The speech segmentation process provides one file with name "-palign" appended
to its name, i.e. "oriana1-palign.xra" for the previous example.
This file includes one or two tiers:

* "PhonAlign" is the segmentation at the phone level;
* "TokensAlign" is the segmentation at the word level (if a file with tokenization was found).

![Alignment workflow](./etc/figures/alignworkflow.bmp)

The following options are available to configure Alignment:

* choose the speech segmentation system. It can be either: julius, hvite or basic
* perform basic alignment if the aligner failed, instead such intervals are empty.
* remove working directory will keep only alignment result: it will remove working files. Working directory includes one wav file per unit and a set of text files per unit.
* create the Activity tier will append another tier with activities as intervals, i.e. speech, silences, laughter, noises...
* create the PhnTokAlign will append anoter tier with intervals of the phonetization of each word.

To perform speech segmentation, click on the Alignment activation button, select
the language and click on the "Configure..." blue text to fix options.


### Perform Alignment with the CLI

`alignment.py` is the program to perform automatic speech segmentation of a
given file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: alignment.py -w file -i file -r file -o file [options]

optional arguments:
    -w file     Input wav file name
    -i file     Input file name with the phonetization
    -I file     Input file name with the tokenization
    -r file     Directory of the acoustic model of the language of the text
    -R file     Directory of the acoustic model of the mother language
                of the speaker
    -o file     Output file name with alignments
    -a name     Aligner name. One of: julius, hvite, basic (default: julius)
    --extend    Extend last phoneme/token to the wav duration
    --basic     Perform a basic alignment if error with the aligner
    --infersp   Add 'sp' at the end of each token and let the aligner
                to decide the relevance
    --noclean   Do not remove temporary data
    -h, --help  Show the help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example of use:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./sppas/bin/alignment.py
-r ./resources/models/models-eng
-w ./samples/samples-eng/oriana1.WAV
-i ./samples/samples-eng/oriana1-phon.xra
-I ./samples/samples-eng/oriana1-token.xra
-o ./samples/samples-eng/oriana1-palign.xra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
