## Getting and installing


### Websites

In the past, SPPAS - Automatic Annotation of Speech, was hosted by 
"Laboratoire Parole et Langage" (see <http://www.lpl-aix.fr>.
SPPAS is hosted by Speech and Language Data Repository (SLDR), since
January 2015, and is located at the following URL:

<http://sldr.org/sldr000800/preview>


The source code with recent stable releases is now migrated on github. 

<https://github.com/brigittebigi/>

From this website, anyone can download the development version, 
contribute, send comments and/or declare an issue.


### Dependencies

On the main website, you will find information about the software requirements.
In fact, other programs are required for SPPAS to operate. Of course,
they must be installed before using SPPAS, and *only once*.
This operation takes from 5 to 15 minutes depending on the operating system.
The following software are required:

1. Python, version 2.7.x
2. wxPython >= 3.0
3. julius >= 4.1

An installation guide is available on the website, depending on your
operating system. **Please, closely follow the instructions.**
Administrator rights are required to perform these installations. 


### Download and install SPPAS

The website lets to go to the Download Page to download a new version or 
Subscribe to the User's group.

SPPAS is ready to run, so it does not need elaborate installation, except for
its dependencies (other software required for SPPAS to work properly).
All you need to do is to copy the SPPAS package from the website to somewhere
on your computer. Preferably, choose *a location without spaces nor accentuated 
characters in the name of the path*.  

The SPPAS package is compressed and zipped, so you will need to
*decompress and unpack* it once you've got it.

There is a unique version of SPPAS which does **not depend** on your operating
system. The only obvious difference depending on the system is how it looks
on the computer screen.

![Operating systems](./etc/logos/systemes.jpg)


### The SPPAS package

Unlike many other software, SPPAS is not what is called a "black box". 
Instead, everything is done so that users can check / change operation.
It is particularly suitable for automatic annotations. It allows any user 
to adapt automatic annotations to its own needs.

The package of SPPAS is then a folder with content as files and sub-folders. 

![SPPAS Package content](./etc/screenshots/explorer-sppas-folder.png)

The SPPAS package contains:

- the `README.txt` file, which aims to be read by users!
- the files `sppas.bat` and `sppas.command` to execute the Graphical User Interface of SPPAS
- the `resources` used by automatic annotations (lexicons, dictionaries, ...)
- the `samples` are sets of annotations freely distributed to test SPPAS
- the `sppas` directory contains the program itself
- the `documentation`, which contains:

    - the file `CHANGES.txt` is a Release History
      It shows an overview of the differences between the succeeding versions of SPPAS
    - the copyright and a copy of the licenses
    - the `documentation in PDF`
    - the slides of the document `SPPAS for Dummies`
    - the `references` sub-folder includes PDF files of some publications about SPPAS
    - the `solutions` of the exercises proposed in the chapter "Scripting with Python and SPPAS"
    - the `etc` directory is for internal use: never modify or remove it!


### Update

SPPAS is constantly being improved and new packages are published frequently
(about 10 versions a year). It is important to update regularly in order
to get the latest functions and corrections.

Updating SPPAS is very (very very!) easy and fast:

1. Optionally, put the old package into the Trash,
2. Download and unpack the new version.
