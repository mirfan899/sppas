## Syllabification

### Overview

The syllabification of phonemes is performed with a rule-based system from
time-aligned phonemes. This phoneme-to-syllable segmentation system is based
on 2 main principles:

* a syllable contains a vowel, and only one;
* a pause is a syllable boundary.

These two principles focus the problem of the task of finding a syllabic
boundary between two vowels. Phonemes were grouped into classes and rules 
are established to deal with these classes.

![Syllabification example](./etc/screenshots/syll-example.png)


For each language, the automatic syllabification requires a configuration 
file to fix phonemes, classes and rules.


### Adapt Syllabification

Any user can change the set of rules by editing and modifying the 
configuration file of a given language. Such files are located in the 
folder "syll" of the "resources" directory. Files are all with
[UTF-8 encoding](https://en.wikipedia.org/wiki/UTF-8) 
and ["LF" for newline](https://en.wikipedia.org/wiki/Newline).

At first, the list of phonemes and the class symbol associated with 
each of the phonemes are described as, for example:

* `PHONCLASS e V`
* `PHONCLASS p P`

Each association phoneme/class definition is made of 3 columns: 
the first one is the key-word PHONCLASS, the second is the phoneme 
symbol (like defined in the tier with the phonemes, commonly X-SAMPA), 
the last column is the class symbol. 
The constraints on this definition are that a class-symbol is only 
one upper-case character, and that the character X if forbidden,
and the characters V and W are reserved for vowels.

The second part of the configuration file contains the rules.
The first column is a keyword, the second one describes the classes 
between two vowels and the third column is the boundary location.
The first column can be:

* `GENRULE`
* `EXCRULE`
* `OTHRULE`.

In the third column, a "0" means the boundary is just after the 
first vowel, "1" means the boundary is one phoneme after the first 
vowel, etc. Here are some examples of the file for French language:

* `GENRULE VXV 0`
* `GENRULE VXXV 1`
* `EXCRULE VFLV 0`
* `EXCRULE VOLGV 0`

Finally, to adapt the rules to specific situations that the rules failed to
model, we introduced some phoneme sequences and the boundary definition.
Specific rules contain only phonemes or the symbol "ANY" which means any
phoneme. It consists of 7 columns: the first one is the key-word OTHRULE,
the 5 following columns are a phoneme sequence where the boundary should be
applied to the third one by the rules, the last column is the shift to apply
to this boundary. In the following example:

`OTHRULE ANY ANY p s k -2`

More information are available in (Bigi et al. 2010).


### Support of a new language

The support of a new language in this automatic syllabification only 
consists in adding a configuration file (see previous section).
Fix properly the encoding (utf-8) and newlines (LF) of this file; 
then fix the name and extension of the file as follow: 

- "syllConfig-" followed by language name with iso639-3 standard,
- with extension ".txt".


### Perform Syllabification with the GUI

The Syllabification process takes as input a file that strictly match the
audio file name except for the extension and that "-palign" is appended.
For example, if the audio file name is "oriana1.wav", the expected input file
name is "oriana1-palign.xra" if .xra is the default extension for annotations.
This file must include time-aligned phonemes in a tier with name "PhonAlign".

The annotation provides an annotated file with "-salign" appended to its name,
i.e. "oriana1-salign.xra" for the previous example.
This file is including 2 tiers: SyllAlign, SyllClassAlign.

![Syllabification workflow](./etc/figures/syllworkflow.bmp)

To perform the annotation, click on the Syllabification activation button, 
select the language and click on the "Configure..." blue text to fix options.


### Perform Syllabification with the CLI

`syllabify.py` is the program to perform automatic syllabification of a 
given file with time-aligned phones.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: syllabify.py -r config [options]

optional arguments:
    -r config   Rules configuration file name
    -i file     Input file name (time-aligned phonemes)
    -o file     Output file name
    -e file     Reference file name to syllabify between intervals
    -t string   Reference tier name to syllabify between intervals
    --nophn     Disable the output of the result that does not use the reference tier
    --noclass   Disable the creation of the tier with syllable classes
    -h, --help   Show the help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
