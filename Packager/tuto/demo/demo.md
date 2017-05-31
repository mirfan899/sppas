# SPPAS full demonstration

-----------------------------

## Install SPPAS

* Unzip in a directory of your computer

![](./etc/screencasts/sppas-install.mp4)

-----------------

### Install SPPAS

* Right-click on the SPPAS package
* Click on "Extract All"
* Choose the folder where to install SPPAS
* That's it. SPPAS is installed!

-----------------------------

## Launch SPPAS for the first time

![](./etc/screencasts/sppas-launch-first.mp4)

-----------------

### Launch SPPAS for the first time

* Open the SPPAS folder
* Double-click on "sppas.bat" file (Windows) or "sppas.command" file (Linux/MacOS)
* A security alert may occur...
* Ignore the message and start SPPAS anyway
* Python opens a black frame
* SPPAS Graphical User Interface then arises

-----------------------------

## Launch SPPAS

![](./etc/screencasts/sppas-launch.mp4)

* Open the SPPAS folder
* Python opens a black frame (and... don't close it!)
* SPPAS Graphical User Interface then arises

-----------------------------

## Install a plugin

![](./etc/screencasts/sppas-install-plugin.mp4)

-----------------

### Install a plugin

* Open SPPAS folder then launch SPPAS
* Click on "Plugins" action icon
* Click on the "Install" button
* Set the plugin package
* The plugin is added into the list of plugins

-----------------------------

## Check audio files

![](./etc/screencasts/sppas-demo01-audioroamer-selectchannel.mp4)

-----------------------------

## Check audio files

![](./etc/screencasts/sppas-demo02-audioroamer.mp4)               

* Type  F5 to refresh the list of files

-----------------------------

## Visualize files

![](./etc/screencasts/sppas-demo03-vizualizer.mp4)          

-------------------

### Visualize files

* Select the files
* Click on the Visualizer
* Click on the files to open

    - Tabs allow to open files separately
    - Green buttons allow to display information and play the sound
    - Blue buttons allow to scroll and zoom

-----------------------------

## Remove files

![](./etc/screencasts/sppas-demo04-remove.mp4)      

-----------------------------

## Silence/Speech segmentation

![](./etc/screencasts/sppas-demo05-ipus.mp4)                       

------------------------

### Silence/Speech segmentation

* Select the audio files, or the whole directory
* Click on "Annotate" action button
* Enable "IPUs Segmentation" automatic annotation
* Click on "Configure" blue text
* Fix carefully each option: READ DOCUMENTATION
* Click on "Performs annotations" button
* A "Procedure Outcome Report" is displayed: 
    
    - read it!
    - ... and save it.

* Newly created files are automatically added into the list

-----------------------------

## Visualize IPUs

![](./etc/screencasts/sppas-demo06-ipus-vizualize.mp4)            

-----------------------------

## IPUscriber

![](./etc/screencasts/sppas-demo07-ipuscribe.mp4)

---------------

### IPUscriber

* Select the audio files and click on "IPUscriber"
* Click on the file to open
* Click on the IPU to transcribe and play the sound
* Perform manually the orthographic transcription of each IPU
* Tabs allow to transcribe several files in parallel
* Copy/Paste transcription is allowed (CTRL-C/CTRL-V)
* Save the displayed files or save all

-----------------------------

## Transcription (1)

![](./etc/screencasts/sppas-demo08-transcription1.mp4)

---------------

### Transcription

* Transcription requirements and the convention are in the help
* It must includes: silent pauses, filled pauses, repeats, truncated words, etc...
* It must strictly follow the convention
* The same information is also in the documentation
* the full convention and advices is here:
    
<https://hdl.handle.net/11403/sldr000873/toe-sppas.pdf>

-----------------------------

## Transcription (2)

![](./etc/screencasts/sppas-demo09-transcription2.mp4) 

-----------------------------

## Convert XRA to TextGrid

![](./etc/screencasts/sppas-demo10-convert-xra-textgrid.mp4)

---------------------------

### Convert XRA to TextGrid

* By default, SPPAS creates XRA files
* Files can be exported in several formats
* Select files and click on "Export" button
* Select the file extension in the list
* Newly created files are added into the list
* Regardless of the format files can be visualized, annotated, etc.

-----------------------------

## Check transcription and ipus (1)

![](./etc/screencasts/sppas-demo11-praat-correction1.mp4)

-------------------------------

### Check transcription and ipus

* Check the transcription and IPUs with Praat or Phonedit, or AnnotationPro, ...
* Praat: 
  
    - *first of all* check "Text writing preferences...": Set to UTF-8
    - Adjust font size
    - Fix properly the sound scaling: Scaling strategy: fixed height

* Adjust IPUs boundaries
* Play sound and validate the transcription
* Save the TextGrid file

-----------------------------

## Check transcription and ipus (2)

![](./etc/screencasts/sppas-demo12-praat-correction2.mp4)

-------------------------------

### Check transcription and ipus

* For an audio file of 50 seconds:

    - less than 1 minute to perform automatic IPUs segmentation;
    - about 4 minutes to transcribe with IPUscriber;
    - about 4 minutes to check both the transcription and IPUs (with an external program).

-----------------------------

## Generates a PitchTier file

![](./etc/screencasts/sppas-demo13-praat-pitchtier.mp4)

-----------------------------

## Manage files

![](./etc/screencasts/sppas-demo14-files.mp4)

-----------------------------

## Text normalization

![](./etc/screencasts/sppas-demo15-tokenization.mp4)

---------------------

### Text normalization

* Select audio files or the whole directory
* Enable "Tokenization"
* Click on the "Configure" blue text
* Fix the options
* Choose the language in the list
* Click on "Perform annotations" button
* The "Procedure Outcome Report" is displayed
* Newly created files are automatically added into the list

-----------------------------

## Phonetization

![](./etc/screencasts/sppas-demo16-phonetization.mp4)

-----------------

### Phonetization

* Select audio files or the whole directory
* Enable "Phonetization"
* Click on the "Configure" blue text
* Fix the options
* Choose the language in the list
* Click on "Perform annotations" button
* The "Procedure Outcome Report" is displayed
* Newly created files are automatically added into the list

-----------------------------

## Alignment

![](./etc/screencasts/sppas-demo17-alignment.mp4)

-----------------

### Alignment

* Select audio files or the whole directory
* Enable "Alignment"
* Click on the "Configure" blue text
* Fix the options
* Choose the language in the list
* Click on "Perform annotations" button
* The "Procedure Outcome Report" is displayed
* Newly created files are automatically added into the list

-----------------------------

## Syllabification

![](./etc/screencasts/sppas-demo18-syllabification.mp4)

-----------------

### Syllabification

* Select audio files or the whole directory
* Enable "Syllabification"
* Click on the "Configure" blue text
* Fix the options
* Choose the language in the list
* Click on "Perform annotations" button
* The "Procedure Outcome Report" is displayed
* Newly created files are automatically added into the list

-----------------------------

## Momel and INTSINT

![](./etc/screencasts/sppas-demo19-momel-intsint.mp4) 

-----------------

### Momel and INTSINT

* Select audio files or the whole directory
* Enable "Momel"
* Enable "INTSINT"
* Click on the "Configure" blue text of "Momel"
* Fix the options
* Click on "Perform annotations" button
* The "Procedure Outcome Report" is displayed
* Newly created files are automatically added into the list

-----------------------------

## Views of the merged file

![](./etc/screencasts/sppas-demo20-view-merge.mp4)

-----------------------------

## Apply plugins

![](./etc/screencasts/sppas-demo21-plugins.mp4)

------------------

### Apply a plugin

* Select the files
* Click on Plugins
* Click on the button of the plugin
* Verify options
* Press OK to apply the plugin
* Newly created files are automatically added to the list of files

-----------------------------

## DataRoamer: annotated files manager

![](./etc/screencasts/sppas-demo22-dataroamer.mp4)

-----------------------------

## Copy a file

![](./etc/screencasts/sppas-demo23-copy.mp4)

-----------------------------

## Export files

![](./etc/screencasts/sppas-demo24-export.mp4)

-----------------------------

## the Time Group Analyzer

![](./etc/screencasts/sppas-demo25-tga.mp4)

-----------------------------

### the Time Group Analyzer

- proposed by D. Gibbon and implemented into DataStats of SPPAS
- Time Group Analysis requires syllables
- Each line of the displayed gris are the results of a Time Group
- The "Means" tab displays information of each file
- The "Delta Duration" tab compares the duration of each syllable with the previous one
- TGA results can be exported as an annotated file
- TGA results can be saved in a CSV file

-----------------------------

## Statistical distributions

![](./etc/screencasts/sppas-demo26-distrib.mp4)

-----------------------------

### Statistical distributions

- Information about statistical distributions

    - Summary Tab displays occurrences and total/mean/media/stdev duration of each label
    - Occurrences tab: occurrences of each label in each file
    - Total durations tab: total duration of each label in each file
    - Mean durations tab: mean duration of each label in each file
    
- Distributions of sequences of labels: change Ngram value
- Any of the displayed grid can be saved in a CSV file

-----------------------------

## Data Filter (1)

Request 1: Get all "toto" tokens

![](./etc/screencasts/sppas-demo27-filter-toto.mp4)

-----------------------------

## Data Filter (2)

Request 2: Get "p, t, k, b, d, g" time-aligned phonemes

![](./etc/screencasts/sppas-demo28-filter-ptkbdg.mp4)

-----------------------------

## Data Filter (3)

Request 3: Get time-aligned phonemes during more than 80ms

![](./etc/screencasts/sppas-demo29-filter-duration.mp4)

-----------------------------

## Data Filter (4)

Request 4: Get time-aligned "p, t, k, b, d, g" during more than 80ms

![](./etc/screencasts/sppas-demo30-duration-ptkbdg.mp4)
          
-----------------------------

## Data Filter (5)

Request 5: Get the first phoneme of each syllable

![](./etc/screencasts/sppas-demo31-filter-first-phon-in-syll.mp4)

-----------------------------

## View result

![](./etc/screencasts/sppas-demo32-filter-verif.mp4)

-----------------------------

## Fix settings

![](./etc/screencasts/sppas-demo33-settings.mp4)

-----------------------------

## Getting help

![](./etc/screencasts/sppas-demo34-help.mp4)

-----------------------------

### 

[Back to tutorials](./tutorial.html)



