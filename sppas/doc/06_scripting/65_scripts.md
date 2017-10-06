## Creating scripts with annotationdata API


### Preparing the data

To practice, you have first to create a new folder in your computer 
- on your Desktop for example; with name "sppasscripts" for example,
and to execute the python IDLE.

Open a File Explorer window and go to the SPPAS folder location.
Then, copy the `sppas` directory into the newly created "sppasscripts" 
folder. Then, go to the solution directory and copy/paste the files
`skeleton-sppas.py` and `F_F_B003-P9-merge.TextGrid` into your 
"sppasscripts" folder.
Then, open the skeleton script with the python IDLE and execute it.
It will do... nothing! But now, you are ready to do something with the
API of SPPAS!


### Read/Write annotated files

We are being to Open/Read a file of any format (XRA, TextGrid, Elan, ...) 
and store it into a `Transcription` object instance. Then, the latter
will be saved into another file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
trs = trsio.read(filename_in)
trsaio.write(filename_out, trs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Only these two lines of code are required to convert a file from one format 
to another one!
The appropriate reader/writer for the format is given by the extension of the
name of the file.

To get the list of accepted extensions that the API can read, just use 
`trsaio.extensions_in`. The list of accepted extensions that the API can write 
is given by `trsaio.extensions_out`.

Currently, accepted input file extensions are:

* xra
* csv, txt
* TextGrid, PitchTier, IntensityTier
* eaf
* trs
* mrk
* sub, srt
* hz
* antx
* tdf

Possible output file extensions are:

* xra
* csv, txt, lab, ctm, stm
* TextGrid, PitchTier
* eaf
* mrk
* sub, srt
* antx

>*Practice:* Write a script to convert a TextGrid file into CSV
>(solution: ex10_read_write.py)


### Manipulating a Transcription object

The most useful functions used to manage a Transcription object are:

* `Append(tier)`, `Pop()`
* `Add(tier, index)`, `Remove(index)`
* `Find(name, case_sensitive=True)`

`Append()` is used to add a tier at the end of the list of tiers of the 
Transcription object; and `Pop()` is used to remove the last tier of such list.

`Add()` and `Remove()` do the same, except that it does not put/delete the tier 
at the end of the list but at the given index.

`Find()` is useful to get a tier from its name.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="15"}
trs = trsaio.read('Filename-palign.TextGrid)
for tier in trs:
    # do something with the tier:
    print(tier.GetName())
phonemes_tier = trs.Find("PhonAlign")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

Transcription object has an iterator to get access to tiers.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="15"}
trs = trsaio.read('Filename-palign.TextGrid)
phonemes_tier = trs[0]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

>*Practice:*
>Write a script to select a set of tiers of a file and save them into a new file
>(solution: ex11_transcription.py).


### Manipulating a Tier object

A tier is made of a name, a list of annotations and meta-data.
To get the name of a tier, or to fix a new name, the easier way is to
use `tier.GetName()`. 

The following block of code allow to get a tier and change its name. It should be
tested into a script...

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="43"}
trs = trsaio.read(filename)
tier = trs[0]
print(tier.GetName())
tier.SetName("toto")
print(tier.GetName())
print(trs[0].GetName())
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

The most useful functions to manage a Tier object are:

* `Append(annotation)`, `Pop()`
* `Add(annotation)`, `Remove(begin, end, overlaps=False)`
* `IsDisjoint()`, `IsInterval()`, `IsPoint()`
* `Find(begin, end, overlaps=True)`
* `Near(time, direction)`
* `SetRadius(radius)`

>Practice:
>Write a script to open an annotated file and print information about tiers
>(solution: ex12_tiers_info.py)


**Goodies:**
 
The file `ex12_tiers_info_wx.py` proposes a GUI to print information of one 
file, or all files of a directory, and to ask the file/directory name with a 
dialogue frame, instead of fixing it in the script. This script can be executed 
simply by double-clicking on it in the File Explorer of your system.
Many functions of this script can be cut/pasted in any other script.


### Main information on Annotation/Location/Label objects

The most useful methods used to manage an `Annotation` object are:

* `IsSilence()`, `IsLabel()`
* `IsPoint()`, `IsInterval()`, `IsDisjoint()`
* `GetBegin()`, `SetBegin(time)`, only if time is a TimeInterval
* `GetEnd()`, `SetEnd(time)`, only if time is a TimeInterval
* `GetPoint()`, `SetPoint(time)`, only if time is a TimePoint

The following example shows how to get/set a new label, and to set a new time 
value to an annotation:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
if ann.GetLabel().IsEmpty():
    ann.GetLabel().SetValue("dummy")
if ann.GetLocation().IsPoint():
    p = ann.GetLocation().GetPoint()
    p.SetMidPoint(0.234)
    p.SetRadius(0.02)
if ann.GetLocation().IsInterval():
    ann.GetLocation().GetBegin().SetMidPoint(0.123)
    ann.GetLocation().GetEnd().SetMidPoint(0.234)    
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

If something forbidden is attempted, the object will raise an Exception. 
This means that the program will stop except if the script "raises" the 
exception.


### Exercises


>Exercise 1:
>Write a script to print information about annotations of a tier
>(solution: ex13_tiers_info.py)

>Exercise 2:
>Write a script to estimates the frequency of a specific annotation label in a file/corpus
>(solution: ex14_freq.py)

    
    
### Search in annotations: Filters

#### Overview

This section focuses on the problem of *searching and retrieving* data from 
annotated corpora. 

The filter implementation can only be used together with the `Tier()` class. 
The idea is that each `Tier()` can contain a set of filters, that each reduce 
the full list of annotations to a subset. 

SPPAS filtering system proposes 2 main axis to filter such data: 

* with a boolean function based either on the content, the duration or on the time of annotations, 
* with a relation function between annotation locations of 2 tiers. 

A set of filters can be created and combined to get the expected result.
To be able to apply filters to a tier, some data must be loaded first. 
First, a new `Transcription()` has to be created when loading a file.
Then, the tier(s) to apply filters on must be fixed. Finally,
if the input file was NOT an XRA, it is widely recommended to fix a radius 
value depending on the annotation type. 


#### Creating a boolean function

In the following, let `Bool` and `Rel` two predicates, 
a tier `T`, and a filter `f`.

Thus, the following matching predicates are proposed to select annotations
(intervals or points) depending on their label. Notice that `P` 
represents the text pattern to find:

* exact match: `pr = Bool(exact=P)`, means that a label is valid if it strictly corresponds to the expected pattern;
* contains: `pr = Bool(contains=P)`, means that a label is valid if it contains the expected pattern;
* starts with, `pr = Bool(startswith=P)`, means that a label is valid if it starts with the expected pattern;
* ends with, `pr = Bool(endswith=P)`, means that a label is valid if it ends with the expected pattern.

These predicates are then used while creating a filter on labels.
All these matches can be reversed, to represent does not exactly match, 
does not contain, does not start with or does not end with.

The next examples illustrate how to work with such filters and patterns.
In this example, `f1` is a filter used to get all phonemes with the exact label
'a'. On the other side, `f2` is a filter that ignores all phonemes matching 
with 'a' (mentioned by the symbol '~') with a case insensitive comparison
(iexact means insensitive-exact).

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
tier = trs.Find("PhonAlign")
ft = Filter(tier)
f1 = LabelFilter(Bool(exact='a'), ft)
f2 = LabelFilter(~Bool(iexact='a'), ft)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For complex search, a selection based on regular expressions is available 
by using `pr = Bool(regexp=R)`.

A multiple pattern selection can be expressed with the operators
`|` to represent the logical "or" and the operator `&` to represent 
the logical "and".

With this notation in hands, it is possible to formulate queries as, 
for example: *Extract words starting by "ch" or "sh"*, like:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
pr = Bool(startswith="ch") | Bool(startswith="sh")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Filters on duration can also be created on annotations if Time instance is 
of type TimeInterval. 
In the following, `v` represents the value to be compared with:

* lower: `pr = Bool(duration_lt=v)`, means that an annotation of `T` is valid if its duration is lower than `v`;
* lower or equal: `pr = Bool(duration_le=v)`;
* greater: `pr = Bool(duration_gt=v)`;
* greater or equal: `pr = Bool(duration_ge=v)`;
* equal: `pr = Bool(duration_e=v)`;

Search can also starts and ends at specific time values in a tier by 
creating filters with `begin_ge` and `end_le`.

Finally, the user must apply the filter to get filtered data from the filter.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
# creating a complex boolean function
predicate = (Bool(icontains="a") | Bool(icontains="e")) & Bool(duration_ge=0.08)

# to create a filter:
ft = Filter(tier)
flab = LabelFilter(predicate, ft)

# to get filtered data from the filter:
tier = flab.Filter()
tier.SetName('Filtered with a-e-0.8')
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#### Creating a relation function

Relations between annotations is crucial if we want to extract multimodal data. 
The aim here is to select intervals of a tier depending on what is represented
in another tier.

We implemented the 13 Allen interval relations: before, after, meets, met by, 
overlaps, overlapped by, starts, started by, finishes, finished by, contains,
during and equals.
Actually, we implemented the 25 relations proposed in the INDU model.
This model is fixing constraints on INtervals (with Allen's relations) and 
on DUration (duration are equals, one is less/greater than the other).


**MISSING:List of Allen interval relations./etc/screenshots/allen.png**


Below is an example of implementing the request: 
*Which syllables stretch across 2 words?*

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
# Get tiers from a Transcription object
tiersyll = trs.Find("Syllables")
tiertoks = trs.Find("TokensAlign")

# Create filters
fsyll = Filter(tiersyll)
ftoks = Filter(tiertoks)

# Create the filter with the relation function (link both filters)
predicate = Rel("overlaps") | Rel("overlappedby")
f = RelationFilter(relation, fsyll, ftoks)

# to get filtered data from the filter:
tier = f.Filter()
tier.SetName('Syllables across Tokens')
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Exercises


>Exercise 1: Create a script to filter annotated data on their label
>(solution: ex15_annotation_label_filter.py).

>Exercise 2: Idem with a filter on duration or time.
>(solution: ex16_annotation_time_filter.py).

>Exercise 3: Create a script to get tokens followed by a silence.
>(solution: ex17_annotations_relation_filter1.py).
 
>Exercise 4: Create a script to get tokens preceded by OR followed by a silence.
>(solution: ex17_annotations_relation_filter2.py).
    
>Exercise 5: Create a script to get tokens preceded by AND followed by a silence.
>(solution: ex17_annotations_relation_filter3.py).


## More with SPPAS API

In addition to *annotationdata*, SPPAS contains several other API that could 
be relevant for users to simplify their lives!!!
They are all free and open source Python libraries, with a documentation and a
set of tests.

Among others:

- *audiodata* to manage digital audio data: load, get information, extract channels, re-sample, search for silences, mix channels, etc.
- *calculus* to perform some math on data, including descriptive statistics. 
- *resources* to access and manage linguistic resources like lexicons, dictionaries, etc.
