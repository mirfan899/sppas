## Phonetization

Phonetization, also called grapheme-phoneme conversion, is the process of 
representing sounds with phonetic signs.

SPPAS implements a dictionary based-solution which consists in storing a 
maximum of phonological knowledge in a lexicon. In this sense, this approach 
is language-independent. SPPAS phonetization process is the equivalent of a 
sequence of dictionary look-ups. 

The SPPAS phonetization takes as input an orthographic transcription previously
normalized (by the Tokenization automatic system or manually).
The name of this tier must contains one of the following strings:

- "tok" and "std"
- "tok" and "faked"

The first tier that matches is used (case insensitive search). 

The system produces a phonetic transcription. 

![Phonetization workflow](./etc/figures/phonworkflow.bmp)

Actually, some words can correspond to several entries in the dictionary 
with various pronunciations. These pronunciation variants are stored in the 
phonetization result. By convention, spaces separate words, minus separate 
phones and pipes separate phonetic variants of a word.
For example, the transcription utterance:

* Transcription: `The flight was 12 hours long.`
* Tokenization: `the flight was twelve hours long`
* Phonetization: `D-@|D-V|D-i: f-l-aI-t w-A-z|w-V-z|w-@-z|w-O:-z t-w-E-l-v aU-3:r-z|aU-r-z l-O:-N`

Many of the other systems assume that all words of the speech transcription
are mentioned in the pronunciation dictionary. On the contrary, SPPAS
includes a language-independent algorithm which is able to phonetize unknown
words of any language as long as a (minimum) dictionary is available!
If such case occurs during the phonetization process, a WARNING indicates
it in the Procedure Outcome Report. 

For details about the method to phonetize unknown tokens in SPPAS, 
refer to the following reference:

>**Brigitte Bigi (2013).**
>*A phonetization approach for the forced-alignment task*,
>3rd Less-Resourced Languages workshop, 6th Language & Technology Conference, Poznan (Poland).

Since the phonetization is only based on the use of a pronunciation dictionary,
the quality of such a phonetization only depends on this resource.
If a pronunciation is not as expected, it is up to the user to change it in
the dictionary. All dictionaries are located in the folder "dict" of
the "resources" directory.

SPPAS uses the same dictionary-format as proposed in VoxForge, 
i.e. the HTK ASCII format. Here is a piece of the `eng.dict` file:

        THE             [THE]           D @
        THE(2)          [THE]           D V
        THE(3)          [THE]           D i:
        THEA            [THEA]          T i: @
        THEALL          [THEALL]        T i: l
        THEANO          [THEANO]        T i: n @U
        THEATER         [THEATER]       T i: @ 4 3:r
        THEATER'S       [THEATER'S]     T i: @ 4 3:r z

The first column indicates the word, followed by the variant number (except for
the first one). The second column indicates the word between brackets; however
brackets can also be empty. The last columns are the succession of phones, 
separated by a whitespace.

