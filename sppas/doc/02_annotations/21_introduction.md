## Introduction

### About this chapter

This chapter is not a description on how each automatic annotation is
implemented and how it's working: 
the references are available for that specific purpose!

Instead, this chapter describes how each automatic annotation can be
used in SPPAS, i.e.
what is the goal of the annotation, 
what are the requirements, 
what kind of resources are used,
and what is the expected result. 
Each automatic annotation is then illustrated as a workflow schema, where:

- blue boxes represent the name of the automatic annotation, 
- red boxes represent tiers (with their name mentioned in white),
- green boxes indicate the resource,
- yellow boxes indicate the annotated file (given as input or produced as output).

At the end of each automatic annotation process, SPPAS produces a Procedure
Outcome Report that aims to be read!


Among others, SPPAS is able to produce automatically annotations from a
recorded speech sound and its orthographic transcription. Let us first
introduce what is the exaclty meaning of
"recorded speech" and "orthographic transcription".


### File formats and tier names

When using the Graphical User Interface, the file format for input and 
output can be fixed in the Settings and is applied to all annotations,
and file names of each annotation is already fixed and can't be changed.
When using the Command-Line interface, or when using scripts, each 
annotation can be configured independently (file format and file names).
In all cases, **the name of the tiers are fixed and can't be changed**!


### Recorded speech

First of all:

>Only `wav`, `aiff` and `au` audio files and only as mono are supported by SPPAS.

SPPAS verifies if the wav file is 16 bits and 16000 Hz sample rate. 
Otherwise it automatically converts to this configuration.
For very long files, this may take time. So, the following are possible:

1. be patient
2. prepare by your own the required wav/mono/16000Hz/16bits files to be used in SPPAS

Secondly, a relatively good recording quality is expected. Providing a
guideline or recommendation for that is impossible, because it depends:
"IPU segmentation" requires a better quality compared to what is expected
by "Alignment", and for that latter, it depends on the language.

![Example of recorded speech](./etc/screenshots/signal.png)


### Orthographic Transcription

#### Overview

>Only UTF-8 encoding is supported by SPPAS.

Clearly, there are different ways to pronounce the same utterance. 
Different speakers have different accents and tend to speak at different 
rates.
There are commonly
two types of Speech Corpora. First is related to “Read Speech” which 
includes book excerpts, broadcast news, lists of words, sequences of numbers. 
Second is often named as “Spontaneous Speech” which includes dialogs - 
between two or more people (includes meetings), narratives - a person 
telling a story, map- tasks - one person explains a route on a map to another,
appointment-tasks - two people try to find a common meeting time based on 
individual schedules. One of the characteristics of Spontaneous Speech is 
an important gap between a word’s phonological form and its phonetic 
realizations. Specific realization due to elision or reduction processes
are frequent in spontaneous data. It also presents other types of phenomena 
such as non-standard elisions, substitutions or addition of phonemes which
intervene in the automatic phonetization and alignment tasks.

Consequently, when a speech corpus is transcribed into a written text, the 
transcriber is immediately confronted with the following question:
how to reflect the orality of the corpus?
*Transcription conventions* are then designed to provide rules for
writing speech corpora. These conventions establish
phenomena to transcribe and also how to annotate them.

In that sense, the orthographic transcription must be a representation 
of what is “perceived” in the signal. Consequently, it **must** includes:

- filled pauses;
- short pauses;
- repeats;
- noises and laugh items (not available for: English, Japanese and Cantonese).

In speech (particularly in spontaneous speech), many phonetic variations 
occur. Some of these phonologically known variants are predictable and can 
be included in the pronunciation dictionary but many others are still 
unpredictable (especially invented words, regional words or words borrowed 
from another language). 

> SPPAS is the only automatic annotation software that deals with **Enriched Orthographic Transcriptions**.


#### Convention

The transcription must use the following convention:

* truncated words, noted as a ’-’ at the end of the token string (an ex- example);
* noises, noted by a ’*’ (not available for: English, Japanese and Cantonese);
* laughs, noted by a ’@’ (not available for: English, Japanese and Cantonese);
* short pauses, noted by a ’+’;
* elisions, mentioned in parenthesis;
* specific pronunciations, noted with brackets [example,eczap];
* comments are noted inside braces or brackets without using comma {this} or [this and this];
* liaisons, noted between ’=’ (an =n= example);
* morphological variants with \<like,lie ok\>,
* proper name annotation, like \$John S. Doe\$.

SPPAS also allows to include in the transcription:

- regular punctuations,
- numbers: they will be automatically converted to their written form.

The result is what we call an enriched orthographic construction, from which
two derived transcriptions are generated automatically: 
the **standard transcription** (the list of orthographic tokens) 
and a specific transcription from which the phonetic tokens are obtained 
to be used by the grapheme-phoneme converter that is named **faked transcription**.


#### Example

*This is + hum... an enrich(ed) transcription {loud} number 1!*

The derived transcriptions are:

- standard: this is hum an enriched transcription number one 
- faked: this is + hum an enrich transcription number one
