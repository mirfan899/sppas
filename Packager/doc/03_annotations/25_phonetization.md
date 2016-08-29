## Phonetization

### Overview

Phonetization, also called grapheme-phoneme conversion, is the process of
representing sounds with phonetic signs. However, converting from written
text into actual sounds, for any language, cause several problems that have
their origins in the relative lack of correspondence between the spelling
of the lexical items and their sound contents.

SPPAS implements a dictionary based-solution which consists in storing a
maximum of phonological knowledge in a lexicon. In this sense, this approach
is language-independent. SPPAS phonetization process is the equivalent of a
sequence of dictionary look-ups.
It is then assumed that all words of the speech transcription are mentioned
in the pronunciation dictionary.

Actually, some words can correspond to several entries in the dictionary
with various pronunciations. These pronunciation variants are stored in the
phonetization result. By convention, spaces separate words, minus separate
phones and pipe character separate phonetic variants of a word.
For example, the transcription utterance:

* Transcription: `The flight was 12 hours long.`
* Tokenization:  `the flight was twelve hours long`
* Phonetization: `D-@|D-V|D-i: f-l-aI-t w-A-z|w-V-z|w-@-z|w-O:-z t-w-E-l-v aU-3:r-z|aU-r-z l-O:-N`

Many of the other systems assume that all words of the speech transcription
are mentioned in the pronunciation dictionary. On the contrary, SPPAS
includes a language-independent algorithm which is able to phonetize unknown
words of any language as long as a (minimum) dictionary is available (Bigi 2013)!
If such case occurs during the phonetization process, a WARNING indicates
it in the Procedure Outcome Report.

Since the phonetization is only based on the use of a pronunciation dictionary,
the quality of such a phonetization only depends on this resource.

### Adapt Phonetization

If a pronunciation is not as expected, it is up to the user to change it in
the dictionary. All dictionaries are located in the folder "dict" of
the "resources" directory.

SPPAS uses the HTK ASCII format for dictionaries. As example, below is a piece
of the `eng.dict` file:

        THE             [THE]           D @
        THE(2)          [THE]           D V
        THE(3)          [THE]           D i:
        THEA            [THEA]          T i: @
        THEALL          [THEALL]        T i: l
        THEANO          [THEANO]        T i: n @U
        THEATER         [THEATER]       T i: @ 4 3:r
        THEATER'S       [THEATER'S]     T i: @ 4 3:r z

The first column indicates the word, followed by the variant number (except for
the first one). The second column indicates the word between brackets; however
brackets can also be empty. The last columns are the succession of phones,
separated by a whitespace.

SPPAS dictionaries are mainly based on X-SAMPA international standard for
phoneme encoding. See the chapter "Resources" of this documentation to know
the list of accepted phones for a given language. This list can't be extended
nor modified while using SPPAS.
However, it can be improved from one version to the other one thanks to user
comments (to be sent to the author).

### Perform Phonetization with the GUI

The Phonetization process takes as input a file that strictly match the audio
file name except for the extension and that "-tokens" is appended. For example,
if the audio file name is "oriana1.wav", the expected input file name is
"oriana1-tokens.xra" if .xra is the default extension for annotations.
This file must include a **normalized** orthographic transcription.
The name of such tier must contains one of the following strings:

1. "tok"
2. "trans"

The first tier that matches one of these requirements is used
(this match is case insensitive).

Phonetization produces a file with "-phon" appended to its name,
i.e. "oriana1-phon.xra" for the previous example.
This file is including only one tier with the resulting phonetization and with
name "Phonetization".

![Phonetization workflow](./etc/figures/phonworkflow.bmp)

To perform the grapheme-to-phoneme convertion, click on the Phonetization
activation button, select the language and click on the "Configure..."
blue text to fix options.


### Perform Phonetization with the CLI

`phonetize.py` is the program performs Phonetization, i.e. grapheme to
phoneme conversion on a given file.

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
