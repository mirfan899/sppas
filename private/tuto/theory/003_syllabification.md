# Syllables segmentation

-------------------------------

### Data preparation

* Time-aligned phonemes

![](./etc/screenshots/CM-extract-palign.png)

-------------------------------

## Expected result

* Time-aligned syllables

![](./etc/screenshots/CM-extract-salign.png)

* IMPORTANT: Syllabification was fully re-implemented in version 1.9.7 
and the displayed result has not been updated

-----------------

### Syllabification: my approach

* A rule-based system to cluster phonemes into syllables
* Rules available for:
    - French
    - Italian
    - Polish

* This phoneme-to-syllable segmentation system is based on 2 main principles:
    1. a syllable contains a vowel, and only one;
    2. a pause is a syllable boundary.

-----------------

### Syllabification: my approach (continued)

* Phonemes are grouped into classes
* Classes for both French and Italian:
    - V - Vowels, 
    - G - Glides,
    - L - Liquids,
    - P - Plosives, 
    - F - Fricatives,
    - N - Nasals.

-----------------

### Syllabification: my approach (continued)

* Fix rules to find the boundaries between two vowels
    - general rules with V and C
        - VCV => V.CV
        - VCCV => VC.CV
    - exception rules based on the classes
        - VLGV => V.LGV
        - VPGV => V.PGV
    - other rules based on the phonemes themselves
    
------------------

### Syllabification: resources

* A file with:
    - the list of phonemes and the corresponding class
    - the list of all rules 
* Current languages:
    - French:  10 exception rules; 6 phoneme-based rules
    - Italian: 11 exception rules; 1 phoneme-based rule
    - Polish:  50 exception rules; 337 phoneme-based rules

------------------

### Syllabification of French: reference

    Brigitte Bigi, Christine Meunier, Irina Nesterenko and Roxane Bertrand (2010). 
    Automatic detection of syllable boundaries in spontaneous speech.
    Language Resource and Evaluation Conference, pages 3285-3292, La Valetta, Malte.

![](./etc/screenshots/syllabification_fra_paper.png)

-----------------

### Syllabification of Italian: reference

    Brigitte Bigi and Caterina Petrone (2014).
    A generic tool for the automatic syllabification of Italian.
    In Proceedings of the First Italian Conference on Computational Linguistics CLiC-it 2014 and 
    of the Fourth International Workshop EVALITA 2014, pp. 73–77, Pisa, Italy.

![](./etc/screenshots/syllabification_ita_paper.png)

-----------------

### Syllabification of Polish: reference

    Brigitte Bigi and Katarzyna Klessa (2015).
    Automatic Syllabification of Polish.
    In 7th Language and Technology Conference: Human Language Technologies as a Challenge for 
    Computer Science and Linguistics, pp. 262–266, Poznan, Poland.

![](./etc/screenshots/syllabification_pol_paper.png)

-------------------------------

##

[Back to tutorials](tutorial.html)
