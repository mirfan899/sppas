## Alignment

Alignment, also called phonetic segmentation, is the process of aligning 
speech with its corresponding transcription at the phone level. 
The alignment problem consists in a time-matching between a given speech 
unit along with a phonetic representation of the unit. 

SPPAS is based on the Julius Speech Recognition Engine (SRE). 
Speech Alignment also requires an Acoustic Model in order to align speech. 
An acoustic model is a file that contains statistical representations of each
of the distinct sounds of one language. Each phoneme is represented by one 
of these statistical representations. 
SPPAS is working with HTK-ASCII acoustic models, trained from 16 bits, 
16000 Hz wav files. 

Speech segmentation was evaluated for French: in average, automatic speech 
segmentation is 95% of times within 40ms compared to the manual segmentation
and was tested on read speech and on conversational speech (Bigi 2014). 
Details about these results are available in the slides of the 
following reference:

![Alignment workflow](./etc/figures/alignworkflow.bmp)

The SPPAS aligner takes as input the phonetization and optionally the 
tokenization.
The name of the phonetization tier must contains the string "phon".
The first tier that matches is used (case insensitive search). 

The annotation provides one annotated file with 2 tiers:

* "PhonAlign", is the segmentation at the phone level;
* "TokensAlign" is the segmentation at the word level.

![SPPAS alignment output example](./etc/screenshots/alignment.png)

The following options are available to configure alignment:

* choose the speech segmentation system. It can be either: julius, hvite or basic
* perform basic alignment if the aligner failed, instead such intervals are empty.
* remove working directory will keep only alignment result: it will remove working files. Working directory includes one wav file per unit and a set of text files per unit.
* create the Activity tier will append another tier with activities as intervals, i.e. speech, silences, laughter, noises...
* create the PhnTokAlign will append anoter tier with intervals of the phonetization of each word.


### Perform Alignment with the GUI

Click on the Alignment activation button, select the language and click 
on the "Configure..." blue text to fix options.


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
