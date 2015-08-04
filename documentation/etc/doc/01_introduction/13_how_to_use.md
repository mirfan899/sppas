## Capabilities

### What SPPAS can do?

Here is the list of functionalities available to annotate automatically 
speech data and to analyse annotated files:

1. **Automatic Annotations**

    - **Momel/INTSINT**:     modelling melody
    - **IPUs segmentation**: utterance level segmentation
    - **Tokenization**:      text normalization
    - **Phonetization**:     grapheme to phoneme conversion
    - **Alignment**:         phonetic segmentation
    - **Syllabification**:   group phonemes into syllables
    - **Repetitions**:       detect self-repetitions, and other-repetitions (not in the GUI).


2. **Components**

    - *IPUScribe*:      Manual orthographic transcription
    - *SndPlayer*:      Play sounds (mono wav) and display main information
    - *Statistics*:     Estimates/Save statistics on annotated files
    - *DataRoamer*:     Manipulate annotated files
    - *DataFilter*:     Extract data from annotated files
    - *SppasEdit*:      Display sound and annotated files (development version, unstable)


3. **Plugins**

    - *TierMapping-plugin*: Create tier by mapping annotation labels
    - *MarsaTag-plugin*: Use the POS-Tagger MarsaTag from SPPAS (French only)


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

SPPAS is able to open/save files from the following software, with
the expected extension:

* Praat: TextGrid, PitchTier, IntensityTier
* Elan: eaf
* Sclite: ctm, stm
* HTK: lab, mlf
* Subtitles: srt, sub
* Phonedit: mrk
* Signaix: hz
* Excel/OpenOffice/R: csv

It can also import and export data from:

* Annotation Pro: antx

And it can also import data from:

* ANVIL: anvil
* Transcriber: trs

![File formats SPPAS can open/save and import](./etc/figures/sppas-formats.png)
