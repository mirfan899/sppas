## Components Panel

The components are useful for the analysis of annotated files: display the
automatic alignments with the audio signal, estimates statistics on the 
annotations, filter the annotated data to get only the annotations you are
interested in, etc.
 
To execute a specific component, select file(s) in the file explorer, then 
click on the button of a component. It will open the component frame, 
and add the selected file(s) in the file manager of the component. 
Refer to the documentation of each component to know how to use it.

![Component Panel (CCP)](./etc/screenshots/CCP.png)

Six components are available:

1. `DataRoamer` allows to explore the annotated files: cut/copy/paste/rename/duplicate tiers, move a tier from one file to another one, etc. 
2. `SndPlayer` allows to play your speech files.
3. `IPUscribe` is useful to perform manual orthographic transcription.
4. `SppasEdit` displays speech files and annotated files, and is very useful to take a screenshot! Easy way to zoom/scroll, change colours, choose the tiers to display, etc;
5. `DataFilter` allows to select annotations: fix a set of filters to create new tiers with only the annotations you are interested in!
6. `Statistics` estimates the number of occurrences, the duration, etc. of the annotations, and allows to save in CSV (for Excel, OpenOffice, R, MatLab,...).

All of the components share the same style:

- a menu, a toolbar
- at left: the list of files
- at right: a notebook to open files in tabs.


### The main toolbar

![The toolbar of the components](./etc/screenshots/components-toolbar.png)

Seven buttons are available:

- Exit: go out of the component;
- Add: add file(s) in the list;
- Remove: remove all un-checked (i.e. un-used) files of the list;
- New tab: open an empty new tab in the notebook;
- Close tab: close the selected tab;
- Settings: the same that the main frame of SPPAS;
- About: get information about the component.


### The list of files

![Components: list of files](./etc/screenshots/components-files.png)

The most important information to know is that when files are added in the 
list, they are not opened: only checked files are loaded.


### DataRoamer

`DataRoamer` displays detailed information about annotated files and allows 
to manage the tiers: cut/copy/paste/rename/duplicate tiers, move a tier from 
one file to another one, etc.

![Component: DataRoamer](./etc/screenshots/DataRoamer.png)


### SndRoamer

`SndRoamer` allows to play your speech files and to get information.

![Component: SndRoamer](./etc/screenshots/SndRoamer.png)


### IPUscribe

`IPUscribe` is useful to perform manual orthographic transcription.

![Component: IPUTranscriber](./etc/screenshots/IPUscribe.png)

To transcribe an IPU, click on the IPU box, play sound and write 
the corresponding text: refer to the transcription convention of 
this document.
To manage sound, use green buttons just at the bottom of the IPUs 
list (from left to right):

- information about the file
- play sound
- auto-play sound
- pause
- stop

The following keyboard shortcuts can also be used:

- to play: TAB
- to pause: ESC
- to stop: F1


### SppasEdit

This component is still under-development, some "troubles/crashes" can occur 
while using it... but the data will never been corrupted!!

`DataViewer` displays speech files and annotated files, and is very useful 
to take a nice screenshot! 
Most of the screenshots of annotated data of this document were taken with it...

Try the `Demo` of this component: 
easy way to zoom/scroll, change colours, choose the tiers to display, etc! 

![Component: SppasEdit](./etc/screenshots/SppasEdit.png)


### DataFilter

`DataFilter` allows to select annotations: fix a set of filters to create new 
tiers with only the annotations you are interested in!
This system is based on the creation of 2 different types of filters:

1. single filters, i.e. search in a/several tier(s) depending on the data content, the time values or the duration of each annotation;
2. relation filters, i.e. search on annotations of a/several tier(s) in time-relation with annotations of another one.

These later are applied on tiers of many kind of input files (TextGrid, eaf,
trs, csv...). The filtering process results in a new tier, that can re-filtered
and so on.

![Component: DataFilter](./etc/screenshots/DataFilter.png)


#### Filtering annotations of a tier: SingleFilter

Pattern selection is an important part to extract data of a corpus and is
obviously and important part of any filtering system. Thus, if the label
of an annotation is a string, the following filters are proposed in DataFilter:

- exact match: an annotation is selected if its label strictly corresponds to the given pattern;
- contains:    an annotation is selected if its label contains the given pattern;
- starts with: an annotation is selected if its label starts with the given pattern;
- ends with:   an annotation is selected if its label ends with the given pattern.

All these matches can be reversed to represent respectively: 
does not exactly match, does not contain, does not start with or does not end with.
Moreover, this pattern matching can be case sensitive or not.

For complex search, a selection based on regular expressions is available for 
advanced users.

A multiple pattern selection can be expressed in both ways:

- enter multiple patterns at the same time (separated by commas) 
to mention the system to retrieve either one pattern or the other, etc.
- enter one pattern at a time and choose the appropriate button: "Apply All" or "Apply any".

![Frame to create a filter on annotation labels. In that case, filtering annotations that exactly match either a, @ or E](./etc/screenshots/DataFilter-label.png)

Another important feature for a filtering system is the possibility to retrieve 
annotated data of a certain duration, and in a certain range of time in the
timeline.

![Frame to create a filter on annotation durations. In that case, filtering annotations that are during more that 80 ms](./etc/screenshots/DataFilter-duration.png)

Search can also starts and/or ends at specific time values in a tier.

![Frame to create a filter on annotation time values. In that case, filtering annotations that are starting after the 5th minute.](./etc/screenshots/DataFilter-time.png)



All the given filters are then summarized in the "SingleFilter" frame.
To complete the filtering process, it must be clicked on one of the apply
buttons and the new resulting tiers are added in the annotation file(s).

In the given example:

- click on "Apply All" to get either a, @ or E vowels during more than 80ms, after the 5th minute.
- click on "Apply Any" to get a, @ or E vowels, and all annotations during more than 80 ms, and all annotations after the 5th minute.


![DataFilter: SingleFilter frame](./etc/screenshots/DataFilter-single.png)



#### Filtering on time-relations between two tiers


Regarding the searching problem, linguists are typically interested in
locating patterns on specific tiers, with the possibility to relate
different annotations a tier from another.
The proposed system offers a powerful way to request/extract data, with the 
help of Allen's interval algebra.

In 1983 James F. Allen published a paper in which he proposed 13 basic
relations between time intervals that are distinct, exhaustive, and
qualitative:

- distinct because no pair of definite intervals can be related 
  by more than one of the relationships;
- exhaustive because any pair of definite intervals are described 
  by one of the relations;
- qualitative (rather than quantitative) because no numeric time 
  spans are considered.

These relations and the operations on them form Allen's interval algebra. 
These relations were extended to Interval-Tiers as Point-Tiers to be used
to find/select/filter annotations of any kind of time-aligned tiers.

For the sake of simplicity, only the 13 relations of the Allen's algebra are 
available in the GUI. But actually, we implemented the 25 relations proposed 
Pujari and al. (1999) in the INDU model. This model is fixing constraints on 
INtervals (with Allen's relations) and on DUration (duration are equals, one 
is less/greater than the other). Such relations are available while requesting
with Python.

At a first stage, the user must select the tiers to be filtered and click
on "RelationFilter". The second stage is to select the tier that will be
used for time-relations.

![Fix time-relation tier name](./etc/screenshots/DataFilter-relationY.png)

The next step consists in checking the Allen's relations that will be applied.
The last stage is to fix the name of the resulting tier.
The above screenshots illustrates how to select the first phoneme of each token,
except for tokens that are containing only one phoneme (in this later case, the
"equal" relation should be checked).

![DataFilter: RelationFilter frame](./etc/screenshots/DataFilter-relation.png)

To complete the filtering process, it must be clicked on the "Apply" button
and the new resulting tiers are added in the annotation file(s). 



### Statistics

`Statistics` allows to get descriptives statistics about a set of selected
tiers. It also allows to estimate a user agreement rate (Kappa as a
first stage) and includes TGA (Time Group Analyzer), originaly available at 
<http://wwwhomes.uni-bielefeld.de/gibbon/TGA/>, a tool developped
by Dafydd Gibbon, emeritus professor of English and General Linguistics at
Bielefeld University. 

![Component: Statistics](./etc/screenshots/Statistics.png)


#### Descriptive statistics

It allows to estimate the number of occurrences, the duration, etc. of the 
annotations of a set of selected tiers, and allows to save in CSV
(for Excel, OpenOffice, R, MatLab,...).
It offers a serie of sheets organized in a notebook. The first tab is
displaying a summary of descriptive statistics of the set of given tiers.
The other tabs are indicating one of the statistics over the given tiers.
The followings are estimated:

- occurrences: the number of observations
- total durations: the sum of the durations 
- mean durations: the arithmetic mean of the duration 
- median durations: the median value of the distribution of durations 
- std dev. durations: the standard deviation value of the distribution of durations 

All of them can be estimated on a single annotation label or on a serie of them.
The lengh of this context can be optionally changed while fixing the "N-gram"
value (available from 1 to 5), just above the sheets.

Each displayed sheet can be saved as a CSV file, which is a useful file format
to be read by R, Excel, OpenOffice, LibreOffice, and so... To do so, display
the sheet you want to save and click on the button "Save sheet", just below
the sheets. If you plan to open this CSV file with Excel under Windows, it is
recommended to change the encoding to UTF-16. For the other cases, UTF-8 is
probably the most relevant.

The annotation durations are commonly estimated on the Midpoint value,
without taking the radius into account; see (Bigi et al, 2012) for 
explanations about the Midpoint/Radius. Optionnally, the duration can
either be estimated by taking the vagueness into account, then check "Add the
radius value" button, or by ignoring the vagueness and estimating only on the
central part of the annotation, then check "Deduct the radius value".

For those who are estimating statistics on XRA files, you can either estimate
stats only on the best label (the label with the higher score) or on all labels,
i.e. the best label and all its alternatives (if any).

![Component: Statistics](./etc/screenshots/Statistics-descriptives.png)


#### User agreement

SPPAS integrates the estimation of the Cohen's Kappa.
It is currently limited to the evaluation of this user agreement between labels 
of 2 tiers with the same number of intervals.



#### TGA - Time Group Analyzer

>*Dafydd Gibbon* (2013).
>**TGA: a web tool for Time Group Analysis**,
> Tools ans Resources for the Analysis of Speech Prosody, Aix-en-Provence, France, pp. 66-69.

The  TGA   is   an   online   batch   processing   tool  which
provides  a  parametrised  mapping  from  time-stamps  in
speech annotation files in various formats to a detailed
analysis   report   with   statistics   and   visualisations. 
TGA software calculates, inter alia, mean, median, rPVI, nPVI, slope and 
intercept functions within interpausal groups, provides visualisations of
timing patterns, as well as correlations between these, and parses interpausal 
groups into hierarchies based on duration relations.
Linear regression is selected mainly for the slope function, as a first 
approximation to examining acceleration and deceleration over large data sets.

The   TGA   online   tool   was   designed   to   support
phoneticians   in   basic   statistical   analysis   of   annotated
speech data. In practice, the tool provides not only rapid
analyses but also the ability to handle larger data sets than
can be handled manually.


>*Katarzyna Klessa, Dafydd Gibbon* (2014).
>**Annotation Pro + TGA: automation of speech timing analysis**,
>9th International conference on Language Resources and Evaluation (LREC), Reykjavik (Iceland). pp. 1499-1505, ISBN: 978-2-9517408-8-4.

The integrated  Annotation Pro + TGA tool incorporates some TGA features  and
is   intended   to   support   the development of more robust and versatile 
timing models for a greater variety of data.

The   integration   of  TGA  statistical   and   visualisation functions into 
Annotation Pro+TGA results in a powerful computational   enhancement   of  the  
existing  AnnotationPro  phonetic workbench,   for   supporting   experimental
analysis   and   modelling   of   speech   timing.


So... What's the novelty...

TGA is partly implemented in SPPAS.
The Statistics component of SPPAS allows to estimates TGA within the SPPAS 
framework. It results in the following advantages:

- it can read either TextGrid, csv, Elan, HTK, or Sclite, or any file format supported by SPPAS,
- it can save TGA results either as a table in a CSV file or as an annotation file (of any of the format supported by SPPAS),
- it estimates 2 linear regressions (the y-axis is the duration in both cases):

    1. with x-axis based on positions, like in the inline TGA
    2. with x-axis based on time-stamps, like in the AnnotationPro+TGA
    
