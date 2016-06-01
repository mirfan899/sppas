## Programs to perform an automatic annotation

This chapter describes how to use the automatic annotations of SPPAS with a
Command-Line Interface (CLI). It describes all available command and how to 
use them. However, for scripts that execute an automatic annotation, refer 
to the chapter "Automatic Annotation" to understand exactly each option!

Generally, data are given to the CLI with the following arguments:

- a resources is given with "-r" option;
- an input audio file is given with "-w" option;
- an input annotated file is given with "-i" option;
- the output is specified with "-o".


### annotation.py

This program performs automatic annotations on a given file or on all files
of a directory. It strictly corresponds to the button `Annotate` of the GUI.
All annotations are pre-configured: no specific option can be specified.
This configuration is fixed in the source code packages, via a file with name
`sppas.conf` for each annotation.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: annotation.py -w file|folder [options]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
optional arguments:
   -h, --help      show this help message and exit
   -w file|folder  Input wav file name, or folder
   -l lang         Input language, using iso639-3 code
   -e extension    Output extension. One of: xra, textgrid, eaf, csv, ...
   --momel         Activate Momel and INTSINT
   --ipu           Activate IPUs Segmentation
   --tok           Activate Tokenization
   --phon          Activate Phonetization
   --align         Activate Alignment
   --syll          Activate Syllabification
   --rep           Activate Repetitions
   --all           Activate ALL automatic annotations
   --merge         Create a merged TextGrid file, if more than two automatic
                   annotations (this is the default).
   --nomerge       Do not create a merged TextGrid file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Examples of use:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./sppas/bin/annotation.py ./samples/samples-eng
                    -l eng
                    --ipu --tok --phon --align
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A progress bar is displayed for each annotation. At the end of the process,
a message indicates the name of the procedure outcome report file, which
is `./samples/samples-eng.log` in our example. This file can be opened with
any text editor (as Notepad++, vim, TextEdit, ...).

![CLI: annotation.py output example](./etc/screenshots/CLI-example.png)



### wavsplit.py

This program performs the IPU-segmentation, i.e. silence/speech segmentation.
When this program is used from an audio speech sound and eventually a
transcription, it consists in aligning macro-units of a document with the
corresponding sound.

>Notice that all time values are indicated in seconds.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: wavsplit.py -w file [options]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Generic options:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    -w file		    audio input file name
    -d delta shift	Add this time value to each start
                    bound of the IPUs
    -D delta shift	Add this time value to each end
                    bound of the IPUs
    -h, --help      show the help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Options that can be fixed for the Speech/Silence segmentation:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    -r float 	Window size to estimate rms, in seconds
                (default value is: 0.010)
    -m value 	Drop speech shorter than m seconds long
                (default value is: 0.300)
    -s value 	Drop silences shorter than s seconds long
                (default value is: 0.200)
    -v value 	Assume that a rms lower than v is a silence
                (default value is: 0 which means to auto-adjust)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Options that can be fixed for the Speech/Silence segmentation with
a given orthographic transcription. It must be choose one of -t or -n options:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    -t file 	Input transcription file (default: None)
    -n value 	Input transcription tier number (default: None)
    -N 		    Adjust the volume cap until it splits
                into nb tracks (default: 0=automatic)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Output options:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    -o dir		Output directory name       (default: None)
    -e ext		Output tracks extension     (default: txt)
    -p file		File with the segmentation  (default: None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Examples of use to get each IPU in a wav file and its corresponding textgrid:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./sppas/bin/wavsplit.py -w ./samples/samples-eng/oriana1.WAV
-d 0.02
-t ./samples/samples-eng/oriana1.txt
-p ./samples/samples-eng/oriana1.xra

./sppas/bin/wavsplit.py -w ./samples/samples-eng/oriana1.WAV
-t ./samples/samples-eng/oriana1.xra
-o ./samples/samples-eng/oriana1
-e textgrid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### tokenize.py

This program performs Tokenization, i.e. the text normalization of a given 
file or a raw text.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: tokenize.py -r vocab [options]

optional arguments:
    -r vocab         Vocabulary file name
    -i file          Input file name
    -o file          Output file name
    --delimiter char Use a delimiter character instead of a space for word delimiter.
    -h, --help       Show the help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following situations are possible:

1. no input is given: the input is `stdin` and the output is `stdout`
(if an output file name is given, it is ignored). In case of Enriched
Orthographic Transcription, only the faked tokenization is printed.

2. an input is given, but no output: the result of the tokenization is
added to the input file.

3. an input and an output are given: the output file is created (or
erased if the file already exists) and the result of the tokenization is
added to this file..


Example of use, using stdin/stdout:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ echo "The te(xt) to normalize 123." |\
  ./sppas/bin/tokenize.py
  -r ./resources/vocab/eng.vocab
$ the te to normalize one_hundred_twenty-three
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In that case, the elision mentionned with the parenthesis is removed
and the number is converted to its written form. The character "_" is
used for compound words (it replaces the whitespace).

Example of use on a transcribed file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ ./sppas/bin/tokenize.py -r ./resources/vocab/eng.vocab
  -i ./samples/samples-eng/oriana1.xra
  -o ./samples/samples-eng/oriana1-token.xra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



### phonetize.py

This program performs Phonetization, i.e. grapheme to phoneme conversion on a
given file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: phonetize.py -r dict [options]

optional arguments:
    -r dict      Pronunciation dictionary file name (HTK-ASCII format)
    -m map       Pronunciation mapping table
    -i file      Input file name
    -o file      Output file name
    --nounk      Disable unknown word phonetization
    -h, --help   Show the help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examples of use:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ echo "the te totu" |\
 ./sppas/bin/phonetize.py 
    -r ./resources/dict/eng.dict 
    --nounk
$ D-@|D-V|D-i: t-i: UNK
$
$ echo "the te totu" |\
 ./sppas/bin/phonetize.py -r ./resources/dict/eng.dict 
$ D-@|D-V|D-i: t-i: t-u-t-u|t-i-t-u|t-A-t-u|t-@-t-u
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If we suppose that the previous text was read by a French native speaker, the
previous example can be phonetized as:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ echo "the te totu" |\
 ./sppas/bin/phonetize.py 
     -r ./resources/dict/eng.dict 
     -m ./resources/dict/eng-fra.map 
$ D-@|z-@|v-@|z-9|D-V|v-9|v-V|D-9|z-V|D-i:|z-i|v-i|D-i|v-i:|z-i: 
  t-i:|t-i 
  t-u-t-u|t-i-t-u|t-A-t-u|t-@-t-u
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example of use on a tokenized file:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./sppas/bin/phonetize.py
-d ./resources/dict/eng.dict
-i ./samples/samples-eng/oriana1-token.xra
-o ./samples/samples-eng/oriana1-phon.xra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### alignment.py

This program performs automatic speech segmentation of a given file.

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


### syllabify.py

This program performs automatic syllabification of a given file with 
time-aligned phones.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: syllabify.py -r config [options]

optional arguments:
    -r config   Rules configuration file name
    -i file     Input file name (time-aligned phonemes)
    -o file     Output file name
    -e file     Reference file name to syllabify between intervals
    -t string   Reference tier name to syllabify between intervals
    --nophn     Disable the output of the result that does not use the reference  tier
    -h, --help   Show the help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### repetition.py

This program performs automatic detection of self-repetitions or
other-repetitions if a second speaker is given.

It can be language-dependent (better results) or language-independent.

If an input is given, but no output: the result is appended to the input file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: repetition.py -i file [options]

optional arguments:
  -h, --help  show this help message and exit
  -i file     Input file name with time-aligned tokens of the self-speaker
  -r folder   Directory with resources
  -l lang     Language code in iso639-3
  -I file     Input file name with time-aligned tokens of the echoing-speaker
              (if ORs)
  -o file     Output file name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Momel and INTSINT

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: momel-intsint.py [options] -i file

optional arguments:
  -i file            Input file name (extension: .hz or .PitchTier)
  -o file            Output file name (default: stdout)
  --win1 WIN1        Target window length (default: 30)
  --lo LO            f0 threshold (default: 50)
  --hi HI            f0 ceiling (default: 600)
  --maxerr MAXERR    Maximum error (default: 1.04)
  --win2 WIN2        Reduct window length (default: 20)
  --mind MIND        Minimal distance (default: 5)
  --minr MINR        Minimal frequency ratio (default: 0.05)
  --non-elim-glitch
  -h, --help         Show the help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

