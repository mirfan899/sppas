% SPPAS for dummies
% Brigitte Bigi
% Use the left/right arrow keys to show slides


## Last update: January 2016

-![](./etc/img/for-dummies.jpg)



# Introduction



## Overview

* SPPAS is a scientific computer software package written and maintained
by Brigitte Bigi of the Laboratoire Parole et Langage, in Aix-en-Provence,
France.

* Operating systems:

    -![](./etc/logos/systemes.jpg)

* GNU Public License, version 3


## Download, install and update

* Web site: <http://sldr.org/sldr000800/preview/>

    1. Follow *carefully* instructions of the installation page
    2. Download the last package
    3. Unzip on your computer

* Update SPPAS regularly:

    1. Put the old package into the Trash
    2. Download and unpack the new one



# Main and IMPORTANT recommendations


## Speech files: recommendations

* only `wav`, `aiff` and `au` files

* channels: 1 (mono)

* sample width: 16 bits

* frame rates: 16000 Hz

* NEVER convert from a compressed file (mp3, ...)

* Good recording quality is expected

> Open speech file(s) with SndRoamer component for a diagnosis


## Annotated files: recommendations

* UTF-8 encoding only

* No accentuated characters in file names (nor in the path)

* Supported file formats to open/save (software, extension):

    - SPPAS: xra
    - Praat: TextGrid, PitchTier, IntensityTier
    - Elan: eaf
    - AnnotationPro: antx
    - HTK: lab, mlf
    - Sclite: ctm, stm
    - Phonedit: mrk
    - Excel/OpenOffice/R/...: csv
    - subtitles: sub, srt

* Supported file formats to import (software, extension):
    - Transcriber: trs
    - Anvil: anvil

----------------

### Supported file formats

![](./etc/figures/sppas-formats.png)


## How to cite SPPAS

* By using SPPAS, you agree to cite any of the references in your publications

* Main reference is:

> *Brigitte Bigi (2015).*
> **SPPAS - Multi-lingual Approaches to the Automatic Annotation of Speech**.
> In "the Phonetician", International Society of Phonetic Sciences,
> Volume 111-112, Pages 55-69.

* Other references are available in the documentation.



# What SPPAS can do?



## What SPPAS can do?

* **Automatic and semi-automatic annotations:**

    - **Momel/INTSINT**: Modelling melody
    - **IPUs segmentation**: utterance level segmentation
    - **Tokenization**: text normalization
    - **Phonetization**: grapheme to phoneme conversion
    - **Alignment**: phonetic segmentation
    - **Syllabification**: group phonemes into syllables
    - **Repetitions**: detect self-repetitions

* ... and many other things!

    - Components
    - Plugins

---------------------

### Components and plugins

* *IPUScribe*: Orthographic manual transcription

* *SndRoamer*: Play sound (mono wav)

* *Statistics*: Estimates/Save statistics of tiers, TGA...

* *DataRoamer*: Manipulate annotated files

* *DataFilter*: Select/Filter annotations of tiers

* *SppasEdit*: Display wav and annotated files

* *TierMapping-plugin*: Create tier by mapping annotations

* *MarsaTag-plugin*: Use the POS-Tagger MarsaTag from SPPAS (French only)


## Usage: GUI, CLI or Python Scripts

* Read documentation for command-line interface and python scripts
* Graphical User Interface:
-![](./etc/screenshots/sppas-1-7-6.png)


## GUI Usage (1)

* Open the file explorer of your system

* Go to the SPPAS folder location

* Windows:
    - Doucle-click on the `sppas.bat` file

* MacOS / Linux:
    - Double-click on the `sppas.command` file


## GUI Usage (2)

* Click on the 'Add File' button

* Explore the `samples` folder and choose as many audio files as expected

* All files with the same name as the audio files will be added into the list

* Click (and/or ctrl+click) on some files in this list

* Choose what you want to do with your selection (a component, automatic annotations, plugin)



# Automatic Annotation of Speech in SPPAS


## One of the specificy of SPPAS...

> All the automatic annotations are based on **language independent** approaches

-![](./etc/img/multilangue.png)

* This means:

    1. adding a new language consist ONLY in adding related resources (lexicons, dictionaries, etc)
    2. any user can edit resources to modify them to its own requirements

-----------

### Inputs: Orthographic Transcription / Speech signal

* Enriched Orthographic transcription:

    - Representation of what is "perceived" in the signal
    - Already time-aligned at the utterance level (IPUs segmentation)
    - It **must** includes:

        - Filled pauses
        - Short pauses
        - Repeats
        - Noises and Laugh

* Audio: mono wav file, 16KHz, 16 bits


## Phonetic Segmentation: Overview

* Definition:

> The process of taking the text transcription of an audio speech
> segment and determining where in time particular phonemes occur
> in the speech segment

* Manual vs Automatic?

-![](./etc/screenshots/compare-manual-auto.png)

--------------

### Phonetic Segmentation: in 3 steps

-![](./etc/figures/speech-seg-process.bmp)

--------------

### Tokenization (Phonetic Segmentation step 1)

* Tokenization requires *a list of words* (lexicon)

* To create/edit a lexicon:

    - create/open the file SPPAS/resources/vocab/LANG.vocab
    - save (UTF-8 encoding)

* Input example:

    >Et euh donc donc du coup c'est toi c'est un peu toi q(ui) a les premiers
    >contacts avec le avec le gosse quoi + et puis là ils te demandent le prénom
    >donc faut ce soit prêt là @ parce que putain.

* Output:

    >et euh donc donc du coup c' est toi c'est un_peu toi qui a les premiers
    >contacts avec le avec le gosse quoi + et puis là ils te demandent le
    >prénom donc faut ce soit prêt là @ parce_que putain

-------------

### Phonetization (Phonetic Segmentation step 2)

* Phonetization requires a pronunciation dictionary

* To create/edit a dictionary:

    - create/open the file SPPAS/resources/dict/LANG.dict
    - save (UTF-8 encoding)

* In the phonetization output, by convention, spaces separate words,
minus separate phones and pipes separate phonetic variants of a word. Example:

    - input: `the flight`
    - output: `dh-ax|dh-ah|dh-iy f-l-ay-t`

* If a word is missing of the dictionary, SPPAS generates a pronunciation.

---------------

### Alignment (Phonetic Segmentation step 3)

* Alignment requires an acoustic model

-![](./etc/screenshots/alignment.png)



## Outputs/Results

* Each automatic annotation generates a file

    - the file format can be fixed in the "Settings"

* a "merged" file is created, in TextGrid format

* Save/Export any file into any format (XRA, TextGrid, EAF, CSV) either with the 'Export' or 'Save' buttons

-------------

### Look at the Outputs/Results

* Open file(s) in the SppasEdit component, or Praat, or Elan, ...

    -![](./etc/screenshots/SpeechSeg.png)



# And...

## That's all!

* You are now ready *to test* SPPAS with the proposed set of samples...

* Need help?

    1. the documentation contains most of the answers to your questions!
    2. most of the problems can be solved by updating the version of SPPAS.
    3. there is a SPPAS Users discussion group:
        - <https://groups.google.com/forum/#!forum/sppas-users>

    -![](./etc/logos/sppas-logo.png)

