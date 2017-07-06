## Syllabification

### Overview

The syllabification of phonemes is performed with a rule-based system from
time-aligned phonemes. This phoneme-to-syllable segmentation system is based
on 2 main principles:

* a syllable contains a vowel, and only one;
* a pause is a syllable boundary.

These two principles focus the problem of the task of finding a syllabic
boundary between two vowels. Phonemes were grouped into classes and rules were
established to deal with these classes.

![Syllabification example](./etc/screenshots/syll-example.png)


Syllabification requires a configuration file to indicate phonemes, classes 
and rules.

### Adapt Syllabification

Any user can change the set of rules by editing and modifying the 
configuration file of a given language. Files are located in the folder 
"syll" of the "resources" directory. Files are all with
[UTF-8 encoding](https://en.wikipedia.org/wiki/UTF-8) 
and ["LF" for newline](https://en.wikipedia.org/wiki/Newline).

At first, the list of phonemes and the class symbol associated with each of the
phonemes are described as, for example:

* `PHONCLASS e V`
* `PHONCLASS p O`

The couples phoneme/class are made of 3 columns: the first column is the
key-word PHONCLASS, the second column is the phoneme symbol, the third column
is the class symbol. The constraints on this definition are:

* a pause is mentioned with the class-symbol #,
* a class-symbol is only one upper-case character, except:
    * the character X if forbidden;
    * the characters V and W are reserved for vowels.

The second part of the configuration file contains the rules.
The first column is a keyword, the second column describes the classes between
two vowels and the third column is the boundary location.
The first column can be:

* `GENRULE`
* `EXCRULE`
* `OTHRULE`.

In the third column, a 0 means the boundary is just after the first vowel,
1 means the boundary is one phoneme after the first vowel, etc.
Here are some examples of the file for French language:

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

The support of a new language in Syllabification only consists in adding
its configuration file (see previous section).
Fix properly its encoding (utf-8), its newlines (LF), 
and fix the name and extension of the file as follow: 

- "syllConfig-" followed by language name with iso639-3 standard
- extension ".syll"


### Perform Syllabification with the GUI

The Syllabification process takes as input a file that strictly match the
audio file name except for the extension and that "-palign" is appended.
For example, if the audio file name is "oriana1.wav", the expected input file
name is "oriana1-palign.xra" if .xra is the default extension for annotations.
This file must include a tier containing the time-aligned phonemes with
name "PhonAlign".

The annotation provides an annotated file with "-salign" appended to its name,
i.e. "oriana1-salign.xra" for the previous example.
This file is including 3 tiers: Syllables, Classes and Structures.

![Syllabification workflow](./etc/figures/syllworkflow.bmp)

Click on the Syllabification activation button, select the language and click
on the "Configure..." blue text to fix options.


### Perform Syllabification with the CLI

`syllabify.py` is the program performs automatic syllabification of a given
file with time-aligned phones.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: syllabify.py -r config [options]

optional arguments:
    -r config   Rules configuration file name
    -i file     Input file name (time-aligned phonemes)
    -o file     Output file name
    -e file     Reference file name to syllabify between intervals
    -t string   Reference tier name to syllabify between intervals
    --nophn     Disable the output of the result that does not use the reference  tier
    -h, --help   Show the help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
