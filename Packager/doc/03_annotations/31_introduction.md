## Introduction

### About this chapter

This chapter is not a description on how each automatic annotation is
implemented and how it's working: 
references are available for that in chapter 7.

Instead, this chapter describes how each automatic annotation can be used in 
SPPAS, i.e.
what is the goal of the annotation, 
what are the requirements, 
what kind of resources are used,
what is the expected result
and how to perform it within SPPAS. 

Each automatic annotation process is illustrated as a workflow schema, where:

- blue boxes represent the name of the automatic annotation; 
- red boxes represent tiers, with their name in white;
- green boxes indicate the resource;
- yellow boxes indicate the annotated file either given as input or produced as result.


### Annotations methodology

The kind of process to implement in the perspective of obtaining rich and 
broad-coverage multimodal/multi-levels annotations of a corpus is illustrated 
in next Figure. It describes each step of the annotation workflow. This 
Figure must be read from top to bottom and from left to right, starting by 
the recordings and ending to the analysis of annotated files.
Yellow boxes represent manual annotations, blue boxes represent automatic ones.

![Annotation methodology](./etc/figures/methodo.png)

After the recording, the first annotation to perform is IPUs segmentation. 
Indeed, at a first stage, the audio signal must be automatically segmented 
into Inter-Pausal Units (IPUs) which are blocks of speech bounded by silent 
pauses of more than X ms, and time-aligned on the speech signal. 
**An orthographic transcription has to be performed manually inside the IPUs**.
Then text normalization automatic annotation will normalize the orthographic
transcription. The phonetization process will convert the normalized text in 
a set of pronunciations using X-SAMPA standard. Alignment will perform 
segmentation at phonemes and tokens levels, etc.

At the end of each automatic annotation process, SPPAS produces a *Procedure
Outcome Report* that contains important information about the annotations.
This window opens in the scope to be read by users (!) and can be saved with
the annotated corpus. It mentions all parameters and eventually warnings and
errors that occurred during the annotation process.

Among others, SPPAS is able to produce automatically annotations from a
recorded speech sound and its orthographic transcription. Let us first
introduce what is required in terms of files, and what is the exactly meaning 
of "recorded speech" and "orthographic transcription".


### File formats and tier names

When using the Graphical User Interface, the file format for input and 
output can be fixed in the Settings and is applied to all annotations.
However, while using the GUI to annotate, the file names of each annotation 
is already fixed and can't be changed.

When using the Command-Line interface, or when using scripts, each 
annotation can be configured independently (both file format and file names).

In all cases, **the name of the tiers are fixed and can't be changed**!


### Recorded speech

>Only `wav` and `au` audio file formats are supported by SPPAS.

>Only mono audio files are supported by SPPAS.

SPPAS verifies if the audio file is 16 bits sample rate and 16000 Hz frame
rate. Otherwise it automatically create a copy of the audio file converted
to this configuration. For very long files, this process may take time. So, 
the following 2 options are possible:

1. be patient;
2. prepare by your own the required wav/mono/16000Hz/16bits files to be used in SPPAS.

Secondly, a relatively good recording quality is expected. Providing a
guideline or recommendation for that is impossible, because it depends
on many factors. For example, "IPU segmentation" requires a better quality 
compared to what is expected by "Alignment", and for that latter, it depends 
on the language. The quality of the result of automatic annotations highly
depends on the quality of the audio file. SPPAS simply performs automatic 
annotations: It does not make sense to hope for miracles but you can expect
good enough results that will allow you to save your precious time!
And it begins by taking care of the recordings...

![Example of expected recorded speech](./etc/screenshots/signal.png)


### Automatic Annotations with GUI

To perform automatic annotations with SPPAS Graphical User Interface, select
first the list of audio files and/or a directory, then click on the 
"Annotate" button.

![The annotate panel](./etc/screenshots/AAP.png)

1. Enable each annotation to perform by clicking on the button in red. 
It will be turned green.

2. Select options and configure each annotation by clicking on the 
"Configure..." link text in blue.

3. Select the language for all annotations in one; or for each annotation
independently by clicking on the "chains" button first then selecting each 
language.

4. Click on the *Perform annotations* button, and wait. Be patient! 
Particularly for Text Normalization or Phonetization: loading resources 
(lexicons or dictionaries) can be very long. Sometimes, the progress bar 
does not really show the progress... it depends on the operating system 
and the power of the computer. So, just wait!

5. It is important to read the Procedure Outcome report to check that 
everything happened normally during the automatic annotations.


###  Automatic Annotations with CLI

To perform automatic annotations with SPPAS Command-line User Interface, 
there is a main program `annotation.py`. Each annotation has also its own
program with more options than the previous one.

This main program performs automatic annotations on a given file or on all 
files of a directory. It strictly corresponds to the button 
`Perform annotations`  of the GUI.
All annotations are pre-configured: no specific option can be specified.
The options of annotations are fixed files with extension `.ini` in 
`sppas/etc` folder.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: annotation.py -w file|folder [options]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
optional arguments:
   -h, --help      show this help message and exit
   -w file|folder  Input wav file name, or folder
   -l lang         Input language, using iso639-3 code
   -e extension    Output extension. One of: xra, textgrid, eaf, csv, ...
   --momel         Activate Momel and INTSINT
   --ipu           Activate IPUs Segmentation
   --tok           Activate Text Normalization
   --phon          Activate Phonetization
   --align         Activate Alignment
   --syll          Activate Syllabification
   --rep           Activate Repetitions
   --all           Activate ALL automatic annotations
   --merge         Create a merged TextGrid file, if more than two automatic
                   annotations (this is the default).
   --nomerge       Do not create a merged TextGrid file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examples of use:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./sppas/bin/annotation.py -w ./samples/samples-eng
                          -l eng
                          --ipu --tok --phon --align
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A progress bar is displayed for each annotation. At the end of the process,
a message indicates the name of the procedure outcome report file, which
is `./samples/samples-eng.log` in our example. This file can be opened with
any text editor (as Notepad++, vim, TextEdit, ...).

![CLI: annotation.py output example](./etc/screenshots/CLI-example.png)


### The procedure outcome report

It is very important to read conscientiously this report: it mentions 
exactly what happened during the automatic annotation process.
This text can be saved: it is recommended to be kept it with the related data
because it contains information that are interesting to know for anyone using
the annotations.

The text first indicates the version of SPPAS that was used. This information is 
very important. Annotations in SPPAS and their related resources are regularly 
improved and then, the result of the automatic process can change from one 
version to the other one.

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SPPAS version 1.9.0
Copyright (C) 2011-2017 Brigitte Bigi
Site web: http://www.sppas.org/
Contact: Brigitte Bigi(brigite.bigi@gmail.com)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Secondly, the text mentions information related to the given input: 

1. the selected language of each annotation, only if the annotation is 
language-dependent). For some language-dependent annotations, SPPAS can 
still perform the annotation even if the resources for a given language are 
not available: in that case, select "und", which is the iso639-3 code for
"undetermined".
2. the list of files to be annotated.
3. the list of annotations and if each annotation was activated or disabled. 
In that case, activated means that the checkbox of the AAP was checked by the 
user and that the resources are available for the given language. On the 
contrary, disabled means that either the checkbox of the AAP was not checked 
or the required resources are not available.
4. the file format of the resulting files.

Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Date: 2017-07-05 12:15:40.637000
Langages selectionnés: 
  - Momel: 
  - INTSINT: 
  - IPUs Segmentation: 
  - Text Normalization: eng
  - Phonetization: eng
  - Alignment: eng
  - Syllabification: und
  - Self-repetitions: eng
------------------------------------------------------------------------------
Fichiers sélectionnés: 
  - oriana1.wav
------------------------------------------------------------------------------
Annotations sélectionnées: 
  - Momel: désactivé
  - INTSINT: désactivé
  - IPUs Segmentation: sélectionné
  - Text Normalization: sélectionné
  - Phonetization: sélectionné
  - Alignment: sélectionné
  - Syllabification: désactivé
  - Self-repetitions: désactivé
------------------------------------------------------------------------------
Extension de fichiers: .xra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thirdly, each automatic annotation is described in details, for each
annotated file. At a first stage, the list of options and their value
is summarized. 
Example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ... Text Normalization du fichier oriana1.wav
 ...  ... Options: 
 ...  ...  ...  - faked: True
 ...  ...  ...  - std: False
 ...  ...  ...  - custom: False
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Then, a diagnosis of the given file is printed. This 
latter can be:
1. "Valid": the file is relevant
2. "Admit": the file is not as expected but SPPAS will convert it in a copy and work on it.
3. "Invalid": SPPAS can't work with that file. The annotation of this file is disabled.
In case 2 and 3, a message indicates the origin of the problem.

Example of "Valid" diagnosis:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ...  ... Diagnostic: 
 ...  ...  ...  - oriana1.xra: Valide. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example of "Admit" diagnosis:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ...  ... Diagnostic: 
 ...  ...  ...  - M_3.wav: Admis. La taux d'échantillonage d'un fichier audio est
  de préférence 16000 Hz. Ce fichier est échantilloné à 44100 Hz, SPPAS créera une
  copie et travaillera sur celle-ci.
 ...  ...  ...  - M_3-phon.xra: Valide. 
 ...  ...  ...  - M_3-token.xra: Valide. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Then, if any, the annotation procedure prints message.
Four levels of information must draw your attention:

1. "[   OK    ]" means that everything happened normally. The annotation was 
performed successfully.
2. "[ IGNORE  ]" means that SPPAS ignored the file and didn't do anything.
3. "[ WARNING ]" means that something happened abnormally, but SPPAS found
a solution, and the annotation was still performed successfully.
4. "[  ERROR  ]" means that something happened abnormally and SPPAS failed to
found a solution. The annotation was either not performed, or performed with
a bad result.

Example of "Warning" message:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ...  ... Export AP_track_0711.TextGrid
 ...  ... into AP_track_0711.xra
 ...  ... [ IGNORE  ] because a previous segmentation is existing.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example of "Warning" message:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ...  ...  ... [ WARNING  ] chort- est absent du dictionnaire et a été phonétisé 
  automatiquement S-o-R-t
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At the end of the report, the "Result statistics" section mentions the 
number of files that was annotated for each step, or -1 if the annotation 
was disabled. 

![Procedure outcome report](./etc/screenshots/log.png)


## New language support

Some of the annotations are requiring linguistic resources in order to work
efficiently on a given language: text normalization requires a lexicon,
phonetization requires a pronunciation dictionary, etc. Each section of this
chapter which is describing an annotation also is also including *the way to 
create the related resource*. 
The next chapter contains details about the existing resources 
- list of phonemes, authors, licenses, etc.

While starting SPPAS, the Graphical User Interface dynamically creates the 
list of available languages of each annotation by exploring the related folder.
This means that:

* appended resources are automatically taken into account 
  (ie. there's no need to modify the program itself);
* SPPAS needs to be re-started if new resources are appended 
  while it was already being running.
