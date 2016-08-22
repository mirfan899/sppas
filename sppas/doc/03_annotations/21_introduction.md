## Introduction

### About this chapter

This chapter is not a description on how each automatic annotation is
implemented and how it's working: 
the references are available for that specific purpose!

Instead, this chapter describes how each automatic annotation can be used in 
SPPAS, i.e.
what is the goal of the annotation, 
what are the requirements, 
what kind of resources are used,
what is the expected result
and how to perform it with SPPAS. 
Each automatic annotation is illustrated as a workflow schema, where:

- blue boxes represent the name of the automatic annotation, 
- red boxes represent tiers (with their name mentioned in white),
- green boxes indicate the resource,
- yellow boxes indicate the annotated file (given as input or produced as output).


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
An orthographic transcription has to be performed manually inside the set of 
IPUs. Then tokenization will normalize the transcription. The phonetization
process will convert the normalized text in a set of pronunciations using
X-SAMPA standard. Alignment will perform segmentation at phonemes and tokens
levels, etc.

At the end of each automatic annotation process, SPPAS produces a Procedure
Outcome Report that contains important information about the annotations.

Among others, SPPAS is able to produce automatically annotations from a
recorded speech sound and its orthographic transcription. Let us first
introduce what is required in terms of files, and what is the exactly meaning 
of "recorded speech" and "orthographic transcription".


### File formats and tier names

When using the Graphical User Interface, the file format for input and 
output can be fixed in the Settings and is applied to all annotations,
however file names of each annotation is already fixed and can't be changed.

When using the Command-Line interface, or when using scripts, each 
annotation can be configured independently (file format and file names).

In all cases, **the name of the tiers are fixed and can't be changed**!


### Recorded speech

First of all:

>Only `wav`, `aiff` and `au` audio files and only as mono are supported by SPPAS.

SPPAS verifies if the audio file is 16 bits and 16000 Hz sample rate. 
Otherwise it automatically converts to this configuration.
For very long files, this may take time. So, the following are possible:

1. be patient;
2. prepare by your own the required wav/mono/16000Hz/16bits files to be used in SPPAS.

Secondly, a relatively good recording quality is expected. Providing a
guideline or recommendation for that is impossible, because it depends:
"IPU segmentation" requires a better quality compared to what is expected
by "Alignment", and for that latter, it depends on the language.

![Example of recorded speech](./etc/screenshots/signal.png)


### Orthographic Transcription

An orthographic transcription is often the minimum requirement for a speech 
corpus so it is at the top of the annotation procedure, and it is the entry 
point for most of the automatic annotations, including automatic speech 
segmentation.
But clearly, there are different ways to pronounce the same utterance. 
Consequently, when a speech corpus is transcribed into a written text, the 
transcriber is immediately confronted with the following question:
how to reflect the orality of the corpus?
*Transcription conventions* are then designed to provide rules for
writing speech corpora. These conventions establish phenomena to transcribe 
and also how to annotate them.

In that sense, the orthographic transcription is a subjective representation 
of what is "perceived" in the signal. It **must** includes:

- filled pauses;
- short pauses;
- repeats;
- noises and laugh items (not available for: English, Japanese and Cantonese).

In speech, many phonetic variations occur. Some of these phonologically known 
variants are predictable and can be included in the pronunciation dictionary 
but many others are still unpredictable like invented words, regional words or 
words borrowed from another language. These specifics have a direct consequence
on the automatic phonetization procedure as shown in (Bigi 2012). 
As a consequence, from the beginning of its development it was considered to 
be essential for SPPAS to deal with **Enriched Orthographic Transcriptions**.

The transcription must use the following convention to represent speech 
phenomena. All the symbols must be surrounded by whitespace.

* truncated words, noted as a '-' at the end of the token string (an ex- example);
* noises, noted by a '*' (not available for: English, Japanese and Cantonese);
* laughs, noted by a '@' (not available for: English, Japanese and Cantonese);
* short pauses, noted by a '+';
* elisions, mentioned in parenthesis;
* specific pronunciations, noted with brackets [example,eczap];
* comments are noted inside braces or brackets without using comma {this} or [this and this];
* liaisons, noted between '=' (an =n= example);
* morphological variants with \<like,lie ok\>,
* proper name annotation, like \$ John S. Doe \$.

SPPAS also allows to include in the transcription:

- regular punctuations,
- numbers: they will be automatically converted to their written form.

This convention is not software-dependent which means that it can be performed
with IPUscriber tool of SPPAS, Praat, Annotation Pro, ...

The result is what we call an Enriched Orthographic construction, from which
two derived transcriptions can be generated automatically: 

1. the **standard transcription** is the list of orthographic tokens
2. a specific transcription from which the phonetic tokens are obtained 
to be used by the grapheme-phoneme converter that is named 
**faked transcription**.

As for example with the following sentence:

*This is + hum... an enrich(ed) transcription {loud} number 1!*

The derived transcriptions are:

- standard: this is hum an enriched transcription number one 
- faked: this is + hum an enrich transcription number one


### Automatic Annotations with GUI

To perform automatic annotations with SPPAS Graphical User Interface, select
first the list of audio files and/or a directory, then click on the 
"Annotate" button.

![the annotate panel](./etc/screenshots/AAP.png)

1. Enable each annotation to perform by clicking on the button in red. 
It will be turned green.

2. Each annotation can be configured by clicking on the "Configure..." text
in blue.

3. Select the language for all annotations in one, or for each one independently 
by clicking on the "chains" button.

4. Click on the *Perform annotations* button... and wait! Please, be patient! 
Particularly for Tokenization or Phonetization: loading resources (lexicons 
or dictionaries) is very long. Sometimes, the progress bar does not really 
"progress"... it depends on the system. So, just wait!

5. It is important to read the Procedure Outcome report to check that 
everything happened normally during the automatic annotations.


###  Automatic Annotations with CLI

To perform automatic annotations with SPPAS Command-line User Interface, 
there is a main program `annotation.py` and each annotation has also its own
program with more options than the main one.

This main program performs automatic annotations on a given file or on all 
files of a directory. It strictly corresponds to the button `Perform annotations` 
of the GUI.
All annotations are pre-configured: no specific option can be specified.
This configuration is fixed in the source code packages, via a file with 
extension `.cfg` for each annotation.

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
   --tok           Activate Tokenization
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
./sppas/bin/annotation.py ./samples/samples-eng
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
the annotations!

The text first indicates the version of SPPAS that was used. This information is 
very important, mainly because annotations in SPPAS and their related resources
are regularly improved and then, the result of the automatic process can change
from one version to the other one.

Secondly, the text mentions information related to the given input: 

1. the selected language of each annotation, only if the annotation is 
language-dependent). For some language-dependent annotations, SPPAS can 
still perform the annotation even if the resources for a given language are 
not available: in that case, select "und", which is the iso639-3 code for
"undetermined".
2. the list of files to be annotated; 
3. the list of annotations and if each annotation was activated or disabled. 
In that case, activated means that the checkbox of the AAP was checked by the 
user and that the resources are available for the given language. On the 
contrary, disabled means that either the checkbox of the AAP was not checked 
or the required resources are not available.

In the following, each automatic annotation is described in details, for each
annotated file. Four levels of information must draw your attention:

1. "[   OK    ]" means that everything happened normally. The annotation was 
performed successfully.
2. "[ IGNORED ]" means that SPPAS ignored the file and didn't do anything.
3. "[ WARNING ]" means that something happened abnormally, but SPPAS found
a solution, and the annotation was still performed successfully.
4. "[  ERROR  ]" means that something happened abnormally and SPPAS failed to
found a solution. The annotation was either not performed, or performed with
a bad result.

Finally, the "Result statistics" section mentions the number of files that was
annotated for each step, or -1 if the annotation was disabled. 

![Procedure outcome report](./etc/screenshots/log.png)
