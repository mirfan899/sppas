## The API of SPPAS to manage data

In this section, we are going to create Python scripts with the SPPAS 
Application Programming Interface *annotationdata* and then run them. 

### Overview

We are now going to write Python scripts using the *annotationdata* API 
included in SPPAS. This API is useful to read/write and manipulate files
annotated from various annotation tools like SPPAS, Praat or Elan for example.

First of all, it is important to understand the data structure included into
the API to be able to use it efficiently.
Details can be found in the following publication:

> *Brigitte Bigi, Tatsuya Watanabe, Laurent Prévot* (2014).
> **Representing Multimodal Linguistics Annotated data**,
> Proceedings of the 9th edition of the Language Resources and Evaluation Conference, 26-31 May 2014, Reykjavik, Iceland.


### Why developing a new API?

In the Linguistics field, multimodal annotations contain information ranging 
from general linguistic to domain specific information. Some are annotated 
with automatic tools, and some are manually annotated.
In annotation tools, annotated data are mainly represented in the form of 
"tiers" or "tracks" of annotations. Tiers are series of intervals defined by:

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

The *annotationdata* API was designed to be able to manipulate all data in 
the same way, regardless of the file type. 
The API supports to merge data and annotations from a wide range of
heterogeneous data sources.


### The API class diagram

After opening/loading a file, its content is stored in a `Transcription`
object. A `Transcription` has a name, and a list of `Tier` objects.
Two tiers can't share the same name. The list of tiers can be empty.
A hierarchy between tiers can be defined.
Actually, subdivision relations can be established between tiers.
For example, a tier with phonemes is a subdivision reference for syllables,
or for tokens, and tokens are a subdivision reference for the orthographic
transcription in IPUs. Such subdivisions can be of two categories:
alignment or constituency.

A `Tier` has a name, and a list of `Annotation` objects. It also contains a 
set of meta-data and it can be associated to a controlled vocabulary.

An annotation is made of 2 objects:
 
- a `Location` object,
- a `Label` object.

A `Label` object is representing the "content" of the annotation. It is a list
of `Text` associated to a score.

A `Location` is representing where this annotation occurs in the media.
Then, a `Location` is made of a list of `Localization` which includes
the `BasePlacement` associated with a score.
A `BasePlacement` object is one of:

* a `TimePoint` object; or
* a `TimeInterval` object, which is made of 2 `TimePoint` objects; or
* a `TimeDisjoint` object which is a list of `TimeInterval`; or
* a `FramePoint` object; or
* a `FrameInterval` object; or
* a `FrameDisjoint` object.

![API class diagram](./etc/figures/annotationdata.png)

> **The whole API documentation is available at the following URL:**
> <http://www.sppas.org/manual/module-tree.html>


#### Label representation

Each annotation holds at least one label, mainly represented in the form of
a string, freely written by the annotator or selected from a list of 
categories, depending on the annotation tool.
The *annotationdata* API allows to assign a score to each label, and allows 
multiple labels for one annotation. 


#### Location representation

In the *annotationdata* API, a `TimePoint` is considered *as an imprecise 
value*. It is possible to characterize a point in a space immediately allowing 
its vagueness by using:

* a midpoint value (center) of the point;
* a radius value.

![Representation of a TimePoint](./etc/figures/timepoint-represent.png)


#### Example

The screenshot below shows an example of multimodal annotated data, 
imported from 3 different annotation tools. Each `TimePoint` is 
represented by a vertical dark-blue line with a gradient color to refer 
to the radius value.

In the screenshot the following radius values were assigned:

- 0ms for prosody, 
- 5ms for phonetics, discourse and syntax 
- 40ms for gestures. 

![Example of multimodal data](./etc/screenshots/Grenelle.png)

