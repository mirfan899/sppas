## Automatic Annotations

### Description

The Automatic Annotations Panel (AAP) consists of a list of buttons to check 
(the left column), the annotation name (middle) and buttons to fix the 
language of each annotation (at right).

![Automatic Annotations Panel (AAP)](./etc/screenshots/AAP.png)


### AAP Usage

>Remark: to understand what each annotation is for, please refer to 
>the chapter "Automatic Speech Segmentation and Annotation" of this document.

1. Select each annotation to perform. 
Each annotation can be configured by clicking on the annotation name.

2. Select the language for all annotations, or for each one independently by 
clicking on the "chains" button.

3. Click on the *Annotate* button... and wait! Please, wait! Particularly for
Tokenization or Phonetization: loading resources (lexicons or dictionaries) is
very long. Sometimes, the progress bar does not really "progress"...it depends
on the system. So, just wait!

4. It is important **to read the Procedure Outcome report** to check that 
everything happened normally during the automatic process.


### The procedure outcome report

It is very important to read conscientiously this report: it mentions 
exactly what happened during the automatic annotation process.
This text can be saved: it is recommended to be kept it with the related data
because it contains information that are interesting to know for anyone using
the annotations!

The text first indicates the version of SPPAS that was used. This information is 
very important, mainly because annotations in SPPAS and their related resources
are regularly improved and then, the result of the automatic process can change
from one version to the other one.

Secondly, the text mentions information related to the given input: 

1. the selected language of each annotation, only if the annotation is 
language-dependent). For some language-dependent annotations, SPPAS can 
still perform the annotation even if the resources for a given language are 
not available: in that case, select "und", which is the iso639-3 code for
"undetermined".
2. the list of files to be annotated; 
3. the list of annotations and if each annotation was activated or disabled. 
In that case, activated means that the checkbox of the AAP was checked by the 
user and that the resources are available for the given language. On the 
contrary, disabled means that either the checkbox of the AAP was not checked 
or the required resources are not available.

In the following, each automatic annotation is described in details, for each
annotated file. Three levels of information must draw your attention:

1. "[   OK    ]" means that everything happened normally. The annotation was 
performed successfully.
2. "[ WARNING ]" means that something happened abnormally, but SPPAS found
a solution, and the annotation was still performed successfully.
3. "[  ERROR  ]" means that something happened abnormally, and SPPAS failed to
found a solution. The annotation was either not performed, or performed with
a bad result.

Finally, the "Result statistics" section mentions the number of files that was
annotated for each step, or -1 if the annotation was disabled. 

![Procedure outcome report](./etc/screenshots/log.png)
