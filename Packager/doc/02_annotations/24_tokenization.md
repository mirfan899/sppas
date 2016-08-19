## Tokenization

Tokenization is also known as "Text Normalization" the process of segmenting a
text into tokens.
In principle, any system that deals with unrestricted text need the text to
be normalized. Texts contain a variety of "non-standard" token types such as
digit sequences, words, acronyms and letter sequences in all capitals, mixed
case words, abbreviations, roman numerals, URL's and e-mail addresses...
Normalizing or rewriting such texts using ordinary words is then an important
issue. The main steps of the text normalization implemented in SPPAS 
(Bigi 2011) are:

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

![Text normalization workflow](./etc/figures/tokworkflow.bmp)

The SPPAS Tokenization system takes as input a file including a tier
with the orthographic transcription. 
At a first stage, SPPAS tries to find a tier with `transcription` as name.
If such a tier does not exist, SPPAS tries to find a tier that contains
one of the following strings:

1. trans
2. trs
3. ipu
4. ortho
5. toe

The first tier that matches is used (case insensitive search).

By default, Tokenization produces a file including only one tier with the
tokens. 
In case of an Enriched Orthographic Transcription, to get both faked 
and standard tokenized tiers, check the corresponding option. Then, 2
tiers will be created:

- Tokens-std: the text normalization of the standard transcription,
- Tokens-faked: the text normalization of the faked transcription.

Read the "Introduction" of this chapter for a better understanding of the 
difference between "standard" and "faked" transcriptions.
