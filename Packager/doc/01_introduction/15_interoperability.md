## Interoperability and compatibility


In the scope of the compatibility between SPPAS data and annotated data from
other software tools or programs, SPPAS is able to open/save and convert
files.
The conversion of a file to another file is the process of changing the form 
of the presentation of the data, and not the data itself. Every time, when 
data file is to be used, they must be converted to a readable format for 
the next application. A data conversion is normally an automated process 
to some extent. 
SPPAS provide the possibility to automatically import and export the work 
done on some various file formats from a wide range of other software tools.
For the users, the visible change will be only a different file extension but
for software it is the difference between understanding of the contents of 
the file and the inability to read it. 

The conversion of file formats is then a difficult task and it can imply that
some data are left.
Representing annotated data in SPPAS is of crucial importance for its 
automatic annotations, its analysis of annotations and for the software 
to be able to automatically annotate and analyze any kind of data files. 
SPPAS then includes an original and generic enough annotation representation 
framework. This framework for annotations is very rich and contain several 
information like alternative labels or alternative localizations of annotations,
a tier hierarchy, controlled vocabularies, etc. 
A native format named XRA was then developed to fit in such data 
representation. The physical level of representation of XRA obviously makes 
use of XML, XML-related standards and stand-off annotation. Due to an 
intuitive naming convention, XRA documents are human readable as far as 
possible within the limits of XML. 

SPPAS makes use of its internal data representation to convert files. 
A conversion then consists of two steps: First, the incoming file is loaded 
and mapped to the SPPAS data framework; and second, such data is saved to 
the expected format. These two steps are applied whatever the organization 
structure of annotations in the original or in the destination file format.
This process allows SPPAS to import from and export to a variety of file 
formats. This is illustrated by the next Figure which includes the list of
file formats and the corresponding software that are supported. Arrows are
representing the following actions:
* import from, represented by a continued line with an arrow from the file format to the SPPAS framework;
* partially import from, represented by a dash line with an arrow from the file format to the SPPAS framework;
* export to, represented by an arrow from the SPPAS framework to the file format.

![SPPAS conversion method and formats](./etc/figures/sppas-formats.png)

To summarize, SPPAS supports the following software with their file extensions:

* Praat: TextGrid, PitchTier, IntensityTier
* Elan: eaf
* Annotation Pro: antx
* Phonedit: mrk
* Sclite: ctm, stm
* HTK: lab, mlf
* Subtitles: srt, sub
* Signaix: hz
* Spreadsheets, R,...: csv
* Audacity, notepads: txt

And the followings can be imported:

* ANVIL: anvil
* Transcriber: trs
* Xtrans: tdf

The support of external formats is regularly extended to new formats by the 
author on-demand from the users and distributed to the community in the SPPAS
regular updates.
