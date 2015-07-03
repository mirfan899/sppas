## Syllabification

The syllabification of phonemes is performed with a rule-based system from 
time-aligned phonemes. This phoneme-to-syllable segmentation system is based
on 2 main principles:

* a syllable contains a vowel, and only one;
* a pause is a syllable boundary.

These two principles focus the problem of the task of finding a syllabic 
boundary between two vowels. As in state-of-the-art systems, phonemes were 
grouped into classes and rules established to deal with these classes.
We defined general rules followed by a small number of exceptions. 
Consequently, the identification of relevant classes is important 
for such a system.

We propose the following classes, for both French and Italian set of rules:

* V - Vowels, 
* G - Glides,
* L - Liquids,
* O - Occlusives, 
* F - Fricatives,
* N - Nasals.

The rules we propose follow usual phonological statements for most of the 
corpus. A configuration file indicates phonemes, classes and rules. 
This file can be edited and modified to adapt the syllabification.

For more details, see the following reference:

>**B. Bigi, C. Meunier, I. Nesterenko, R. Bertrand** (2010).
>*Automatic detection of syllable boundaries in spontaneous speech.*
>Language Resource and Evaluation Conference, pp 3285-3292, La Valetta, Malte.

![Syllabification workflow](./etc/figures/syllworkflow.bmp)

The Syllabification annotation takes as input one file with (at least) one 
tier containing the time-aligned phonemes.
The annotation provides one annotated file with 3 tiers (Syllables, Classes
and Structures).

![Syllabification example](./etc/screenshots/syll-example.png)

If the syllabification is not as expected, you can change the set of rules.
The configuration file is located in the sub-directory "syll" of the
"resources" directory.

The syllable configuration file is a simple ASCII text file that any user can 
change as needed. At first, the list of phonemes and the class symbol 
associated with each of the phonemes are described as, for example:

* `PHONCLASS e V`
* `PHONCLASS p O`

The couples phoneme/class are made of 3 columns: the first column is the 
key-word PHONCLASS, the second column is the phoneme symbol, the third column 
is the class symbol.The constraints on this definition are: 

* a pause is mentioned with the class-symbol #,
* a class-symbol is only one upper-case character, except:
    * the character X if forbidden;
    * the characters V and W are used for vowels.   

The second part of the configuration file contains the rules. 
The first column is a keyword, the second column describes the classes between 
two vowels and the third column is the boundary location. 
The first column can be:

* `GENRULE`,
* `EXCRULE`, or
* `OTHRULE`.

In the third column, a 0 means the boundary is just after the first vowel, 
1 means the boundary is one phoneme after the first vowel, etc. 
Here are some examples, corresponding to the rules described in this paper 
for spontaneous French:

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
