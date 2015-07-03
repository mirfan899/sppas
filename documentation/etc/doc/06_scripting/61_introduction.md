## Introduction

SPPAS implements an Application Programming Interface (API), named 
*annotationdata*, to deal with annotated files.
 
*annotationdata* API is a free and open source Python library to access and 
search data from annotated data. It can convert file formats like Elan’s EAF, 
Praat's TextGrid and others into a `Transcription` object and convert this 
object into anyone of these formats. This object allows unified access to 
linguistic data from a wide range sources.

In this chapter, we are going to create Python scripts with the SPPAS 
Application Programming Interface *annotationdata* and then run them. 
This chapter includes examples and some exercises to practice. Solutions 
of the exercises are included in the package sub-directory *documentation*, 
then *solutions*.

*annotationdata* is based on the Programming Language Python, version 2.7. 
This chapter firstly introduces basic programming concepts, then it will 
gradually introduce how to write scripts with Python. Those who are familiar 
with programming in Python can directly go to the last section related to the 
description of the *annotationdata* API and how to use it in Python scripts.

In this chapter, it is assumed that Python 2.7 is already installed and
configured. It is also assumed that the Python IDLE is ready-to-use.
For more details about Python, see:

> The Python Website: <http://www.python.org>
