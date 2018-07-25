## anndata, an API to manage annotated data

### Overview

We are now going to write Python scripts using the *anndata* API
included in SPPAS. This API is useful to read/write and manipulate files
annotated from various annotation tools like SPPAS, Praat or Elan.

First of all, it is important to understand the data structure included into
the API to be able to use it efficiently.


### Why developing a new API?

In the Linguistics field, multimodal annotations contain information ranging 
from general linguistic to domain specific information. Some are annotated 
with automatic tools, and some are manually annotated.
In annotation tools, annotated data are mainly represented in the form of 
"tiers" or "tracks" of annotations. Tiers are mostly series of intervals
defined by:

* a time point to represent the beginning of the interval;
* a time point to represent the end of the interval;
* a label to represent the annotation itself.

Of course, depending on the annotation tool, the internal data representation 
and the file formats are different.
In Praat, tiers can be represented by a time point and a label (such 
tiers are respectively named PointTiers and IntervalTiers).
IntervalTiers are made of a succession of consecutive intervals (labelled or 
un-labelled). In Elan, points are not supported; and unlabelled intervals are 
not represented nor saved.

The *anndata* API was designed to be able to manipulate all data in
the same way, regardless of the file type. It supports to merge data
and annotations from a wide range of heterogeneous data sources.


### The API class diagram

After opening/loading a file, its content is stored in a `sppasTranscription`
object. A `sppasTranscription` has a name, and a list of `sppasTier` objects.
Tiers can't share the same name, the list of tiers can be empty, and
a hierarchy between tiers can be defined.
Actually, subdivision relations can be established between tiers.
For example, a tier with phonemes is a subdivision reference for syllables,
or for tokens; and tokens are a subdivision reference for the orthographic
transcription in IPUs. Such subdivisions can be of two categories:
alignment or association.

A `sppasTier` object has a name, and a list of `sppasAnnotation` objects.
It can also be associated to a controlled vocabulary, or a media.

Al these objects contain a set of meta-data.

An annotation is made of 2 objects:
 
- a `sppasLocation` object,
- a list of `sppasLabel` objects.

A `sppasLabel` object is representing the "content" of the annotation. It is a list
of `sppasTag` each one associated to a score.

A `sppasLocation` is representing where this annotation occurs in the media.
Then, a `sppasLocation` is made of a list of localization each one
associated with a score. A localization is one of:

* a `sppasPoint` object; or
* a `sppasInterval` object, which is made of 2 `sppasPoint` objects; or
* a `sppasDisjoint` object which is a list of `sppasInterval`.

![API class diagram](etc/figures/anndata.png)


#### Label representation

Each annotation holds a serie of 0..N labels, mainly represented in the form
of a string, freely written by the annotator or selected from a list of
categories.


#### Location representation

In the *anndata* API, a `sppasPoint` is considered *as an imprecise
value*. It is possible to characterize a point in a space immediately allowing 
its vagueness by using:

* a midpoint value (center) of the point;
* a radius value.

![Representation of a sppasPoint](etc/figures/timepoint-represent.png)


#### Example

The screenshot below shows an example of multimodal annotated data, 
imported from 3 different annotation tools. Each `sppasPoint` is
represented by a vertical dark-blue line with a gradient color to refer 
to the radius value.

In the screenshot the following radius values were assigned:

- 0ms for prosody, 
- 5ms for phonetics, discourse and syntax 
- 40ms for gestures. 

![Example of multimodal data](etc/screenshots/Grenelle.png)

