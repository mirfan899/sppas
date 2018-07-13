## Creating scripts with anndata


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

When using the API, if something forbidden is attempted, the object will
raise an Exception. It means that the program will stop except if the
script "raises" the exception.


### Read/Write annotated files

We are being to Open/Read an annotated file of any format (XRA, TextGrid,
Elan, ...) and store it into a `sppasTranscription` object instance.
Then, it will be saved into another file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
# Create a parser object then parse the input file.
parser = sppasRW(input_filename)
trs = parser.read()

# Save the sppasTranscription object into a file.
parser.set_filename(output_filename)
parser.write(trs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Only these two lines of code are required to convert a file from a format
to another one! The appropriate parsing system is extracted from the extension
of file name.

To get the list of accepted extensions that the API can read, just use 
`aio.extensions_in`. The list of accepted extensions that the API can write
is given by `aio.extensions_out`.

>*Practice:* Write a script to convert a TextGrid file into CSV
>(solution: ex10_read_write.py)


### Manipulating a sppasTranscription object

The most useful functions to manage tiers of a sppasTranscription object are:

* `create_tier()` to create an empty tier and to append it,
* `append(tier)` to add a tier into the sppasTranscription,
* `pop(index)` to remove a tier of the sppasTranscription,
* `find(name, case_sensitive=True)` to find a tier from its name.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="15"}
for tier in trs:
    # do something with the tier:
    print(tier.get_name())
phons_tier = trs.find("PhonAlign")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

>*Practice:*
>Write a script to select a set of tiers of a file and save them into a new file
>(solution: ex11_transcription.py).


### Manipulating a sppasTier object

A tier is made of a name, a list of annotations, and optionally a controlled
vocabulary and a media. To get the name of a tier, or to fix a new name, the
easier way is to use `tier.get_name()`.
The following block of code allows to get a tier and change its name.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="43"}
# Get the first tier, with index=0
tier = trs[0]
print(tier.get_name())
tier.set_name("NewName")
print(tier.get_name())
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The most useful functions to manage annotations of a `sppasTier` object are:

* `create_annotation(location, labels)` to create and add a new annotation
* `append(annotation)` to add a new annotation at the end of the list
* `add(annotation)` to add a new annotation
* `pop(index)` to delete the annotation of a given index
* `remove(begin, end)` to remove annotations of a given localization range
* `is_disjoint()`, `is_interval()`, `is_point()` to know the type of location
* `is_string()`, `is_int()`, `is_float()`, `is_bool()` to know the type of labels
* `find(begin, end)` to get annotations in a given localization range
* `get_first_point()`, `get_last_point()` to get respectively the point with the lowest or highest localization
* `set_radius(radius)` to fix the same vagueness value to each localization point

>Practice:
>Write a script to open an annotated file and print information about tiers
>(solution: ex12_tiers_info.py)


### Manipulating a sppasAnnotation object

An annotation is a container for a location and optionally a list of labels.
It can be used to manage the labels and tags with the following methods:

* `is_labelled()` returns True if at least a `sppasTag` exists and is not None
* `append_label(label)` to add a label into the list of labels
* `get_labels_best_tag()` returns a list with the best tag of each label
* `add_tag(tag, score, label_index)` to add a tag into a label
* `remove_tag(tag, label_index)` to remove a tag of a label

An annotation object can also be copied with the method `copy()`. The location,
the labels and the metadata are all copied; and the 'id' of the returned
annotation is then the same. It is expected that each annotation of a tier
as its own 'id', but the API doesn't check this.


>*Practice*: Write a script to print information about annotations of a tier
>(solution: ex13_tiers_info.py)

    
    
### Search in annotations: Filters

#### Overview

This section focuses on the problem of *searching and retrieving* data from 
annotated corpora. 

The filter implementation can only be used together with the `sppasTier()` class.
The idea is that each `sppasTier()` can contain a set of filters, that each reduce
the full list of annotations to a subset. 

SPPAS filtering system proposes 2 main axis to filter such data: 

* with a boolean function based either on the content, the duration or on the time of annotations, 
* with a relation function between annotation locations of 2 tiers. 

A set of filters can be created and combined to get the expected result.
To be able to apply filters to a tier, some data must be loaded first. 
First, a new `sppasTranscription()` has to be created when loading a file.
Then, the tier(s) to apply filters on must be fixed. Finally, if the input
file was NOT an XRA, it is widely recommended to fix a radius value before
using a relation filter.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
f = sppasFilter(tier)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a filter is applied, it returns an instance of `sppasAnnSet` which
is the set of annotations matching with the request. It also contains
a 'value' which is the list of functions that are truly matching for each
annotation.
Finally, `sppasAnnSet` objects can be combined with the operators '|' and '&',
and expected to a `sppasTier` instance.


#### Filter on the tag content

The following matching names are proposed to select annotations:

* 'exact': means that a tag is valid if it strictly corresponds to the expected pattern;
* 'contains' means that a tag is valid if it contains the expected pattern;
* 'startswith' means that a tag is valid if it starts with the expected pattern;
* 'endswith' means that a tag is valid if it ends with the expected pattern.
* 'regexp' to define regular expressions.

All these matches can be reversed, to represent does not exactly match, does
not contain, does not start with or does not end with. Moreover, they can be
case-insensitive by adding 'i' at the beginning like 'iexact', etc.
The full list of tag matching functions is obtained by invoking
`sppasTagCompare().get_function_names()`.

The next examples illustrate how to work with such pattern matching filter.
In this example, `f1` is a filter used to get all phonemes with the exact label
'a'. On the other side, `f2` is a filter that ignores all phonemes matching 
with 'a' (mentioned by the symbol '~') with a case insensitive comparison
(iexact means insensitive-exact).

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
tier = trs.find("PhonAlign")
f = sppasFilter(tier)
ann_set_a = f.tag(exact='a')
ann_set_aA = f.tag(iexact='a')
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The next example illustrates how to write a complex request. Notice
that r1 is equal to r2, but getting r1 is faster:


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
tier = trs.find("TokensAlign")
f = sppasFilter(tier)
r1 = f.tag(startswith="pa", not_endswith='a', logic_bool="and")
r2 = f.tag(startswith="pa") & f.tag(not_endswith='a')
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}


With this notation in hands, it is easy to formulate queries like
for example: *Extract words starting by "ch" or "sh"*, like:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
result = f.tag(startswith="ch") | f.tag(startswith="sh")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


>*Practice:*: Write a script to extract phonemes /a/ then phonemes /a/, /e/, /A/ and /E/.
>(solution: ex15_annotation_label_filter.py).


#### Filter on the duration

The following matching names are proposed to select annotations:

* 'lt' means that the duration of the annotation is lower than the given one;
* 'le' means that the duration of the annotation is lower or equal than the given one;
* 'gt' means that the duration of the annotation is greater than the given one;
* 'ge' means that the duration of the annotation is greater or equal than the given one;
* 'eq' means that the duration of the annotation is equal to the given one;
* 'ne' means that the duration of the annotation is not equal to the given one.

The full list of duration matching functions is obtained by invoking
`sppasDurationCompare().get_function_names()`.

Next example shows how to get phonemes during between 30 ms and 70 ms. Notice
that r1 and r2 are equals!

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
tier = trs.find("PhonAlign")
f = sppasFilter(tier)
r1 = f.dur(ge=0.03) & f.dur(le=0.07)
r2 = f.dur(ge=0.03, le=0.07, logic_bool="and")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


>*Practice*: Extract phonemes 'a' or 'e' during more than 100ms
>(solution: ex16_annotation_dur_filter.py).


#### Filter on position in time

The following matching names are proposed to select annotations:

* rangefrom allows to fix the begin time value,
* rangeto allows to fix the end time value.

Next example allows to extract phonemes 'a' of the 5 first seconds:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
tier = trs.find("PhonAlign")
f = sppasFilter(tier)
result = f.tag(exact='a') & f.loc(rangefrom=0., rangeto=5., logic_bool="and")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



#### Creating a relation function

Relations between annotations is crucial if we want to extract multimodal data. 
The aim here is to select intervals of a tier depending on what is represented
in another tier.

James Allen, in 1983, proposed an algebraic framework named Interval
Algebra (IA), for qualitative reasoning with time intervals where the
binary relationship between a pair of intervals is represented  by a
subset of 13 atomic relation, that are:

  - distinct because no pair of definite intervals can be related
  by more than one of the relationships;

  - exhaustive because any pair of definite intervals are described
  by one of the relations;

  - qualitative (rather than quantitative) because no numeric time
  spans are considered.

These relations and the operations on them form "Allen's Interval Algebra".

Pujari, Kumari and Sattar proposed INDU in 1999: an Interval & Duration
network. They extended the IA to model qualitative information about
intervals and durations in a single binary constraint network. Duration
relations are: greater, lower and equal.
INDU comprises of 25 basic relations between a pair of two intervals.

`anndata` implements the 13 Allen interval relations: before, after, meets,
met by, overlaps, overlapped by, starts, started by, finishes, finished by,
contains, during and equals; and it also contains the relations proposed
in the INDU model. The full list of matching functions is obtained by invoking
`sppasIntervalCompare().get_function_names()`.

Moreover, in the implementation of `anndata`, some functions accept
options:

* `before` and `after` accept a `max_delay` value,
* `overlaps` and `overlappedby` accept an `overlap_min` value and a boolean `percent` which defines whether the value is absolute or is a percentage.

The next example returns monosyllabic tokens and tokens that are
overlapping a syllable (only if the overlap is during more than 40 ms):

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
tier = trs.find("TokensAlign")
other_tier = trs.find("Syllables")
f = sppasFilter(tier)
f.rel(other_tier, "equals", "overlaps", "overlappedby", min_overlap=0.04)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Below is another example of implementing a request.
*Which syllables stretch across 2 words?*

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
# Get tiers from a sppasTranscription object
tier_syll = trs.find("Syllables")
tier_toks = trs.find("TokensAlign")
f = sppasFilter(tier_syll)

# Apply the filter with the relation function
ann_set = f.rel(tier_toks, "overlaps", "overlappedby")

# To convert filtered data into a tier:
tier = ann_set.to_tier("SyllStretch")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



>*Practice 1*: Create a script to get tokens followed by a silence.
>(solution: ex17_annotations_relation_filter1.py).
 
>*Practice 2*: Create a script to get tokens preceded by OR followed by a silence.
>(solution: ex17_annotations_relation_filter2.py).
    
>*Practice 3*: Create a script to get tokens preceded by AND followed by a silence.
>(solution: ex17_annotations_relation_filter3.py).


## More with SPPAS...

In addition to *anndata*, SPPAS contains several other API. They are all free and
open source Python libraries, with a documentation and a set of tests.

Among others:

- *audiodata* to manage digital audio data: load, get information, extract channels, re-sample, search for silences, mix channels, etc.
- *calculus* to perform some math on data, including descriptive statistics. 
- *resources* to access and manage linguistic resources like lexicons, dictionaries, etc.
