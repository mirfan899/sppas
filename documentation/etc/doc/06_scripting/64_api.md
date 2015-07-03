## The API of SPPAS to manage data


### Overview

We are now going to write Python scripts with the help of the 
*annotationdata* API included in SPPAS. This API is useful to read/write
and manipulate files annotated from various annotation tools as Praat
or Elan for example.

First of all, it is important to understand the data structure included in
the API to be able to use it efficiently.
Details can be found in the following publication:

> *Brigitte Bigi, Tatsuya Watanabe, Laurent Prévot* (2014).
> **Representing Multimodal Linguistics Annotated data**,
> Proceedings of the 9th edition of the Language Resources and Evaluation Conference, 26-31 May 2014, Reykjavik, Iceland.


### Why developing a new API?

In the Linguistics field, multimodal annotations contain information ranging 
from general linguistic to domain specific information. Some are annotated 
with automatic tools, and some are manually annotated.
Linguistics annotation, especially when dealing with multiple domains, 
makes use of different tools within a given project. 
Many tools and frameworks are available for handling rich media data.
The heterogeneity of such annotations has been recognized as a key problem
limiting the interoperability and re-usability of NLP tools and linguistic
data collections. 

In annotation tools, annotated data are mainly represented in the form of 
"tiers" or "tracks" of annotations. 
The genericity and flexibility of "tiers" is appropriate to represent any 
multimodal annotated data because it simply maps the annotations on the 
timeline.
In most tools, tiers are series of intervals defined by:

* a time point to represent the beginning of the interval;
* a time point to represent the end of the interval;
* a label to represent the annotation itself.

In Praat, tiers can be represented by a time point and a label (such 
tiers are named PointTiers and IntervalTiers).
Of course, depending on the annotation tool, the internal data representation 
and the file formats are different.
For example, in Elan, unlabelled intervals are not represented nor saved. 
On the contrary, in Praat, tiers are made of a succession of consecutive 
intervals (labelled or un-labelled).

The *annotationdata* API used for data representation is based on the 
common set of information all tool are currently sharing. 
This allows to manipulate all data in the same way, regardless of the file 
type. 

The API supports to merge data and annotation from a wide range of
heterogeneous data sources for further analysis.


### The API class diagram

After opening/loading a file, its content is stored in a `Transcription`
object. A `Transcription` has a name, and a list of `Tier` objects.
This list can be empty.
Notice that in a `Transcription`, two tiers can't have the same name.

A `Tier` has a name, and a list of `Annotation` objects. It also contains a 
set of meta-data and it can be associated to a controlled vocabulary.

A common solution to represent annotation schemes is to put them in a tree.
One advantage in representing annotation schemes through those trees,
is that the linguists instantly understand how such a tree works and 
can give a representation of “their” annotation schema. However, each 
annotation tool is using its own formalism and it is unrealistic to be able
to create a generic scheme allowing to map all of them.
SPPAS implements another solution that is compatible with trees and/or flat
structures (as in Praat). 
Actually, subdivision relations can be established between tiers.
For example, a tier with phonemes is a subdivision reference for syllables,
or for tokens, and tokens are a subdivision reference for the orthographic
transcription in IPUs. Such subdivisions can be of two categories:
alignment or constituency.
This data representation allows to keep the Tier representation, which is shared
by most of the annotation tools and it allows too to map data on a tree if
required: the user can freely create tiers with any names and arrange them in 
such custom and very easy hierarchy system.

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
> <http://sldr.org/000800/preview/manual/module-tree.html>


#### Label representation

Each annotation holds at least one label, mainly represented in the form of
a string, freely written by the annotator or selected from a list of 
categories, depending on the annotation tool.
The *"annotationdata"* API, aiming at representing any kind of linguistic 
annotations, allows to assign a score to each label, and allows multiple 
labels for one annotation. The API also allows to define a controlled 
vocabulary.


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
to the radius value (0ms for prosody, 5ms for phonetics, discourse 
and syntax and 40ms for gestures in this screenshot). 

![Example of multimodal data](./etc/screenshots/Grenelle.png)

