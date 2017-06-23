## the Prehistory

SPPAS 1.0 to 1.3 was made only of tcsh and gawk scripts. It was developped
under Linux and tested under Windows with Cygwin.


#### Version 1.0

The first release was published on 2011, 9th March.

It was able to perform speech segmentation of English read speech.


#### Version 1.1

Published on 2011, 7th June.


#### Version 1.2:

Published on 2011, 23th July.

Support of English, French and Italian.


#### Version 1.3

Published on 2011, 12th December.

This is a transitional version, from tcsh/bash scripts to python.
The main fixes and improvements are:

Programs:

  - MacOS support
  - bugs corrected in many scripts.
  - check.csh -> check.py
  - sppas.csh -> sppas.py
  - GUI: zenity ->  pyGtk
  - sox now only used for resampling
  - a wav python library is added.

Resources:

  - Italian dictionary improved
  - Italian acoustic model changed
        (triphones trained from map-task dialogues. see doc/publications)
  - French acousic model changed


## the Middle Ages

Since version 1.4, SPPAS has a name!

It's python made only.
It uses python 2.7.x and wxpython 2.8.x or 2.9.x.

Remark for MacOS users: wxpython must be 32 bits.
SPPAS requires sox and julius free software to be installed.


#### SPPAS 1.4 (2012-06-14)

This is the first real version of SPPAS.

Automatic annotations main changes:

  - add momel: implements momel in python.
    Momel (MOdelling MELody) is an algorithm developed by Daniel Hirst
    and Robert Espesser for the analysis and synthesis of intonation patterns.
    Momel need a .hz files with pitch values: ASCII file with one value each 10ms.
    This Momel implementation can be used directly, with a large set of options:

          > python $SPPAS/scripts/lib/momel.py -h

    or in SPPAS, using the GUI, or in text-mode (only with default options):

          > $SPPAS/sppas.py -i INPUT --momel

  - add the first version of INTSINT, proposed by Daniel Hirst.
    INTSINT is an acronym for INternational Transcription System for INTonation.
    INTSINT codes the intonation of an utterance by means of an alphabet of i
    8 discrete symbols constituting a surface phonological representation of
    the intonation:

       - T (Top),
       - H (Higher),
       - U (Upstepped),
       - S (Same),
       - M (mid),
       - D (Downstepped),
       - L (Lower),
       - B (Bottom).

Package:

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

GUI:

  - pyGTK GUI: select steps in the main window
  - pyGTK GUI: add 'None' in the language list for language-independent modules
  - GUI with the wxpython library (2012-03-27)
  - Manage a list of selected files
  - Add a "File information"
  - Add a "Wav player"
  - Fix options to each annotation step with the menu
  - Open the log file after each process

Resources:

  - French dictionary is using UTF-8 (instead of iso8859-1 in previous versions)
  - French dictionary is SAMPA
  - Chinese: work with chinese characters instead of pinyin.

Known Bugs:

    - The wav player can not play wav files if the filename contains '#'.
    - The first line of the Italian dictionary must be changed to "# [#] #".


#### SPPAS 1.4.1 (2012-07-13)

Resources:

  - Updated English models (from voxforge, 2012-06-25)
  - English acoustic models updated, and converted to SAMPA

Annotations:

  - IPUs Segmentation annotation performs a simple silence detection if no
    transcription is available (the volume is automatically adjusted)
  - A specific language can be selected for each annotation depending on
    available resources
  - Updated transcription conventions:
        truncated words: a '-' at the end of the token string (an ex- example)
        liaisons: the 'letter' between '=' (an =n= example)
        noises: * (only for FR and IT)
        short pauses: + (a + example)
        silences: # (a # example)

GUI:

  - Create (systematically) a merged annotations file.

Development:

   - Package's management


#### SPPAS 1.4.2 (2012-08-02)

GUI:

  - add a panel with a Transcription editor
  - IPU segmentation can split a wav into tracks
  - IPU segmentation can fix a shift value to boundaries
  - IPU segmentation: min-volume option is removed (because the min-volume
    value is automatically adjusted)
  - "File Information" button adds some tier manipulation tools:
        cut/copy/paste/rename/duplicate/move/preview/filter

Known bug:

  - The filter frame is not working under Windows XP.


#### SPPAS 1.4.3 (2012-10-10)

This is primarily a bug-fix release. Many thanks to all users who send their
comments!

GUI:

  - Frames and Dialog design is more uniform.
  - Users preferences changed. Themes and colors introduced.
  - Help is available.

Annotations:

  - Bug fixed for phonetization/alignement if the input transcription contains
    series of silence intervals or series of speech intervals. Previous
    versions was supposing a **strict IPUs** input transcription.
  - Tokenization is done.

Development:

  - Code cleaning in the package wxGUI.
  - Debug...


#### SPPAS 1.4.4 (2012-12-06)

GUI:

  - add information/options when "Request" a file
  - debug Request/Filter (for windows)

Annotations:

  - New Italian acoustic model
  - New Chinese acoustic model, and some minor changes in the dictionary

Development:

  - ".trs" files support (transcriptions from Transcriber)
  - debug (alignment, tokenization)
  - add ".lab" files export (HTK format)

Known bugs:

   - Alignment: it fails under Windows, if julius is not installed properly.
   - Syllabification: the last syllable of each file is "broken".
   - Alignment error if unknown words during phonetization.


#### SPPAS 1.4.5 (2013-01-15)

Development:

  - Correct a few bugs of the previous version
    (phonetization, alignment, syllabification)
  - ".eaf" files support (transcriptions from Elan)

Annotations:

  - Experimental version of Vietnamese
  - add Tokenization as a specific annotation level
  - add Phonetization of PinYin

GUI:

  - Request/Filter a tier: multiple patterns filtering
  - Request: add a "New File" button

Tools/scripts:

  - tierfilter.py
  - tiercombine.py


#### SPPAS 1.4.6 (2013-02-12)

GUI:

  - Improved Request/Filter a tier:

      * add new modes: not contains, not starts with, not ends with
      * add time constraints: minimum duration, maximum duration, meets
      * multiple modes selection (replace radio buttons by check buttons)

  - Add Requests/Stats to obtain basic statistics
  - Requests Copy/Cut/Paste/Duplicate/Save debugged

Annotations:

  - IPU segmentation: can take a "Name" tier to fix names of tracks
    (if the "Split into tracks" option is checked)


#### SPPAS 1.4.7 (2013-03-25)

Requests/Filter:

  - "Starts search at..." and "Ends search at..."
  - remove negative search (because of a bug...).
    Replaced by a "reverse" option.

Development:

  - re-organization of lib, except for the wxGUI library.
  - Cancelled the sppas.lock file creation when SPPAS is running.

Resources:

  - add experimental version of Taiwanese automatic segmentations
    (from romatized transcriptions),
    thanks to Sheng-Fu Wang for the corpus.

Annotations:

  - New version of INTSINT, based on the algorithm proposed in (Hirst 2011)
  and implemented in the last version of Momel/INTSINT Praat plugin!


#### SPPAS 1.4.8 (2013-05-30)

Development:

  - reorganization of the GUI code.  SPPAS is made of:

       * automatic annotations;
       * 3 components (wavplayer, transcriber, requests).

  - sppas.py removed. sppas.bat created (for Windows).
  - Input/Output library entirely changed


GUI:

  - components (wavplayer, transcriber, requests) in separate frames
  - new design
  - Help and documentation changed, expanded and improved


#### SPPAS 1.4.9 (2013-07-03)

New Logo!

Development:

  - bug correction:

      - Bug fixed in IPU segmentation with option "Split into tracks"
      - Bug fixed in Momel with some rare files
      - Bug fixed to create a merged file
      - Bug fixed in align and IPU seg.
      - Bug fixed in Transcriber

  - library organization revised

GUI:

  - Add an export button to the FLP
  - Migrate wav infos from the Requests component to the Wav player component
  - Volume control removed in the Wav Player component
  - Save As improved in the Requests component


#### SPPAS 1.5 (2013-08-02)

Development:

  - bug correction

Annotation:

   - Tokenization: TOE support finalized

GUI:

   - Transcribe: debug of IPU player, for MacOS

Resources:

  - New French acoustic model. Attention: phoneset changed.
  - New French dictionary: use the new phoneset!
  - New Taiwanese acoustic model. Attention: phoneset changed: accept some chinese...
  - New Taiwanese dictionary: use the new phoneset + some chinese syllabes added.
  - Vietnamese removed: due to the lack of data, the model cant be improved.


#### SPPAS 1.5.1 (2013-08-29)

Development:

    - bug correction in annotations
    - help system debugged

Annotation:

    - Phonetization of unknown words improved

Resources:

    - French dict modified


#### SPPAS 1.5.2 (2013-09-27)

ALL RESOURCES ARE MOVED IN A 'RESOURCES' DIRECTORY.

Development:

  - bug correction in annotations and GUI

Resources:

  - French dict modified
  - New resources for the tokenization

Components:

  - Statistics: an avanced component to estimate (and save!) statistics on
    multiple annotated files


#### SPPAS 1.5.3 (2013-10-25)

Resources:

  - Add Spanish support, thanks to JuanMaria Garrido and the "Glissando" corpus

Components:

  - improved Statistics component
  - Add a "Filter" component, first version with a basic GUI

Help updated.


#### SPPAS 1.5.4 (2013-12-03)

The most stable release of this period.

Components:

  - Wav Player changed.
  - Information and Requests removed. Replaced by Data Roamer.
  - Transcriber removed. Replaced by IPU Transcriber.
  - Statistics updated.
  - Filter updated.

Annotations:

  - Add Repetitions (detection of sources only)


#### SPPAS 1.5.5 (2013-12-23)

Development:

  - improved annotationdata
      (add methods: Find, Index; add uncertain label; debug radius).

Components:

  - debug

GUI:

  - Tips at start-up
  - New theme: Christmast


#### SPPAS 1.5.6 (2014-01-28)

Development:

  - improved annotationdata (add methods: Near, Search).

Components:

  - debug

Resources:

  - New Italian dictionary (including gemination)

Package cleaning!


#### SPPAS 1.5.7 (2014-02-18)

Plugins management.

Resources:

  - Japanese support, thanks to the resources available on the Julius website.


#### SPPAS 1.5.8 (2014-03-18)

Development:

  - annotationdata: more flexibility while adding annotations,
      add sub-divisions, export csv modified, docstrings,
      import/export in a native format (xra, version 1.0).

Documentation:

  - add a PDF file of slides: "SPPAS for dummies"


#### SPPAS 1.5.9 (2014-04-15)

Components:

  - new: DataViewer, experimental version

Annotations:

  - syllabification rules: accept 2 types of vowels (V and W)
  - syllabification: faster!

Development:

  - Export Elan
  - Import/Export xra (SPPAS native format. See etc/xra for details)

Resources:

  - New French acoustic model


#### SPPAS 1.6 (2014-05-22)

Package:

  - Rename folder Doc to documentation
  - Documentation created, SPPAS-for-dummies updated.

Development:

  - helpsystem removed
  - gui: package re-organization, re-implementation.
  - Alignment: choice of the aligner (julius, hvite or basic)

Resources:

  - new acoustic model: FR-Read and FR
  - new acoustic model: ZH
  - new acoustic model: TW
  - new acoustic model: SP


#### SPPAS 1.6.1 (2014-09-26)

Development:

  - bug correction (export, syllabification, alignment)
  - DataViewer, major bugs corrected.

Resources:

  - new pronunciation dictionary and new acoustic model for Italian
  - add resources for Catalan

GUI:

  - add a new Export button


#### SPPAS 1.6.2 (2014-10-21)

Resources:

  - language names changed. They are now corresponding to the international
      standard ISO639-3. See <http://www-01.sil.org/iso639-3/>
  - Mandarin Chinese dictionary changed.
  - Catalan dictionary changed.


#### SPPAS 1.6.3 (2014-11-02)


Resources:

  - Add resources for Cantonese

Documentation:

  - It's now (more or less) finished!

Development:

  - Support of Elan improved (add Controlled vocabulary)

GUI:

  - Change the organization of the main frame: annotations above components



## the Renaissance

Since version 1.6.4, SPPAS is still using python 2.7.x, but SPPAS
requires wxpython > 3.0.

For MacOS users: wxpython must be installed in 64 bits (cocoa).


#### SPPAS 1.6.4 (2014-12-05)

Package re-organized!

Development:

  - Phonetization of unknown words improved
  - Support of upper/lower of the extension of speech files (wav, WAV)
  - Tokenization of languages with dictionaries in upper case (eng, ita): bug fixed.
  - Creates systematically a dump file of resources for a faster load at the next use
  - Read TextGrid files exported by Elan: bug fixed.
  - `sppas.command` checks the system and run either in 32 or 64 bits (MacOS)

Components:

  - IPUscribe replaces IPUTransciber mainly for the support large files:
    tested with a file of 1 hour speech (143 Go) and 800 IPUs.
  - SndRoamer replaces WavPlayer
  - Dataroamer has also a new version


#### SPPAS 1.6.5 (2014-12-17)

This is primarily a bug-fix release.

Development:

  - all programs in "bin" and "scripts" sub-directories were revised and
    tested, or removed.

Annotation:

  - Tokenization: code cleaning and re-organisation.

GUI:

  - Procedure outcome report: print a warning message in the log file if no
    file is matching the expected extension


#### SPPAS 1.6.6 (2015-01-19)

Documentation completed and updated. Now, only the documentation of all the
components is missing.

Annotations:

  - log messages more explicit and status with colors:

     * OK is green
     * WARNING is orange
     * IGNORED is violet
     * INFO is blue
     * ERROR is red

  - management of input/output file format redone: now easier for the user.

Development:

  - package architecture revised: mainly "sppasgui" and "components" merged
   in "wxgui", and many other changes.
  - thread removed in automatic annotation process.
  - debug of alignment: if too short units.
  - radius value properly fixed in most of the automatic annotations.

GUI:

  - GUI is more homogeneous and pretty (hope!)
  - Show the date in the status bar
  - New Settings frame:

      - 4 icon themes available
      - Choice of foreground and background colours
      - Choice of the font
      - Choice of the input/output file format of annotations

  - New in Help menu:

     - access to the project homepage
     - access to the online documentation
     - New Feedback

  - New Help browser
  - Add Keyboard shortcuts:

     - ALT+F4 to exit,
     - CTRL+A to add files in FLP
     - SHIFT+CTRL+A to add a directory in FLP
     - Del to remove selected files of the FLP
     - SHIFT+Del to erase selected files of the FLP
     - CTRL+C to copy files
     - CTRL+E to export files
     - F5 to refresh the FLP
     - F1 to open the help browser
     - F2 to open the "About" frame

Components:

  - GUI design unified for DataRoamer, SndPlayer, IPUscribe and SppasEdit
  - New Tier Preview frame (still under development)
  - SndPlayer print information about a sound file with colors:

     - Green: the information corresponds to the SPPAS requirements
     - Orange: the information does not exactly corresponds to the requirements
        however SPPAS is able to deal with (after convertion)
     - Red: SPPAS does not support. It must be converted before using it!

Web site host has changed: <http://sldr.org/sldr00800/preview/>


#### SPPAS-1.6.7 (2015-02-16)

Automatic Annotations:

  - By default, tokenization produces only one tier. Check an option to get
    TokensStd and TokensFaked, in case of EOT.
  - radius value properly fixed in most of the automatic annotations.

GUI:

  - Tested and debugged on MacOS (version 10.9.5, with wxpython 3.0.2)

Development:

  - Tier hierarchy partly implemented: TimeAlignement and TimeAssociation are
    two "links" that can be fixed between tiers.

Annotations:

  - Add Polish support


#### SPPAS-1.6.8 (2015-04-09)

Resources:

  - new French acoustic model
  - new English acoustic model (VoxForge nightly build of March, 15th, 2015)
  - add phoneset mapping tables

Development:

  - Add a phoneme mapping in models, to allow both the dictionary to include
  real SAMPA symbols and the acoustic model to be compatible with Hvite
  requirements.
  - annotationdata bug correction with min and max values
  - IPUs Segmentation:

     - bug correction when split into tracks with a tier "Name"
     - add the ipu number in speech segments if silence/speech segmentation

  - Self-repetitions debug in finding the repetition interval

GUI:

  - DataRoamer: "New" button debugged
  - DataRoamer: Add a button "Radius" to adjust manually the vagueness of each bounday of a tier



## the Early modern period

Since version 1.6.9, the installation is simplified: sox is unnecessary.
Python 2.7.something, wxpython 3.something and Julius are the only dependencies.


#### SPPAS-1.6.9 (2015-05-14)

Development:

  - package annotationdata.filter updated to support last changes of
    annotationdata: multiple labels and numerical labels.
  - package annotationdata.io:

      - praat.py newly created. Support of TextGrid, PitchTier and
       IntensityTier files completely re-written
      - htk.py newly created to support .lab and .mlf files
      - sclite.py newly created to support .stm and .ctm files
      - signaix.py newly created to support .hz files
      - SPPAS native format XRA upgraded to version 1.1 to support
        improvements of the library.

  - package annotationdata:

      - updated object Transcription to support more/different input data
      - updated hierarchy
      - updated meta-data

  - package signal: partially re-written. As a consequence, sox won't
    be neither used, but the file conversion (if required) is slower.

GUI:

  - DataFilter component partially re-written to facilitate its use
  - Preview frame modified


#### SPPAS-1.7.0 (2015-07-03)

Development:

  - package annotationdata.io:

      - add support of subtitles: sub, srt
      - elan.py created to replace eaf.py: allows a full support of Elan annotations
      - transcriber.py created to replace trs.py for a better support of Transcriber files
      - anvil.py allows to import anvil files

  - package annotationdata:

      - updated hierarchy
      - updated meta-data

  - package signal:

     - support of audio files re-written: can open/save wav, aiff and au files
     - add a lot of possibilities to manage one channel of an audio file

GUI:

  - DataFilter component finalized: can deal with alternative labels,
    and typed labels (string, number, boolean)
  - Statistics component fully re-written to facilitate its use
  - SndRoamer displays more properties of audio files (min, mean and max added)

Annotations:

  - IPUs Segmentation produces 2 tiers if a transcription is given:
    the IPUs segmentation itself, and the Transcription time-aligned
    at the IPUs level.


#### SPPAS-1.7.1 (2015-08-05)

Development:

  - package re-organization:

     - package signal is now standalone
     - package resources is now standalone
     - package presenters created

  - updated statistics estimations
  - package annotationdata:

     - add Media object
     - add CtrlVocab object
     - add inheritance of MetaObject for Annotation

  - package annotationdata.io:

     - complete debug of all file formats
     - add comments and documentation
     - add also some tests
     - add Media/CtrlVocab in some file formats
     - add Annotation Pro support of antx files (in API)

Components:

  - add Time Group Analyser (TGA) in Statistics
  - add Kappa estimation on labels of 2 tiers with the same number of intervals

Annotations:

  - New version of XRA: 1.2
  - Make XRA the default input/output file format


#### SPPAS-1.7.2 (2015-09-03)

Development:

  - updated XRA reader/writer to solve problems with upper/lower cases of elements
  - updated Elan reader to be compatible with format 2.8
  - updated Praat reader/writer for single/double quotes
  - support of antx files in the GUI
  - add the julius score in PhonAlign annotation (can be seen only if XRA)
  - remove tk dependencies


#### SPPAS-1.7.3 (2015-10-09)

Resources:

  - New word-based vocab for Cantonese
  - New word-based dict for Cantonese
  - New phoneme-based acoustic model for Cantonese

Development:

  - Descriptive statistics debugged for detailed panels.


#### SPPAS-1.7.4 (2015-11-06)

Resources:

  - Add a vocab for Portuguese
  - Add a dict for Portuguese
  - Add an acoustic model for Portuguese. It has to be noticed that
    it was constructed from French/Spanish/Italian models, not trained
    from data.

Samples:

  - Add Portuguese
  - Change some samples in various languages

Development:

  - Debug of the Tokenizer.


#### SPPAS-1.7.5 (2015-12-11)

Development:

  - Add vagueness to the annotation duration estimation
  - Bug correction while saving the procedure outcome report in the GUI

GUI:

  - Changed all pictures to remove the problem with colorset of some of them
  - Add a christmast theme for the pictures of tips
  - IPUscribe improvements:

     - add keyboard shortcuts to play/pause/stop the sound
     - add a new button to auto-play the sound

#### SPPAS-1.7.6 (2016-01-28)

Web site host has changed: <http://www.sppas.org/>

Development:

  - IPU segmentation:

     - bug correction with option "split into tracks"
     - new option to add or not add the IPU index of each IPU into the
        transcription tier

  - Tokenization:

     - bug correction in input tier selection
     - bug correction for replacements

Resources:

  - add a vocabulary of Korean
  - add an acoustic model for Korean (made from the English and the Taiwanese ones).

GUI:

  - DataRoamer: bug correction of "Duplicate"

Others:

  - Add a sample in Korean
  - Updated references to cite SPPAS in publications


#### SPPAS-1.7.7 (2016-03-30)

Resources:

  - Correction of errors in most of the acoustics models,
    for /@@/ and /dummy/ models
  - New vocabulary and pronunciation dictionary for Mandarin Chinese.

GUI:

  - Dialogs are customized
  - DataRoamer debug and changes: save buttons moved in the main toolbar.
  - HelpSystem is (welcome) back!

Development:

  - Add the API and a script to train acoustic models with HTK.
  - Add Kullback-Leibler distance estimator.
  - Add a script to compare 2 segmentations (of 2 tiers).
  - Classes of the package resources are debugged, improved and extended.
  - Automatic annotation alignment: bug correction if input starts by an
    empty interval.
  - `sppas.command` modified for MacOS-X (use python if python2 not available)
  - GUIs in `bin` directory are updated (test of python, wxpython, and so on).


#### SPPAS-1.7.8 (2016-05-05)

Resources:

  - Add a pronunciation mapping table `eng-fra.map`: to be used for the
  speech segmentation for French speakers reading an English text.

Development:

  - Phonetization is extended: it can take into account a mapping table of
    phones to generate new pronunciation variants.
  - Phonetization: use of minus instead of dots to separate phones as
    recommended in SAMPA standard.
  - Alignment is restructured and extended: it can take into account two
    acoustics models and mix them.
  - DataFilter is extended: Relations can be based on a delay between
    the intervals.
  - annotationdata: add Xtrans reader (extension: .tdf)
  - Code cleaning in several packages.

GUI:

  - Automatic annotations: improved log messages.


#### SPPAS-1.7.9 (2016-06-03)

GUI:

    - Some debug in SppasEdit
    - SndPlayer renamed AudioRoamer because new functionnalities were added:

        - See detailed information about each channel of an audio file
        - Can extract/save a channel or a fragment of channel
        - Can modify the framerate and the sample width of a channel
        - Can add a bias on amplitude values of a channel,
        - Can multiply amplitude values of a channel,
        - Can remove the offset of amplitude values of a channel.

Automatic annotations:

    - IPUs Segmentation fully re-implemented.

        - Silence/speech sehmentation improved for both quality and fastness
        - Package code cleaning and re-organization.


#### SPPAS-1.8.0 (2016-30-08)

GUI:

    - Design fully revisited and tested under Linux Mint, Windows 10 and MacOS 10.9

Development:

    - SLM package created: can estimate a statistical language model (without smooth method)

Automatic annotations:

    - Add a diagnosis of files
    - Tokenize extended: aplied also on alternative labels
    - Phonetize extended: aplied also on alternative labels
    - Alignment code cleaning and partly re-implemented
    - Add "Chunk alignment"
    - Use of a .ini file to configure each annotation instead of a sppas.conf file


#### SPPAS-1.8.1 (2016-28-11)

New: 

    - A few tutorials are available on the web site.

Automatic annotations:

    - Align: an ActivityDuration tier can be optionnally added.
    - Support of 3-columns tab-delimited files with .txt extension. It allows the compatibility with Audacity Label track files.
    - Acoustic models training validated.

Resources:

    - Catalan: new pronunciation dictionary and new acoustic model.



#### SPPAS-1.8.2 (2017-01-18)

Analysis:

    - debug of DataFilter

Resources:

    - French vocabulary and dictionary updated

Development:

    - new plugins package with a new plugin manager
    - GUI integration of this new plugins system
    - some unittest appended and all existing ones updated
    - annotationdata.io renamed annotationdata.aio
    - docstrings of some packages converted from epytext to reST syntax

GUI: 

    - DataStats, DataFilter and DataRoamer toolbars dont scroll anymore
    - Themes management changed.
    - Main font is managed by the Themes.



#### SPPAS-1.8.3 (2017-03-10)

Development:

    - Elan reader highly improved.



#### SPPAS 1.9 (2017-03-00)

Development:

    For the packages utils, term, structs, resources, presenters, plugins, 
    calculus and audiodata: the migration from python 2.7 to python > 3.0 
    is done:
        
        * xrange replaced by range
        * use items() instead of iteritems()
        * print is used as a function
        * add a class to make unicode in the same way in both versions
        * unittest verified, improved, etc.
    
    For the packages utils, term, structs, resources, plugins and calculus:

        - The migration from epydoc to reST syntax is started...
        - Code is re-written to be as PEP8-compatible as possible
        - Exceptions are separately managed
        - Internationalization of the messages

    Relative imports used as the standard way in python!


## the Modern period

... it will be the case when SPPAS will be based on Python 3.x (instead of 2.7)
and Phoenix instead of wxpython!


