## Capabilities

### What SPPAS can do?

Here is the list of features available to annotate automatically
speech data and to analyze annotated files:

1. Automatic and semi-automatic annotations

    - *Momel*: modelling melody
    - *INTSINT*: Intonation    
    - *IPUs segmentation*: speech/silence segmentation
    - *Text normalization*:  tokenization, remove punctuation, etc
    - *Phonetization*:     grapheme to phoneme conversion
    - *Alignment*:         phonetic segmentation
    - *Syllabification*:   group phonemes into syllables
    - *Repetitions*:       detect self-repetitions, and other-repetitions


2. Analysis

    - *IPUscriber*:     Manual orthographic transcription, after IPUs segmentation
    - *AudioRoamer*:    Play, show information and manage speech audio files
    - *Statistics*:     Estimates/Save statistics on annotated files
    - *DataRoamer*:     Manipulate annotated files
    - *DataFilter*:     Extract data from annotated files (i.e. querying data)
    - *Visualizer*:     Display sound and annotated files 


3. Plugins

    - *SAMPA to IPA*: convert SAMPA into IPA phonemes encoding
    - *SAMPA to Praat-IPA*: convert SAMPA into Praat phonemes encoding
    - *Classify phones*: create tiers with the phonemes classification (articulatory information)
    - *Marsatag*: apply MarsaTag French POS-tagger on time-aligned files
    - *sox*: call the Swiss Army Knife of sound processing utilities from SPPAS
    

### How to use SPPAS?

There are three main ways to use SPPAS:

1. The Graphical User Interface (GUI) is as user-friendly as possible:

    * double-click on the `sppas.bat` file, under Windows;
    * double-click on the `sppas.command` file, under MacOS or Linux.

2. The Command-line User Interface (CLI), with a set of programs, each one
essentially independent of the others, that can be run on its own at the level
of the shell.

3. Scripting with Python and SPPAS provides the more powerful way.


