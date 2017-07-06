## Orthographic Transcription

An orthographic transcription is often the minimum requirement for a speech 
corpus so it is at the top of the annotation procedure, and it is the entry 
point for most of the automatic annotations.
*Transcription conventions* are then designed to provide rules for
writing speech corpora. These conventions establish which are the phenomena
to transcribe and also how to mention them in the orthography.

In speech, many phonetic variations occur. Some of these phonologically known 
variants are predictable and can be included in the pronunciation dictionary 
but many others are still unpredictable like invented words, regional words or 
words borrowed from another language. These specifics have a direct consequence
on the automatic phonetization procedure (Bigi 2012). 
As a consequence, from the beginning of its development it was considered to 
be essential for SPPAS to deal with an **Enriched Orthographic Transcription**.

The transcription convention is summarized below. Notice that all the symbols 
must be surrounded by whitespace. The file `TOE-SPPAS.pdf` available in the 
`documentation` folder gives details of the convention, including examples of 
what is recommended.

Convention overview:

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

SPPAS also allows to include in the transcription the regular punctuations,
and numbers (not available for some languages). Numbers will be automatically 
converted to their written form during Text Normalization process.

From this Enriched Orthographic construction, several derived transcriptions 
can be generated automatically, including the followings: 

1. the standard transcription is the list of orthographic tokens
2. a specific transcription from which the phonetic tokens are obtained 
to be used by the grapheme-phoneme converter that is named 
faked transcription.

As for example with the transcribed sentence: *This [is,iz] + hum... an enrich(ed)
transcription {loud} number 1!*. The derived transcriptions are:

- standard: *this is + hum an enriched transcription number one*
- faked: *this iz + hum an enrich transcription number one*

The convention then allows to include a large scale of phenomena, for which 
most of them are optional. As a minimum, the orthographic **transcription 
must include**:

- filled pauses;
- short pauses;
- repeats;
- noises and laugh items (not available for: English, Japanese and Cantonese).

Finally, it has to be noticed that this convention is not software-dependent.
The orthographic transcription can be performed with IPUscriber tool
of SPPAS, Praat, Annotation Pro, Audacity, ...
