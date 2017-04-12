# Tokenization

-----------------

## Overview

* Tokenization is also known as "Text Normalization".
* Tokenization is the process of segmenting a text into tokens. 
* SPPAS Tokenization implemented as a set of modules that are applied sequentially to the text corpora:

    1. Split (whitespace or characters)
    2. Replace symbols by their written form
    3. Segment into words
    4. Stick, i.e. concatenate strings into words
    5. Convert numbers to their written form
    6. Lower the text
    7. Remove punctuation

-----------------

### Tokenization of speech transcription

* Speech transcription includes speech phenomena like:
    - specific pronunciations: [example,eczap]
    - elisions: examp(le)
* Then two types of transcriptions can be automatically derived by the automatic tokenizer: 
    1. the “standard transcription” (a list of orthographic tokens/words);
    2. the “faked transcription” that is a specific transcription from which 
    the obtained phonetic tokens are used by the phonetization system.

-----------------

### Adapt Tokenization

* Tokenization is mainly based on the use of a lexicon.
* If a segmentation is not as expected: 
    - edit the lexicon and make as many changes as wanted!
* Lexicons to edit:
    - in the folder "vocab" of the "resources" directory
    - "one word at a line"
    - UTF-8 encoding

-----------------

### Add a new language in Tokenization

* Create a lexicon and:
    - add it in the folder "vocab" of the "resources" directory
    - "one word at a line"
    - UTF-8 encoding
    - ".vocab" extension
* Create a replacement list and:
    - add it in the folder "vocab" of the "resources" directory
    - 1st column: symbol; 2nd column: token
    - UTF-8 encoding
    - ".repl" extension
* Optionally: Add the number to letter conversion in "num2letter.py" source file

-----------------

## Perform Tokenization

* Required input file:
    - the orthographic transcription, transcribed into IPUs
    - file name strictly match the name of the audio file except the extension
    - include a tier with a name that contains one of the following strings:
    
        1. `trans`
        2. `trs`
        3. `ipu`
        4. `ortho`
        5. `toe`

-----------------

### Tokenization result

* output file:
    - Tokenization produces a file with "-tokens" appended to its name
    - by default, one tier with name "Tokenization"
    - in case of EOT, two tiers:
        - "Tokens-std": the text normalization of the standard transcription,
        - "Tokens-faked": the text normalization of the faked transcription.

-----------------

### Perform Tokenization with the GUI

0. Select audio file(s)
1. Click on the "Annotate" button
2. Click on the Tokenization activation button
3. Select the language in the list
4. Click on the "Configure..." blue text to fix options
5. Click on "Perform annotation button"
6. Read the Procedure Outcome Report

-----------------

### Perform Tokenization with the CLI

* `tokenize.py` is the program to perform Tokenization, in "bin" folder of "sppas" directory.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ ./sppas/bin/tokenize.py -r ./resources/vocab/eng.vocab
  -i ./samples/samples-eng/oriana1.xra
  -o ./samples/samples-eng/oriana1-token.xra
  --std
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-----------------

##

[Back to tutorials](tutorial.html)

