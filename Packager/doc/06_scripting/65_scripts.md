## Creating scripts with the SPPAS API


### Preparing the data

If it is not already done, create a new folder (on your Desktop for example); 
you can name it "pythonscripts" for example.

Open a File Explorer window and go to the SPPAS folder location.
Then, open the `sppas` directory then `src` sub-directory. 
Copy the `annotationdata` folder then paste-it into the newly created 
`pythonscripts` folder.

Open the python IDLE and create a new empty file.
Copy the following code in this newly created file, then save 
the file in the pythonscripts folder. By convention, Python source files 
end with a .py extension; I suggest skeleton-sppas.py.
It will allow to use the SPPAS API in your script.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
# ----------------------------------------------------------------------------
# Author: Me
# Date:   Today
# Brief:  Script using the SPPAS API
# ----------------------------------------------------------------------------

import os
import sys

# Get SPPAS API
import sppas.src.annotationdata.aio as aio
from sppas.src.annotationdata import Transcription
from sppas.src.annotationdata import Tier
from sppas.src.annotationdata import Annotation
from sppas.src.annotationdata import Label
from sppas.src.annotationdata import TimePoint
from sppas.src.annotationdata import TimeInterval
from sppas.src.annotationdata import Bool, Rel

# ----------------------------------------------------------------------------

def main():
    """ This is the main function. """
    pass

# ----------------------------------------------------------------------------
# This is the python entry point:
# Here, we just ask to execute the main function.
if __name__ == '__main__':
    main()
# ----------------------------------------------------------------------------
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

Navigate to the folder containing your script, and open-it with
the python IDLE. To execute the file:

* Menu: "Run", then "Run module"
* Keyboard: F5

It will do... nothing! But now, we are ready to do something with the API!


### Read/Write annotated files

Open/Read a file of any format (TextGrid, Elan, Transcriber, ...) and 
store it into a `Transcription` object instance, named `trs` in the
following code, is mainly done as:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
trs = aio.read(filename_in)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Save/Write a `Transcription` object instance in a file of any format 
is mainly done as:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="2"}
aio.write(filename_out, trs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These two lines of code loads any annotation file (Elan, Praat, Transcriber...)
and writes the data into another file.
The format of the file is given by its extension, as for example ".xra" is 
the SPPAS native format, ".TextGrid" is one of the Praat native format, 
and so on.

So... only both lines are used to convert a file from one format to another one!

In any script, to get the list of accepted extensions as input, just call 
"annotationdata.io.extensions_in", and the list of accepted extensions as 
output is "annotationdata.io.extensions_out".

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

>Practice:
>Write a script to convert a TextGrid file into CSV
>(solution: 10_read_write.py)


### Manipulating a Transcription object

The most useful functions used to manage a Transcription object are:

* `Append(tier)`, `Pop()`
* `Add(tier, index)`, `Remove(index)`
* `Find(name, case_sensitive=True)`

`Append()` is used to add a tier at the end of the list of tiers of the 
Transcription object; and `Pop()` is used to remove the last tier of such list.

`Add()` and `Remove()` do the same, except that it does not put/delete the tier 
at the end of the list but at the given index.

`Find()` is useful to get a tier of the list from its name.

There are useful "shortcuts" that can be used. 
For example, `trs[0]` returns the first tier, 
`len(trs)` returns the number of tiers and loops can be written as:


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="15"}
for tier in trs:
    # do something with the tier
    print(tier.GetName())
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

>Practice:
>Write a script to select a set of tiers of a file and save them into a new file
>(solution: 11_transcription.py).


### Manipulating a Tier object

As it was already said, a tier is made of a name and a list of annotations.
To get the name of a tier, or to fix a new name, the easier way is to
use tier.GetName(). 

Test the following code into a script:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="15"}
trs = aio.read(filename)
tier = trs[0]
print(tier.GetName())
tier.SetName("toto")
print(tier.GetName())
print(trs[0].GetName())
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

The most useful functions used to manage a Tier object are:

* `Append(annotation)`, `Pop()`
* `Add(annotation)`, `Remove(begin, end, overlaps=False)`
* `IsDisjoint()`, `IsInterval()`, `IsPoint()`
* `Find(begin, end, overlaps=True)`
* `Near(time, direction)`
* `SetRadius(radius)`

>Practice:
>Write a script to open an annotated file and print information about tiers
>(solution: 12_tiers_info.py)


**Goodies:**
 
the file `12_tiers_info_wx.py` proposes a GUI to print information of one 
file or all files of a directory, and to ask the file/directory name with a 
dialogue frame, instead of fixing it in the script. This script can be executed 
simply by double-clicking on it in the File Explorer of your system.
Many functions of this script can be cut/pasted in any other script.


### Main information on Annotation/Location/Label objects

The most useful function used to manage an Annotation object are:

* `IsSilence()`, `IsLabel()`
* `IsPoint()`, `IsInterval()`, `IsDisjoint()`
* `GetBegin()`, `SetBegin(time)`, only if time is a TimeInterval
* `GetEnd()`, `SetEnd(time)`, only if time is a TimeInterval
* `GetPoint()`, `SetPoint(time)`, only if time is a TimePoint

The following example shows how to get/set a new label, and to set a new time 
to an annotation:

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
This means that the program will stop (except if the program "raises" the 
exception).


### Exercises


>Exercise 1:
>Write a script to print information about annotations of a tier
>(solution: 13_tiers_info.py)

>Exercise 2:
>Write a script to estimates the frequency of a specific annotation label in a file/corpus
>(solution: 14_freq.py)

    
    
### Search in annotations: Filters

####Overview

This section focuses on the problem of *searching and retrieving* data from 
annotated corpora. 

The filter implementation can only be used together with the `Tier()` class. 
The idea is that each `Tier()` can contain a set of filters, that each reduce 
the full list of annotations to a subset. 

SPPAS filtering system proposes 2 main axis to filter such data: 

* with a boolean function, based on the content, or on the time, 
* with a relation function between intervals of 2 tiers. 

A set of filters can be created and combined to get the expected result, 
with the help of the boolean function and the relation function.

To be able to apply filters to a tier, some data must be loaded first. 
First, you have to create a new `Transcription()` when loading a file.
In the next step, you have to select the tier to apply filters on. Then,
if the input file was not XRA, it is widely recommended to fix a radius 
value depending on the annotation type. Now everything is ready to create 
filters for these data. 


####Creating a boolean function

In the following, let `Bool` and `Rel` two predicates, 
a tier `T`, and a filter `f`.

Pattern selection is an important part to extract data of a corpus. In this 
case, each filter consists of search terms for each of the tiers 
that were loaded from an input file. 
Thus, the following matching predicates are proposed to select annotations
(intervals or points) depending on their label. Notice that `P` 
represents the text pattern to find:

* exact match: `pr = Bool(exact=P)`, means that a label is valid if it strictly corresponds to the expected pattern;
* contains: `pr = Bool(contains=P)`, means that a label is valid if it contains the expected pattern;
* starts with, `pr = Bool(startswith=P)`, means that a label is valid if itstarts with the expected pattern;
* ends with, `pr = Bool(endswith=P)`, means that a label is valid if it ends with the expected pattern.

These predicates are then used while creating a filter on labels.
All these matches can be reversed, to represent does not exactly match, 
does not contain, does not start with or does not end with, as for example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
tier = trs.Find("PhonAlign")
ft = Filter(tier)
f1 = LabelFilter(Bool(exact='a'), ft)
f2 = LabelFilter(~Bool(iexact='a'), ft)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example, `f1` is a filter used to get all phonemes with the exact label
'a'. On the other side, `f2` is a filter that ignores all phonemes matching 
with 'a' (mentioned by the symbol '~') with a case insensitive comparison
(iexact means insensitive-exact).

For complex search, a selection based on regular expressions is available 
for advanced users, as `pr = Bool(regexp=R)`.

A multiple pattern selection can be expressed with the operators
`|` to represent the logical "or" and the operator `&` to represent 
the logical "and".

With this notation in hands, it is possible to formulate queries as, 
for example: *Extract words starting by "ch" or "sh"*, as:

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

The, the user must apply the filter to get filtered data from the filter.

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


    
####Creating a relation function

Relations between annotations is crucial if we want to extract multimodal data. 
The aim here is to select intervals of a tier depending on what is represented
in another tier.

We implemented the 13 Allen interval relations: before, after, meets, met by, 
overlaps, overlapped by, starts, started by, finishes, finished by, contains,
during and equals.
Actually, we implemented the 25 relations proposed in the INDU model.
This model is fixing constraints on INtervals (with Allen's relations) and 
on DUration (duration are equals, one is less/greater than the other).


![List of Allen interval relations]<./etc/screenshots/allen.png>


Below is an example of request: 
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


###Exercises


>Exercise 1: Create a script to filter annotated data on their label
>(solution: 15_annotation_label_filter.py).

>Exercise 2: Idem with a filter on duration or time.
>(solution: 16_annotation_time_filter.py).

>Exercise 3: Create a script to get tokens followed by a silence.
>(solution: 17_annotations_relation_filter1.py).
 
>Exercise 4: Create a script to get tokens preceded by OR followed by a silence.
>(solution: 17_annotations_relation_filter2.py).
    
>Exercise 5: Create a script to get tokens preceded by AND followed by a silence.
>(solution: 17_annotations_relation_filter3.py).
    
