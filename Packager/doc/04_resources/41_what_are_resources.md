## What are resources and where they come from?

### Overview

Automatic annotations included in SPPAS are implemented with
language-independent algorithms. This means that adding a new language
in SPPAS only consists in adding resources related to the annotation
(like lexicons, dictionaries, models, set of rules, etc).

> All resources can be edited, modified, changed or deleted by users.

To know what the resources are for and other information, refer to 
chapter 3 of this documentation: Each resource is used by an 
automatic annotation.

The resources are language dependent and the name of the files are based on 
the ISO639-3 international standard. See <http://www-01.sil.org/iso639-3/> 
for the list of all languages and codes.

In the next sections, the table indicates the list of phonemes that are 
included in the resources required for phonetization, alignment and 
syllabification of a given language. The first column represents the symbols
used by SPPAS and the two other columns are intended to help users to better
understand what it means.


### New language support

Refer to the description of each annotation in chapter 3.

While starting SPPAS, the Graphical User Interface dynamically creates the 
list of available languages of each annotation by exploring the related folder.
This means that:
* appended resources are automatically taken into account (no need to modify the program itself);
* SPPAS needs to be re-started if new resources are appended while it was already running.
