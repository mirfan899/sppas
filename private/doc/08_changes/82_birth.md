## The birth of SPPAS


### SPPAS 1.4.0 

(2012, 14th June)

It's the official birth of SPPAS: the software has a name, a license, a GUI, 
a web-page and is freely distributed to the community.

The source code is only based on Python 2.7 language and the GUI is based 
on WxPython 2.8.x or 2.9.x (on MacOS, wxpython must be 32 bits).
SPPAS requires also `sox` and `julius` software to be installed.

#### Automatic annotations:

- add Momel: 
  Momel (MOdelling MELody) is an algorithm developed by Daniel Hirst
  and Robert Espesser for the analysis and synthesis of intonation patterns.
  Momel needs a .hz files with pitch values: ASCII file with one value each 10ms.
  This Momel implementation can be used directly, with a large set of options:
     > python $SPPAS/scripts/lib/momel.py -h

  or in SPPAS, using the GUI, or in text-mode (only with default options):
     > $SPPAS/sppas.py -i INPUT --momel

- add the first version of INTSINT, proposed by Daniel Hirst.
  INTSINT is an acronym for INternational Transcription System for INTonation.
  INTSINT codes the intonation of an utterance by means of an alphabet of i
  8 discrete symbols constituting a surface phonological representation of
  the intonation.

#### Packaging:

- merge AUTHORS, VERSION and README files in the README file
- create packages in the lib directory (2012-03-20)
- ipu-segmentation in python (2012-02-16)
- improve ipu segmentation algorithm (2012-05-24)
- phonetization in python (2012-02-27), with an unknown word phonetization.
- alignment entirely in python (2012-03-29)
- syllabification implemented with python, and tool/syllabify.py
- add a simple terminal controller (not needed for Unix, just for "DOS")
- Momel can read PitchTier (from Praat) files
- Momel can deal with long sounds (not only one IPU)
- manage source files, comments, exceptions...
- SPPAS works as a single instance by mean of a lock file.
- SPPAS can be installed in a directory containing spaces and can deal
  with file names with spaces (bug fixed: 2012-06-11)

#### GUI:

- GUI with the wxpython library (2012-03-27)
- Manage a list of selected files
- Add a "File information"
- Add a "Wav player"
- Fix options to each annotation step with the menu
- Open the log file after each process

#### Resources:

- French dictionary is using UTF-8 (instead of iso8859-1 in previous versions)
- French dictionary is based on X-SAMPA phone set
- Chinese: work with chinese characters instead of pinyin.

#### Known Bugs:

- The wav player can not play wav files if the filename contains '#'.
- The first line of the Italian dictionary must be changed to "# [#] #".


### SPPAS 1.4.1 

(2012, 13th July)

#### Resources:

- Updated English acoustic model (from voxforge, 2012-06-25)
- English acoustic models converted to X-SAMPA

#### Automatic annotations:

- IPUs Segmentation annotation performs a simple silence detection if no
  transcription is available (the volume is automatically adjusted)
- A specific language can be selected for each annotation depending on
  available resources
- Updated transcription conventions:
   * truncated words: a '-' at the end of the token string (an ex- example)
   * liaisons: the 'letter' between '=' (an =n= example)
   * noises: * (only for FR and IT)
   * short pauses: + (a + example)
   * silences: # (a # example)

#### GUI:

- Create (systematically) a merged annotations TextGrid file.

#### Development:

- Package's management


### SPPAS 1.4.2 

(2012, 2nd August)

#### GUI:

- add a panel with a Transcription editor
- IPU segmentation can split a wav into tracks
- IPU segmentation can fix a shift value to boundaries
- IPU segmentation: min-volume option is removed (because the min-volume
value is automatically adjusted)
- "File Information" button adds some tier manipulation tools:
    cut/copy/paste/rename/duplicate/move/preview/filter

#### Known bug:

- The filter frame is not working under Windows XP.


### SPPAS 1.4.3 

(2012, 10th October)

This is primarily a bug-fix release. 
The author is addressing many thanks to all users who send their
comments!

#### GUI:

- Frames and Dialog design is more uniform.
- Users preferences changed. Themes and colors introduced.
- Help is available.

#### Automatic annotations:

- Bug fixed for phonetization/alignement if the input transcription contains
series of silence intervals or series of speech intervals. Previous
versions was supposing a **strict IPUs** input transcription.
- Tokenization is done.

#### Development:

- Code cleaning in the package wxGUI.
- Debug...


### SPPAS 1.4.4 

(2012, 6th December)

#### GUI:

- add information/options when "Request" a file
- debug Request/Filter (for Windows systems)

#### Automatic annotations:

- New Italian acoustic model
- New Chinese acoustic model, and some minor changes in the dictionary

#### Development:

- ".trs" files support (transcriptions from Transcriber)
- debug (alignment, tokenization)
- add ".lab" files export (HTK format)

#### Known bugs:

- Alignment: it fails under Windows, if `julius` is not installed properly.
- Syllabification: the last syllable of each file is "broken".
- Alignment error if unknown words during phonetization.


### SPPAS 1.4.5 

(2013, 15th January)

#### Development:

- Correct a few bugs of the previous version (phonetization, alignment, 
syllabification)
- ".eaf" files support (transcriptions from Elan software)
- add script tierfilter.py
- add script tiercombine.py

#### Automatic annotations:

- Experimental version of Vietnamese
- add Tokenization as a specific annotation level
- add Phonetization of PinYin

#### GUI:

- Request/Filter a tier: multiple patterns filtering
- Request: add a "New File" button


### SPPAS 1.4.6

(2013, 12th February)
 
#### GUI:

- Improved Request/Filter a tier:
  * add new modes: not contains, not starts with, not ends with
  * add time constraints: minimum duration, maximum duration, meets
  * multiple modes selection (replace radio buttons by check buttons)
- Add Requests/Stats to obtain basic statistics
- Requests Copy/Cut/Paste/Duplicate/Save debugged

#### utomatic annotations:

- IPU segmentation: can take a "Name" tier to fix names of tracks
  (if the "Split into tracks" option is checked)


### SPPAS 1.4.7 

(2013, 25th March)

#### Development:

- re-organization of lib, except for the wxGUI library.
- Cancel the sppas.lock file creation when SPPAS is running.
- Requests/Filter: "Starts search at..." and "Ends search at..."
- Requests/Filter: remove negative search (because of a bug...). Replaced by a "reverse" option.

#### Resources:

- add experimental version of Taiwanese automatic segmentation (from 
  romanized transcriptions)

#### Annotations:

- New version of INTSINT, based on the algorithm proposed in (Hirst 2011)
  and implemented in the last version of Momel/INTSINT Praat plugin!


### SPPAS 1.4.8 

(2013, 30th May)

#### Development:

- reorganization of the GUI code. SPPAS is made of:

   * automatic annotations;
   * 3 components (wavplayer, transcriber, requests).
   
- sppas.py removed. sppas.bat created (for Windows).
- Input/Output library entirely changed

#### GUI:

- components (wavplayer, transcriber, requests) in separate frames
- new design
- Help and documentation changed, expanded and improved


### SPPAS 1.4.9 

(2013, 3rd July)

SPPAS has a new and more colored logo!

#### Development:

- bug correction:
   * Bug fixed in IPU segmentation with option "Split into tracks"
   * Bug fixed in Momel with some rare files
   * Bug fixed to create a merged file
   * Bug fixed in align and IPU seg.
   * Bug fixed in Transcriber
- library organization revised

#### GUI:

- Add an export button to the File List Panel
- Migrate wav infos from the Requests component to the Wav player component
- Volume control removed in the Wav Player component
- Save As improved in the Requests component


### SPPAS 1.5.0

(2013, 2nd August)
 
#### Development:

- bug correction

#### Annotation:

- Tokenization: TOE support finalized

#### GUI:

- Transcribe: debug of IPU player, for MacOS

#### Resources:

- New French acoustic model. Attention: phoneset changed.
- New French dictionary: use the new phoneset!
- New Taiwanese acoustic model. Attention: phoneset changed: accept some chinese...
- New Taiwanese dictionary: use the new phoneset + some chinese syllabes added.
- Vietnamese removed: due to the lack of data, the model can't be improved.


### SPPAS 1.5.1 

(2013, 29th August)

#### Development:

- bug correction in annotations
- help system debugged

#### Annotation:

- Phonetization of unknown words improved

#### Resources:

- French dict modified


### SPPAS 1.5.2 

(2013, 27th September)

All resources are moved into the "resources" directory.

#### Development:

- bug correction in annotations and GUI

#### Resources:

- French dict modified
- New resources for the tokenization

#### Components:

- "Statistics": an avanced component to estimate (and save!) descriptive 
statistics on multiple annotated files


### SPPAS 1.5.3 

(2013, 25th October)

#### Resources:

- Add Spanish support

#### Components:

- improved Statistics component
- Add a "Filter" component, first version with a basic GUI

#### GUI:

- Help updated.


### SPPAS 1.5.4 

(2013, 3rd December)

#### Components:

- Wav Player changed.
- Information and Requests removed. Replaced by Data Roamer.
- Transcriber removed. Replaced by IPU Transcriber.
- Statistics updated.
- Filter updated.

#### Annotations:

- Add Repetitions (detection of sources only)

Notice that this is the first stable release.


### SPPAS 1.5.5 

(2013, 23th December)

#### Development:

- improved annotationdata
  (add methods: Find, Index; add uncertain label; debug radius).

#### Components:

- debug

#### GUI:

- Tips at start-up
- New theme: Christmast


### SPPAS 1.5.6 

(2014, 28th January)

#### Development:

- improved annotationdata (add methods: Near, Search).
- Package cleaning!

#### Components:

- debug

#### Resources:

- New Italian dictionary (including gemination)


### SPPAS 1.5.7 

(2014, 18th February)

#### Development:

- Plugins manager added.

#### Resources:

- Japanese support, thanks to the resources available on the Julius website.


### SPPAS 1.5.8 

(2014, 18th March)

#### Development:

- annotationdata: more flexibility while adding annotations,
  add sub-divisions, export csv modified, docstrings,
  import/export in a native format (xra, version 1.0).

#### Documentation:

- add a PDF file of slides: "SPPAS for dummies"


### SPPAS 1.5.9 

(2014, 15th April)

#### Components:

- new: DataViewer, experimental version

#### Annotations:

- syllabification rules: accept 2 types of vowels (V and W)
- syllabification: faster!

#### Development:

- Export Elan
- Import/Export xra. XRA is the native format of SPPAS annotation files. 
  See etc/xra for details.

#### Resources:

- New French acoustic model


### SPPAS 1.6.0 

(2014, 22th May)

#### Package:

- Rename folder "Doc" to "documentation"
- A documentation is created
- SPPAS-for-dummies updated

#### Development:

- helpsystem removed
- GUI: package re-organization, re-implementation.
- Alignment: choice of the aligner (julius, hvite or basic)

#### Resources:

- new acoustic model: FR-Read and FR
- new acoustic model: ZH
- new acoustic model: TW
- new acoustic model: SP


### SPPAS 1.6.1 

(2014, 26th September)

#### Development:

- bug correction (export, syllabification, alignment)
- DataViewer, major bugs corrected.

#### Resources:

- Italian: new pronunciation dictionary and new acoustic model
- add resources for Catalan

#### GUI:

- add a new Export button


### SPPAS 1.6.2 

(2014, 21th October)

#### Resources:

- language names changed. They are now corresponding to the international
  standard ISO639-3. See <http://www-01.sil.org/iso639-3/>
- Mandarin Chinese dictionary changed.
- Catalan dictionary changed.


### SPPAS 1.6.3 

(2014, 2nd November)

#### Resources:

- Add resources for Cantonese

#### Documentation:

- It's now (more or less) finished!

#### Development:

- Support of Elan improved (add Controlled vocabulary)

#### GUI:

- Change the organization of the main frame: annotations above components

This version is known to be a stable release.
