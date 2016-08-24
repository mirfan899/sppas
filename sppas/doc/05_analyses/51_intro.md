## Introduction

The analysis tools are useful for the analyses of annotated files: display 
the automatic alignments with the audio signal, estimates statistics on the 
annotations, filter the annotated data to get only the annotations you are
interested in, etc.
 
To execute a specific analysis tool, select file(s) in the file explorer of 
the main frame, then click on the button of the tool. It will open the frame, 
and add the file(s) in the file manager of the tool. 

![The analysis tools](./etc/screenshots/CCP.png)

Six tools are available:

1. `DataRoamer` allows to explore the annotated files: cut/copy/paste/rename/duplicate tiers, move a tier from one file to another one, etc. 
2. `AudioRoamer` allows to play and manage audio files: extract a channel, see clipping rates, change framerate, etc.
3. `IPUscriber` is useful to perform manual orthographic transcription.
4. `Vizualizer` displays audio files and annotated files, and is very useful to take a screenshot! Easy way to zoom/scroll, change colours, choose the tiers to display, etc;
5. `DataFilter` allows to select annotations: fix a set of filters to create new tiers with only the annotations you are interested in!
6. `Statistics` estimates the number of occurrences, the duration, etc. of the annotations, and allows to save in CSV (for Excel, OpenOffice, R, MatLab,...).

All of such tools share the same frame with:

- a menu (left), 
- a toolbar (top),
- a list of files,
- a notebook to open files in tabs.
