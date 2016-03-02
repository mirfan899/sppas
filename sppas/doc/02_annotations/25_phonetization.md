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
with various pronunciations, all these variants are stored in the phonetization
result. By convention, spaces separate words, dots separate phones and pipes 
separate phonetic variants of a word. For example, the transcription utterance:

* Tokenization: `the flight was twelve hours long`
* Phonetization: `dh.ax|dh.ah|dh.iy f.l.ay.t w.aa.z|w.ah.z|w.ax.z|w.ao.z t.w.eh.l.v aw.er.z|aw.r.z l.ao.ng`

Many of the other systems assume that all words of the speech transcription
are mentioned in the pronunciation dictionary. On the contrary, SPPAS
includes a language-independent algorithm which is able to phonetize unknown
words of any language as long as a dictionary is available!
If such case occurs during the phonetization process, a WARNING mentions it
in the Procedure Outcome Report. 

For details, see the following reference:

>**Brigitte Bigi (2013).**
>*A phonetization approach for the forced-alignment task*,
>3rd Less-Resourced Languages workshop, 6th Language & Technology Conference, Poznan (Poland).

Since the phonetization is only based on the use of a pronunciation dictionary,
the quality of such a phonetization only depends on this resource.
If a pronunciation is not as expected, it is up to the user to change it in
the dictionary. All dictionaries are located in the sub-directory "dict" of
the "resources" directory.

SPPAS uses the same dictionary-format as proposed in VoxForge, 
i.e. the HTK ASCII format. Here is a peace of the eng.dict file:

        THE             [THE]           D @
        THE(2)          [THE]           D V
        THE(3)          [THE]           D i:
        THEA            [THEA]          T i: @
        THEALL          [THEALL]        T i: l
        THEANO          [THEANO]        T i: n @U
        THEATER         [THEATER]       T i: @ 4 3:r
        THEATER'S       [THEATER'S]     T i: @ 4 3:r z

The first column indicates the word, followed by the variant number (except for
the first one). The second column indicated the word between brackets. The last 
columns are the succession of phones, separated by a whitespace.
