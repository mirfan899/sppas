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
(tested on read speech and on conversational speech). 
Details about these results are available in the slides of the 
following reference:

>*Brigitte Bigi* (2014).
>**Automatic Speech Segmentation of French: Corpus Adaptation**.
>2nd Asian Pacific Corpus Linguistics Conference, p. 32, Hong Kong. 

![Alignment workflow](./etc/figures/alignworkflow.bmp)

The SPPAS aligner takes as input the phonetization and optionally the 
tokenization.
The name of the phonetization tier must contains the string "phon".
The first tier that matches is used (case insensitive search). 

The annotation provides one annotated file with 3 tiers:

* "PhonAlign", is the segmentation at the phone level;
* "PhnTokAlign"  is the segmentation at the word level, with phonemes as labels; 
* "TokensAlign" is the segmentation at the word level.

![SPPAS alignment output example](./etc/screenshots/alignment.png)

The following options are available to configure alignment:

* Expend option: If expend is checked, SPPAS will expend the last phoneme and the last token of each unit to the unit duration.
* Extend option: If extend is checked, SPPAS will extend the last phoneme and the last token to the wav duration, otherwise SPPAS adds a silence.
* Remove temporary files: keep only alignment result and remove intermediary files (they consists in one wav file per unit and a set of text files per unit).
* Speech segmentation system can be either: julius, hvite or basic
* Guess short pauses after each token

