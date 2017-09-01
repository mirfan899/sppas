## Alignment

### Overview

Alignment, also called phonetic segmentation, is the process of aligning
speech with its corresponding transcription at the phone level.
The alignment problem consists in a time-matching between a given speech
unit along with a phonetic representation of the unit.

**SPPAS Alignment does not perform the segmentation itself. It is a wrapper
either for the `Julius` Speech Recognition Engine (SRE) or the `HVite` command
of HTK-Toolkit.**

Speech Alignment requires an Acoustic Model in order to align speech.
An acoustic model is a file that contains statistical representations of each
of the distinct sounds of one language. Each phoneme is represented by one
of these statistical representations.
The quality of the alignment result only depends on both this resource and 
on the aligner. From our past experiences, we got better results with Julius.

In addition, all acoustic models (except English, Japanese and Cantonese) 
include the following fillers:
- dummy: un-transcribed speech
- gb: garbage, for noises
- @@: laughter

They allow SPPAS to time-align automatically these phenomena whose can be 
very frequent in speech, like laugh items (Bigi and Bertrand 2015).
No other system is able to achieves this task!

![SPPAS alignment output example](./etc/screenshots/alignment.png)


### Adapt Alignment

The better Acoustic Model, the better alignment results. 
Any user can append or replace the acoustic models included in the "models" 
folder of the "resources" directory. Be aware that SPPAS only supports 
HTK-ASCII acoustic models, trained from 16 bits, 16000 Hz wave files.

The existing models can be improved if they are re-trained with more data.
To get a better alignment result, any new data is then welcome: send an 
e-mail to the author to share your recordings and transcripts.


### Support of a new language

The support of a new language in Alignment only consists in adding
a new acoustic model of the appropriate format, in the appropriate
directory, with the appropriate phone set.

The articulatory representations of phonemes are so similar across
languages that phonemes can be considered as units which are independent 
from the underlying language (Schultz et al. 2001). In SPPAS package, 
9 acoustic models of the same type - i.e. same HMMs definition and 
acoustic parameters, are already available so that the phoneme prototypes 
can be extracted and reused to create an initial model for a new language.

Any new model can also be trained by the author, as soon as enough data
is available. It is difficult to estimate exactly the amount
of data a given language requires. 
That is said, we can approximate the minimum as follow:

- 3 minutes altogether of various speakers, manually time-aligned at the phoneme level.
- 10 minutes altogether of various speakers, time-aligned at the ipus level with the enriched orthographic transcription.
- more data is good data.


### Perform Alignment with the GUI

The Alignment process takes as input one or two files that strictly match the
audio file name except for the extension and that "-phon" is appended for the
first one and "-token" for the optional second one. For example,
if the audio file name is "oriana1.wav", the expected input file name is
"oriana1-phon.xra" with phonetization and optionally  "oriana1-token.xra"
with text normalization, if .xra is the default extension for annotations.

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

To perform the annotation, click on the Alignment activation button, select
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
