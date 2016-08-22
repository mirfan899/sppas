## What are SPPAS resources and where they come from?

### Overview

All automatic annotations included in SPPAS are implemented with
language-independent algorithms... this means that adding a new language
in SPPAS only consists in adding resources related to the annotation
(like lexicons, dictionaries, models, set of rules, etc).

All available resources to perform automatic annotations are located in
the sub-directory 'resources'. There are 5 sub-directories:

- Lexicon (list of words used during Tokenization) are located in the *vocab* sub-directory.
- A list of replacements to perform during tokenization in the *repl* sub-directory.
- Pronunciation dictionaries (used during Phonetization) are located in the *dict* sub-directory.
- The acoustic models (used during Alignment) are located in the *models* directory.
- The Syllabification configuration files are located in the *syll* directory.

> All resources can be edited, modified, changed or deleted by any user.

> Caution: all the files are in UTF-8, and this encoding must not be changed.

The language names are based on the ISO639-3 international standard.
See <http://www-01.sil.org/iso639-3/> for the list of all languages and codes.
Here is the list of some available languages in SPPAS resources:

- French: fra
- English: eng
- Spanish: spa
- Italian: ita
- Japanese: jpn
- Mandarin Chinese: cmn
- Southern Min (or Min Nan): nan
- Cantonese: yue
- Polish: pol
- Catalan: cat
- Portuguese: por

SPPAS can deal with a new language by simply adding the language resources
to the appropriate sub-directories.
Of course, file formats must corresponds to which expected by SPPAS!
Lexicon and dictionaries can be edited/modified/saved with a simple-editor as
**Notepad++** for example (*under Windows: above all, don't use the windows' notepad*).
Idem for the syllabification rules.

The only step in the procedure which is probably beyond the means of a linguist
without external aid is the creation of a new acoustic model when it does not
yet exist for the language being analysed. This only needs to carried out once
for each language, though, and we provide detailed specifications of
the information needed to train an acoustic model on an appropriate set of
recordings and dictionaries or transcriptions. Acoustic models obtained by such
a collaborative process will be made freely available to the scientific
community.

The current acoustic models can be improved too (except for eng and jpn):
send your data (wav and transcription files) to the author. Notice that
such data will not be published in any form without your authorization.
They will be included in the training procedure to create a new (and better)
acoustic model, that will be distributed in the next version of SPPAS.


### About the phonemes

Most of the dictionaries are using the international standard
X-SAMPA to represent phonemes.
See <https://en.wikipedia.org/wiki/X-SAMPA> for details.
The list of all phonemes for each language is available in this documentation,
in the section related to a given language.

In addition, all models (except eng, jpn and yue) include the following fillers:

- dummy: untranscribed speech
- gb: garbage
- @@: laughter


### How to add a new language

1. Dictionary and lexicon:

    1.1 Copy the phonetic dictionary `LANG.dict` in the `dict` directory

    1.2 Copy the vocabulary list `LANG.vocab` in the `vocab` directory

2. Create a directory `models/models-LANG`; then copy the acoustic model
in this directory

3. Optionally, copy the file `syllConfig-LANG.txt` in the syll directory.

Required Input Data formats:

- The dictionary is HTK ASCII, like: word [word] phon1 phon2 phon3
Columns are separated by spaces.
- Acoustic models are in HTK ASCII format (16bits,16000hz).

Notice that the Graphical User Interface dynamically creates the list of
available languages by exploring the sub-directory "resources" included
in the SPPAS package. This means that all changes in the "resources" directory
will be automatically take into account.
