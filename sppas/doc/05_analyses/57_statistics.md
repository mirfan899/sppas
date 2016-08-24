## Statistics

`Statistics` allows to get descriptives statistics about a set of selected
tiers and includes TGA (Time Group Analyzer), originaly available at 
<http://wwwhomes.uni-bielefeld.de/gibbon/TGA/>, a tool developped
by Dafydd Gibbon, emeritus professor of English and General Linguistics at
Bielefeld University. 
It also allows to estimate a user agreement rate (Kappa as a first stage).

![Statistics: descriptive statistics and TGA](./etc/screenshots/Statistics.png)


### Descriptive statistics

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

![Descriptive statistics](./etc/screenshots/Statistics-descriptives.png)


### TGA - Time Group Analyzer

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
    

### User agreement

SPPAS integrates the estimation of the Cohen's Kappa.
It is currently limited to the evaluation of this user agreement between 
labels of 2 tiers with the same number of intervals.

