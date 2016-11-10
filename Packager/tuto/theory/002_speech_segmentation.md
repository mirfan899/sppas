# Phonemes and words segmentation

-------------------------------

## Definition

* the process of taking the orthographic transcription text of an audio 
   speech segment, like *IPUs*, and determining where particular phonemes/words
   occur in this speech segment.

*IPUs* = Inter-Pausal Units

-------------------------------

## Data preparation

* Audio file with the following recommended conditions:
    - one file = one speaker
    - good recording quality (anechoic chamber)
    - 16000Hz, 16bits
* Orthographic transcription:
    - follow the convention of the software
    - enriched with: filled pauses; short pauses; truncated words; repeats; noises and laugh items.

-------------------------------

### Data preparation: example

![An IPU of "Corpus of Interactional Data"](./etc/screenshots/CM-extract-toe.png)

![](./etc/media/CM-extract-toe.wav)

-------------------------------

## Expected result

* Time-aligned phonemes and tokens and events like noises or laughter

![](./etc/screenshots/CM-extract-palign.png)

-------------------------------

## Phonemes and words segmentation: my approach

1. tokenization 
    - text normalization
2. phonetization 
    - grapheme to phoneme conversion
3. alignment 
    - speech segmentation

> All three tasks are fully-automatic, but each annotation output can be
   manually checked if desired.

-------------------------------

### Tokenization

* Tokenization is also known as "Text Normalization".
* Tokenization is the process of segmenting a text into tokens. 
* In principle, any system that deals with unrestricted text need the text to 
be normalized.
* Automatic text normalization is mostly dedicated to written text, in the NLP community
    - Text normalization development is commonly carried out specifically for 
   each language and/or task even if this work is laborious and time consuming. 
   Actually, for many languages there has not been any concerted effort 
   directed towards text normalization.

-----------------

### Tokenization: my approach

* I proposed a generic approach:
    - a text normalization method as language and task independent as possible. 
    - This enables adding new languages quickly when compared to the development of such tools from scratch.
* This method is implemented as a set of modules that are applied sequentially to the text corpora.
* The portability to a new language consists of:
    - inheriting all language independent modules;
    - (rapid) adaptation of other language dependent modules.

-----------------

### Tokenization main steps

1. Split:
    - use whitespace or characters to split the utterance into separated strings
2. Replace symbols by their written form:
    - based on a lexicon
        - ° is replaced by degrees (English), degrés (French), grados (Spanish), gradi (Italian), mức độ (Vietnamese), 度 (Chinese), du (Chinese pinyin and Taiwanese)
        - ² is replaced by square (English), carré (French), quadrados (Spanish), quadrato (Italian), bình phương (Vietnamese), 平方 (Chinese), ping fang (Chinese pinyin)

-----------------

### Tokenization main steps (continued)

3. Segment into words:
    - fixes a set of rules to segment strings including punctuation marks
    - based on a lexicon and rules
        - aujourd'hui, c'est-à-dire
        - porte-monnaie, cet homme-là, voulez-vous
        - poudre d'escampette, trompe-l'oeil, rock'n roll

-----------------

### Tokenization main steps

4. Stick, i.e. concatenate strings into words
    - based on a dictionary with an optimization criteria: a longest matching
        - English: once_upon_a_time, game_over
        - French: pomme_de_terre, au_fur_et_à_mesure, tel_que
        - Chinese: 登记簿
5. Convert numbers to their written form
    - 123
        - cent-vingt-trois (French), one-hundred-twenty-three (English), ciento-veintitres (Spanish)
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

### Tokenization of speech transcription: example

![](./etc/media/CM-extract-toe.wav)

* Transcription: 
    - mais attendez et je mes fixations s(ont) pas bien réglées [c',z] est en fait c'est m- + ma chaussure qu(i) était partie

* Standard tokenization:
    - mais attendez et je mes fixations sont pas bien réglées c' est en_fait c'est ma chaussure qui était partie

* Faked tokenization:
    - mais attendez et je mes fixations s pas bien réglées z est en_fait c'est m- + ma chaussure qu était partie

------------------

### Tokenization: current languages

- French:  347k words
- English: 121k words
- Italian: 389k words
- Spanish: 22k words
- Catalan: 93k words
- Portuguese: 41k words
- Polish: 576k words
- Japanese: 18k words
- Mandarin Chinese: 110k words
- Cantonese: 46k words
- Korean: 33k words
- Min nan: 1k syllables in pinyin

> The better lexicon, the better automatic tokenization.

------------------

### Tokenization: Adding a new language

1. add lexicons
2. add the num2letter module

Example:

    Roxana Fung, Brigitte Bigi (2015).
    Automatic word segmentation for spoken Cantonese.
    In Oriental COCOSDA and Conference on Asian Spoken Language Research and Evaluation,
    pp. 196–201.

------------------

### Tokenization: reference

    Brigitte Bigi (2014). 
    A Multilingual Text Normalization Approach. 
    Human Language Technologies Challenges for Computer Science and Linguistics. 
    LNAI 8387, Springer, Heidelberg. ISBN: 978-3-319-14120-6. Pages 515-526.

![](./etc/screenshots/tokenization_paper.png)

------------------

## Phonetization

* Phonetization is also known as  grapheme-phoneme conversion
* Phonetization is the process of representing sounds with phonetic signs.
* Phonetic transcription of text is an indispensable component of 
    text-to-speech (TTS) systems and is used in acoustic modeling 
    for automatic speech recognition (ASR) and other natural language 
    processing applications. 

> Converting from written text into actual sounds, for any language, cause 
    several problems that have their origins in the relative lack of 
    correspondence between the spelling of the lexical items and their sound 
    contents.

-----------------

### Phonetization: my approach

* I proposed a generic approach:
    - consists in storing a maximum of phonological knowledge in a lexicon. 
    - In this sense, this approach is language-independent. 
* The phonetization process is the equivalent of a sequence of dictionary look-ups.

-----------------

### Phonetization: dictionary

* An important step is to build the pronunciation dictionary, where each word 
  in the vocabulary is expanded into its constituent phones, including pronunciation variants.

![](./etc/screenshots/dict-eng-extract.png)

-----------------

### Phonetization of normalized speech transcription

* I proposed a language-independent algorithm to phonetize unknown words
    - given enough examples (in the dictionary) it should be possible to predict the pronunciation of unseen words purely by analogy.

* Example with the unknown word "pac-aix":
    - English: p-{-k-aI-k-s|p-{-k-eI-aI-k-s|p-{-k-aI-E-k-s|p-{-k-eI-aI-E-k-s
    - French: p-a-k-E-k-s
    - Mandarin Chinese: p_h-a-a-i

-----------------

### Phonetization: example

* Tokenization:
    - mais attendez je

* Phonetization:
    - m-E-z|m-e|m-E|m-e-z|m a-t-a\~-d-e|a-t-a\~-d-e-z e|E Z|Z-eu|S

------------------

### Phonetization: current languages

- French:  652k entries
- English: 121k entries
- Italian: 590k entries
- Spanish: 24k entries
- Catalan: 94k entries
- Portuguese: 43k entries
- Polish: 300k entries
- Japanese: 20k entries
- Mandarin Chinese: 114k entries
- Cantonese: 59k entries
- Korean: 128 entries (!) is under construction
- Min nan: 1k entries

> The better dictionary, the better automatic phonetization.

-----------------

### Phonetization: reference

    Brigitte Bigi (2016).
    A phonetization approach for the forced-alignment task in SPPAS.
    Human Language Technologies Challenges for Computer Science and Linguistics. 
    LNAI 9561, Springer, Heidelberg. 

![](./etc/screenshots/phonetization_paper.png)

-----------------

## Alignment

* Alignment is also called phonetic segmentation
* The alignment problem consists in a time-matching between a given speech 
unit along with a phonetic representation of the unit. 
* Many freely available tool boxes, i.e. Speech Recognition Engines that can perform Speech Segmentation
    - HTK - Hidden Markov Model Toolkit
    - CMU Sphinx
    - Open Source Large Vocabulary CSR Engine Julius
    - ...

------------------

### Alignment

* Algorithms are language independent
* An acoustic model must be created
    - training procedure
    - based on examples
* "more data is good data"...
* Training a model:
    - requires audio files
    - requires orthographic transcription
    - requires IPUs/utterrances segmentation

------------------

### Alignment: current languages

- French
- English (from voxforge.org)
- Italian
- Spanish
- Catalan is under consctruction
- Polish
- Japanese (from Julius software)
- Mandarin Chinese
- Cantonese (from University of Hong Kong)
- Korean is under construction
- Min nan

-----------------

### Alignment: results of French

* In average, automatic speech segmentation is 95% of times within 40ms 
compared to the manual segmentation (SPPAS 1.5, Sept. 2014)

![Results on vowels of French conversational speech](./etc/screenshots/vowels-start-cid.png)
![Results on vowels of French read speech](./etc/screenshots/vowels-start-read.png)

-----------------

### Alignment: references

    Brigitte Bigi (2012). 
    The SPPAS participation to the Forced-Alignment task of Evalita 2011. 
    B. Magnini et al. (Eds.): EVALITA 2012, LNAI 7689, pp. 312-321. Springer, Heidelberg.

    Brigitte Bigi (2014).
    The SPPAS participation to Evalita 2014.
    In Proceedings of the First Italian Conference on Computational Linguistics CLiC-it 2014 
    and the Fourth International Workshop EVALITA 2014, Pisa, Italy.

    Brigitte Bigi (2014).
    Automatic Speech Segmentation of French: Corpus Adaptation.
    In 2nd Asian Pacific Corpus Linguistics Conference, pp. 32, Hong Kong.

-------------------------------

##

[Back to tutorials](tutorial.html)
