# Phonetization

-----------------

## Overview

* Phonetization is also known as  grapheme-phoneme conversion
* Phonetization is the process of representing sounds with phonetic signs.
* SPPAS implements a dictionary based-solution which consists in storing a
maximum of phonological knowledge in a lexicon.
* Missing tokens are phonetized automatically:
    - a warning message is displayed

-----------------

### Pronunciation variants

* some words can correspond to several entries in the dictionary with various pronunciations
* these pronunciation variants are stored in the phonetization result. 
    - whitespace separate words, 
    - minus characters separate phones,
    - pipe characters separate phonetic variants of a word.
* For example, the transcription utterance:

    - Transcription: `The flight was 12 hours long.`
    - Tokenization:  `the flight was twelve hours long`
    - Phonetization: `D-@|D-V|D-i: f-l-aI-t w-A-z|w-V-z|w-@-z|w-O:-z t-w-E-l-v aU-3:r-z|aU-r-z l-O:-N`

-----------------

### Adapt Phonetization

* Phonetization is mainly based on the use of a dictionary.
* If a pronunciation is not as expected: 
    - edit the dictionary and make as many changes as wanted!
* Dictionaries to edit:
    - in the folder "dict" of the "resources" directory
    - "one word at a line"
    - second columns is brackets
    - use only known phonemes (see documentation for the list of each language)
    - UTF-8 encoding

-----------------

### Add a new language in Phonetization

* Create a pronunciation dictionary and:
    - add it in the folder "dict" of the "resources" directory
    - "one word at a line"
    - second columns is brackets
    - UTF-8 encoding

-----------------

## Perform Phonetization

* Required input file:
    - the normalized orthographic transcription, tokenized into IPUs
    - file name strictly match the name of the audio file with "-tokens" plus extension
    - include a tier with a name that contains one of the following strings:

        1. "tok"
        2. "trans"

-----------------

### Phonetization result

* output file:
    - Phonetization produces a file with "-phon" appended to its name
    - by default, one tier with name "Phonetization"

-----------------

### Perform Phonetization with the GUI

0. Select audio file(s)
1. Click on the "Annotate" button
2. Click on the Phonetization activation button
3. Select the language in the list
4. Click on the "Configure..." blue text to fix options
5. Click on "Perform annotation button"
6. Read the Procedure Outcome Report

-----------------

### Perform Phonetization with the CLI

* `phonetize.py` is the program to perform Phonetization, in "bin" folder of "sppas" directory.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./sppas/bin/phonetize.py
-d ./resources/dict/eng.dict
-i ./samples/samples-eng/oriana1-token.xra
-o ./samples/samples-eng/oriana1-phon.xra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-----------------

##

[Back to tutorials](tutorial.html)
