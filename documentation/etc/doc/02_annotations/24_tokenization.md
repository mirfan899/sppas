## Tokenization

Tokenization is also known as "Text Normalization" the process of segmenting a
text into tokens. 
In principle, any system that deals with unrestricted text need the text to 
be normalized. Texts contain a variety of "non-standard" token types such as
digit sequences, words, acronyms and letter sequences in all capitals, mixed
case words, abbreviations, roman numerals, URL's and e-mail addresses... 
Normalizing or rewriting such texts using ordinary words is then an important
issue. The main steps of the text normalization proposed in SPPAS are:

* Remove punctuation;
* Lower the text;
* Convert numbers to their written form;
* Replace symbols by their written form, thanks to a "replacement" dictionary,
  located into the sub-directory "repl" in the "resources" directory. Do not
  hesitate to add new replacements in this dictionary.
* Word segmentation based on the content of a lexicon. If the
  result is not corresponding to your expectations, fill free to
  modify the lexicon, located in the "vocab" sub-directory of the "resources"
  directory. The lexicon contains one word per line.

For more details, see the following reference:

> **Brigitte Bigi (2011).**
> *A Multilingual Text Normalization Approach.*
> 2nd Less-Resourced Languages workshop, 5th Language  Technology Conference, Poznàn (Poland).

![Text normalization workflow](./etc/figures/tokworkflow.bmp)

The SPPAS Tokenization system takes as input a file including a tier 
with the orthographic transcription. The name of this tier must contains
one of the following strings:

- trs
- trans
- ipu
- ortho
- toe

The first tier that matches is used (case insensitive search).

By default, it produces a file including only one tier with the
tokens. To get both transcription tiers faked and standard,
check such option!

- Tokens-std: the text normalization of the standard transcription,
- Tokens-faked: the text normalization of the faked transcription.

Read the "Introduction" of this chapter to understand the difference
between "standard" and "faked" transcriptions.
