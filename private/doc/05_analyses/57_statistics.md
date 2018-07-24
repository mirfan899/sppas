## Statistics

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
The length of this context can be optionally changed while fixing the "N-gram"
value (available from 1 to 5), just above the sheets.

Each displayed sheet can be saved as a CSV file, which is a useful file format
to be read by R, Excel, OpenOffice, LibreOffice, and so... To do so, display
the sheet you want to save and click on the button "Save sheet", just below
the sheets. If you plan to open this CSV file with Excel under Windows, it is
recommended to change the encoding to UTF-16. For the other cases, UTF-8 is
probably the most relevant.

The annotation durations are commonly estimated on the Midpoint value,
without taking the radius into account; see (Bigi et al, 2012) for 
explanations about the Midpoint/Radius. Optionally, the duration can
either be estimated by taking the vagueness into account, then check "Add the
radius value" button, or by ignoring the vagueness and estimating only on the
central part of the annotation, then check "Deduct the radius value".

For those who are estimating statistics on XRA files, you can either estimate
stats only on the best label (the label with the higher score) or on all labels,
i.e. the best label and all its alternatives (if any).

![Descriptive statistics](./etc/screenshots/Statistics-descriptives.png)


### User agreement

SPPAS implements the estimation of the Cohen's Kappa.
It is currently limited to the evaluation of this user agreement between 
labels of 2 tiers with the same number of intervals.
It is under-development...
