## What is SPPAS?

### Main features

**SPPAS - the automatic annotation and analyses of speech** is a scientific 
computer software package written and maintained by Brigitte Bigi of
the Laboratoire Parole et Langage, in Aix-en-Provence, France.

Available for free, with open source code, there is simply no other package
for linguists to simple use in automatic segmentation of speech.
SPPAS is daily developed with the aim to provide a robust and reliable
software for the automatic annotation and for the analyses of
annotated-data.

As the primary functionality, SPPAS proposes a set of automatic or 
semi-automatic annotations of recordings. 
Corpus annotation "can be defined as the practice of adding interpretative, 
linguistic information to an electronic corpus of spoken and/or written 
language data. 'Annotation' can also refer to the end-product of this process"
(Leech, 1997). The annotation of recordings is concerned by many Linguistics 
sub-fields as Phonetics, Prosody, Gestures or Discourse... 
Corpora are annotated with detailed information at various linguistic levels 
thanks to annotation software. As large multimodal corpora become prevalent, 
new annotation and analysis requirements are emerging. The annotations must 
be time-synchronized: annotations need to be time-aligned in order to be
useful for purposes such as qualitative or quantitative analyses. Temporal 
information makes it possible to describe behaviors from different subjects 
that happen at the same time, and time-analysis of multi-level annotations 
can reveal Linguistic structures.
In the past, studies was mostly based on limited data. In current trends, 
it is expected that models have to be built on the acoustic analysis of 
large quantity of speech data with valid statistical analyses.
Annotating is very labor-intensive and cost-ineffective since it 
has to be performed manually by experienced researchers with many hours 
of work. SPPAS can automatize annotations and allows users to save time.
In order to use efficiently this automatic annotation software, a 
rigorous methodology to collect data and to prepare them is expected.
This implies a rigorous framework to ensure compatibilities between 
annotations and time-saving. 
The expected result is time-aligned data, for all annotated levels.

Indeed, "when multiple annotations are integrated into a single data set, 
inter-relationships between the annotations can be explored both qualitatively
(by using database queries that combine levels) and quantitatively 
(by running statistical analyses or machine learning algorithms)" 
(Chiarcos 2008). 
Some special features are also offered in SPPAS for managing corpora of 
annotated files; particularly, it includes a tool to filter multi-levels 
annotations (Bigi and Saubesty, 2015). Some other tools are dedicated to 
the analysis of time-aligned data; as for example to estimate descriptive 
statistics, and a version of the Time Group Analyzer (Gibbon 2013), etc. 

Linguistics annotation, especially when dealing with multiple domains, 
makes use of different tools within a given project. 
In recent years, many annotation software/tools have become available for 
annotation of audio-video data. For a researcher looking for an annotation 
software, it is difficult to select the most appropriate. 
Due to the diversity of linguistic phenomena, annotation tools lead to a 
variety of models, theories and formalisms. This diversity results in 
heterogeneous  description formats, each tool developing its own framework.
The choice of all annotation software is part of the annotation framework 
and must be done carefully and of course before the creation of the corpus. 
SPPAS annotation files are in a specific XML format (xra). Annotations 
can be imported from and exported to a variety of other formats, including 
Praat (TextGrid, PitchTier, IntensityTier), Elan (eaf), Transcriber (trs), 
Annotation Pro (antx), Phonedit (mrk), Sclite (ctm, stm), HTK (lab, mlf), 
subtitles formats (srt, sub) and CSV files. 

Automatic annotations can be used either with a Command-line User Interface 
or a Graphical User Interface. So, there's no specific difficulty by using 
this software. Advanced users can also access directly the Application 
Programming Interface.
The program was implemented using the programming language Python 2.7.
The only potential brake on the usage of automatic annotations of SPPAS is 
the need to integrate it in a rigorous methodology for the corpus construction,
annotations and analyses.

Data analysis of SPPAS are mainly proposed in the Graphical User Interface.
However, advanced users can also access directly the Application 
Programming Interface, for example to estimate statistics or to manipulate
annotated data.


### Copyright and Licenses

*(c) 2011-2016 Brigitte Bigi, Laboratoire Parole et Langage, Aix-en-Provence, France*

SPPAS software is distributed under the terms of the **GNU GENERAL PUBLIC
LICENSE**.

SPPAS resources are distributed:

- under the terms of the "GNU GENERAL PUBLIC LICENSE", or
- on the terms of the "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License".

A copy of both licenses is available in the package.
See the "Resources" chapter for details about the license of each proposed
resource.


### User engagement: how to cite SPPAS

>By using SPPAS, **you agree to cite the reference in your publications**.

See the "References" chapter of this documentation to get the list or
the home page <http://www.lpl-aix.fr/~bigi/> to get printable versions
of the references.


### Need help

1. When looking for more detail about some subject, one can search this
documentation. This documentation is available in-line (see the SPPAS website),
it is also included in the package (in PDF format) and it can also be explored
with the Graphical User Interface by clicking on the 'Help' button.

2. Many problems can be solved by updating the version of SPPAS.

3. There is a SPPAS Users discussion group where queries and allied topics
are discussed, with responses from colleagues or from the author.
Topics can range from elementary "how do I" queries to advanced
issues in scriptwriting.
There's (or there will be) something there for everybody.
It is recommended to sign up to become a member on the website:
<https://groups.google.com/forum/#!forum/sppas-users>
(neither spam or e-mails will be sent directly to members).

4. If none of the above helps, you may send e-mail to the author.
It is very important to indicate clearly:

    1/ your operating system and its version,
    2/ the version of SPPAS (supposed to be the last one), and
    3/ for automatic annotations, send the log file, and a sample of the data
    on which a problem occurs.

And/Or, if you have any question, if you want to contribute to SPPAS either
to improve the quality of resources or to help in development, or anything else,
contact the author by e-mail.


### Supports


#### 2011-2012:

Partly supported by ANR OTIM project (Ref. Nr. ANR-08-BLAN-0239),
Tools for Multimodal Information Processing.
Read more at: <http://www.lpl-aix.fr/~otim/>


#### 2013-2015:

Partly supported by ORTOLANG (Ref. Nr. ANR-11-EQPX-0032) funded by the
« Investissements d'Avenir » French Government program managed by the
French National Research Agency (ANR).
Read more at: <http://www.ortolang.fr/>


#### 2014-2015:

SPPAS is also partly carried out thanks to the support of the
following projects or groups:

- CoFee - Conversational Feedback <http://cofee.hypotheses.org>
- Variamu - Variations in Action: a MUltilingual approach <http://variamu.hypotheses.org>
- Team C3i of LPL <http://www.lpl-aix.fr/~c3i>
- Campus France, Procore PHC.


### Contributors

Here is the list of contributors:

* Since January 2011: **Brigitte Bigi** is the main author;
* April 2012-June 2012: Alexandre Ranson;
* April 2012-July 2012: Cazembé Henry;
* April 2012-June 2013: Bastien Herbaut;
* March 2013-March 2014: Tatsuya Watanabe;
* April 2015-June 2015: Nicolas Chazeau;
* April 2015-June 2015: Jibril Saffi.
