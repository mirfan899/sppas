## Text normalization

### Overview

In principle, any system that deals with unrestricted text need the text to
be normalized. Texts contain a variety of "non-standard" token types such as
digit sequences, words, acronyms and letter sequences in all capitals, mixed
case words, abbreviations, roman numerals, URL's and e-mail addresses...
Normalizing or rewriting such texts using ordinary words is then an important
issue. The main steps of the text normalization implemented in SPPAS
(Bigi 2011) are:

* Replace symbols by their written form, thanks to a "replacement" dictionary,
  located into the folder "repl" in the "resources" directory.
* Word segmentation based on the content of a lexicon.
* Convert numbers to their written form.
* Remove punctuation.
* Lower the text.


### Adapt Text normalization

Word segmentation of SPPAS is mainly based on the use of a lexicon.
If a segmentation is not as expected, it is up to the user to modify
the lexicon: Lexicons of all supported languages are all located in the folder
"vocab" of the "resources" directory. They are in the form of "one
word at a line" with [UTF-8 encoding](https://en.wikipedia.org/wiki/UTF-8) 
and ["LF" for newline](https://en.wikipedia.org/wiki/Newline).


### Support of a new language

Adding a new language in Text Normalization consists in the following steps:

1. Create a lexicon. Fix properly its encoding (utf-8), its newlines (LF), 
and fix the name and extension of the file as follow: 
    - language name with iso639-3 standard
    - extension ".vocab"
2. Put this lexicon in the `resources/vocab` folder
3. Create a replacement dictionary for that language (take a look on the ones of the other language!)
4. Optionally, the language can be added into the num2letter.py program 

That's it for most of the languages! If the language requires more steps,
simply write to the author to collaborate, find some funding, etc. like it
was already done for Cantonese (Bigi & Fung 2015) for example.


### Perform Text Normalization with the GUI

The SPPAS Text normalization system takes as input a file (or a list of files) 
for which the name strictly match the name of the audio file except the extension.
For example, if a file with name "oriana1.wav" is given, SPPAS will search for a
file with name "oriana1.xra" at a first stage if ".xra" is set as the default
extension, then it will search for other supported extensions until a file is
found.

This file must include a tier with an orthographic transcription.
At a first stage, SPPAS tries to find a tier with `transcription` as name.
If such a tier does not exist, the first tier that is matching
one of the following strings is used (case-insensitive search):

1. `trans`
2. `trs`
3. `ipu`
4. `ortho`
5. `toe`

Text normalization produces a file with "-token" appended to its name,
i.e. "oriana1-token.xra" for the previous example.
By default, this file is including only one tier with the resulting 
normalization and with name "Tokens". To get other versions of the 
normalized transcription, click on the "Configure" text then check 
the expected tiers. 

Read the "Introduction" of this chapter for a better understanding of the
difference between "standard" and "faked" results.

![Text normalization workflow](./etc/figures/tokworkflow.bmp)

To perform the text normalization process, click on the Text Normalization
activation button, select the language and click on the "Configure..." blue 
text to fix options.


### Perform Text Normalization with the CLI

`normalize.py` is the program to perform Text Normalization, i.e. the 
text normalization of a given file or a raw text.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: normalize.py -r vocab [options]

optional arguments:
    -r vocab         Vocabulary file name
    -i file          Input file name
    -o file          Output file name
    --delimiter char Use a delimiter character instead of a space for word delimiter.
    -h, --help       Show the help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following situations are possible:

1. no input is given: the input is `stdin` and the output is `stdout`
(if an output file name is given, it is ignored). Only the normalization 
with a faked orthography is printed.

2. an input and an output are given: the output file is created (or
erased if the file already exists) and the result of the process is
added to this file..


Example of use, using stdin/stdout:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ echo "The te(xt) to normalize 123." |\
  ./sppas/bin/normalize.py
  -r ./resources/vocab/eng.vocab
$ the te to normalize one_hundred_twenty-three
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In that case, the elision mentioned with the parenthesis is removed
and the number is converted to its written form. The character "_" is
used for compound words (it replaces the whitespace).

Example of use on a transcribed file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ ./sppas/bin/normalize.py -r ./resources/vocab/eng.vocab
  -i ./samples/samples-eng/oriana1.xra
  -o ./samples/samples-eng/oriana1-token.xra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
