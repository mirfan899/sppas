## Introduction

Since version 1.8.7, SPPAS implements an Application Programming Interface
(API), named *anndata*, to deal with annotated files. Previously, SPPAS was
based on another API named *annotationdata* which is still distributed in
the package but no longer updated or maintained.

*anndata* API is a free and open source Python library to access and search
data from annotated data of any of the supported formats (xra, TextGrid,
eaf...). It can either be used with the Programming Language Python 2.7
or Python 3.4+. This API is PEP8 and PEP257 compliant and the
internationalization of the messages is implemented (English and French are
available in the "po" directory).

In this chapter, it is assumed that a version of Python is installed and
configured. It is also assumed that the Python IDLE is ready-to-use.
For more details about Python, see:

> The Python Website: <http://www.python.org>

This chapter firstly introduces basic programming concepts, then it 
gradually introduces how to write scripts with Python. Those who are familiar
with programming in Python can directly go to the last section related to the 
description of the *anndata* API and how to use it in Python scripts.

This API can convert file formats like Elan’s EAF, Praat's TextGrid and 
others into a `sppasTranscription` object and convert this object into any of
these formats. This object allows unified access to linguistic data from 
a wide range sources.

    This chapter includes exercises. The solution scripts are included in
    the package directory *documentation*, folder *scripting_solutions*.
