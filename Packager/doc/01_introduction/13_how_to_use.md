## Capabilities

### What SPPAS can do?

Here is the list of functionalities available to annotate automatically
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



### Interoperability and compatibility


In the scope of the compatibility between SPPAS data and annotated data from
other software tools or programs, SPPAS is able to open/save and convert
files.
The conversion of a file to another file is the process of changing the form 
of the presentation of the data, and not the data itself. Every time, when 
data file is to be used, they must be converted to a readable format for 
the next application. A data conversion is normally an automated process 
to some extent. 
SPPAS provide the possibility to automatically import and export the work 
done on some various file formats from a wide range of other software tools.
For the users, the visible change will be only a different file extension but
for software it is the difference between understanding of the contents of 
the file and the inability to read it. 

SPPAS supports the following software with their file extensions:

* Praat: TextGrid, PitchTier, IntensityTier
* Elan: eaf
* Annotation Pro: antx
* Phonedit: mrk
* Sclite: ctm, stm
* HTK: lab, mlf
* Subtitles: srt, sub
* Signaix: hz
* Excel/OpenOffice/R: csv
* Audacity: txt

And the followings can be imported:

* ANVIL: anvil
* Transcriber: trs
* Xtrans: tdf

![File formats SPPAS can open/save and import/export](./etc/figures/sppas-formats.png)
