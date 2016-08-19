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
