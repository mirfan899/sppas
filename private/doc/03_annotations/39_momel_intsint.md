## Momel and INTSINT

### Momel (modelling melody)

Momel is an algorithm for the automatic modeling of fundamental frequency (F0)
curves using a technique called asymetric modal quadratic regression.

This technique makes it possible by an appropriate choice of parameters to 
factor an F0 curve into two components:

* a macro-prosodic component represented by a a quadratic spline function defined by a sequence of target points < ms, hz >.
* a micro-prosodic component represented by the ratio of each point on the F0 curve to the corresponding point on the quadratic spline function.

For details, see the following reference:

>**Daniel Hirst and Robert Espesser** (1993).
>*Automatic modelling of fundamental frequency using a quadratic spline function.*
>Travaux de l’Institut de Phonétique d’Aix. vol. 15, pages 71-85.

The SPPAS implementation of Momel requires a file with the F0 values
**sampled at 10 ms**. Two file formats are supported:

- ".PitchTier", from Praat.
- ".hz", from any tool. It is a file with one F0 value per line.


The following options can be fixed:

* Window length used in the "cible" method 
* F0 threshold: Maximum F0 value
* F0 ceiling: Minimum F0 value
* Maximum error: Acceptable ratio between two F0 values
* Window length used in the "reduc" method
* Minimal distance
* Minimal frequency ratio
* Eliminate glitch option: Filter f0 values before 'cible'


### Encoding of F0 target points using the "INTSINT" system

INTSINT assumes that pitch patterns can be adequately described using a 
limited set of tonal symbols, T,M,B,H,S,L,U,D (standing for : Top, Mid, Bottom, 
Higher, Same, Lower, Up-stepped, Down-stepped respectively) each one of which 
characterises a point on the fundamental frequency curve.

The rationale behind the INTSINT system is that the F0 values of pitch targets 
are programmed in one of two ways : either as absolute tones T, M, B which are 
assumed to refer to the speaker’s overall pitch range (within the current 
Intonation Unit), or as relative tones H, S, L, U, D assumed to refer only to 
the value of the preceding target point.

![INTSINT example](etc/images/INTSINT-tones.png)

The rationale behind the INTSINT system is that the F0 values of pitch targets 
are programmed in one of two ways : either as absolute tones T, M, B which are 
assumed to refer to the speaker’s overall pitch range (within the current 
Intonation Unit), or as relative tones H, S, L, U, D assumed to refer only to
the value of the preceding target point.

A distinction is made between non-iterative H, S, L and iterative U, D relative
tones since in a number of descriptions it appears that iterative raising or 
lowering uses a smaller F0 interval than non-iterative raising or lowering. 
It is further assumed that the tone S has no iterative equivalent since there 
would be no means of deciding where intermediate tones are located.

![](etc/screenshots/Momel-INTSINT.png)


>**D.-J. Hirst** (2011).
>*The analysis by synthesis of speech melody: from data to models*, 
>Journal of Speech Sciences, vol. 1(1), pages 55-83.


### Perform Momel and INTSINT with the GUI

Click on the Momel activation button, select the language and click 
on the "Configure..." blue text to fix options. And click on the INTSINT
activation button.


### Perform Momel and INTSINT with the CLI

`momel-intsint.py` is the program perform both momel and INTSINT.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: momel-intsint.py [options] -i file

optional arguments:
  -i file            Input file name (extension: .hz or .PitchTier)
  -o file            Output file name (default: stdout)
  --win1 WIN1        Target window length (default: 30)
  --lo LO            f0 threshold (default: 50)
  --hi HI            f0 ceiling (default: 600)
  --maxerr MAXERR    Maximum error (default: 1.04)
  --win2 WIN2        Reduct window length (default: 20)
  --mind MIND        Minimal distance (default: 5)
  --minr MINR        Minimal frequency ratio (default: 0.05)
  --non-elim-glitch
  -h, --help         Show the help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
