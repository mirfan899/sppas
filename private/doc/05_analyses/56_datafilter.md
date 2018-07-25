## DataFilter

`DataFilter` allows to select annotations: define a set of filters to create new 
tiers with only the annotations you are interested in!
This system is based on the creation of 2 different types of filters:

1. single filters, i.e. search in a/several tier(s) depending on the data content, the time values or the duration of each annotation;
2. relation filters, i.e. search on annotations of a/several tier(s) in time-relation with annotations of another one.

These later are applied on tiers of many kind of input files (TextGrid, eaf,
trs, csv...). The filtering process results in a new tier, that can re-filtered
and so on.

![DataFilter: select annotations](etc/screenshots/DataFilter.png)


### Filtering annotations of a tier: SingleFilter

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

![Frame to create a filter on annotation labels. In that case, filtering annotations that exactly match either a, @ or E](etc/screenshots/DataFilter-label.png)

Another important feature for a filtering system is the possibility to retrieve 
annotated data of a certain duration, and in a certain range of time in the
timeline.

![Frame to create a filter on annotation durations. In that case, filtering annotations that are during more that 80 ms](etc/screenshots/DataFilter-duration.png)

Search can also starts and/or ends at specific time values in a tier.

![Frame to create a filter on annotation time values. In that case, filtering annotations that are starting after the 5th minute.](etc/screenshots/DataFilter-time.png)


All the given filters are then summarized in the "SingleFilter" frame.
To complete the filtering process, it must be clicked on one of the apply
buttons and the new resulting tiers are added in the annotation file(s).

In the given example:

- click on "Apply All" to get either a, @ or E vowels during more than 80ms, after the 5th minute.
- click on "Apply Any" to get a, @ or E vowels, and all annotations during more than 80 ms, and all annotations after the 5th minute.


![DataFilter: SingleFilter frame](etc/screenshots/DataFilter-single.png)



### Filtering on time-relations between two tiers


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

![Fix time-relation tier name](etc/screenshots/DataFilter-relationY.png)

The next step consists in checking the Allen's relations that will be applied.
The last stage is to fix the name of the resulting tier.
The above screenshots illustrates how to select the first phoneme of each token,
except for tokens that are containing only one phoneme (in this later case, the
"equal" relation should be checked).

![DataFilter: RelationFilter frame](etc/screenshots/DataFilter-relation.png)

To complete the filtering process, it must be clicked on the "Apply" button
and the new resulting tiers are added in the annotation file(s). 
