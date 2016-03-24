## Scripting with Python


### Hello World!

We are going to create a very simple Python script and then run it.
First of all, create a new folder (on your Desktop for example); you
can name it "pythonscripts" for example.

Execute the python IDLE (available in the Application-Menu of your operating
system).

![The Python IDLE logo](./etc/img/python_idle.png)

Then, create a new empty file: 

- by clicking on "File" menu, then "New File", 
- or with the shortcut "CTRL"+N.

Copy the following code in this newly created file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
print 'Hello world!'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

![Hello world! in a Python script](./etc/screenshots/python_idle_00.png)

Then, save the file in the "pythonscripts" folder. 
By convention, Python source files end with a *.py* extension, 
so I suggest the name `01_helloworld.py`.

Notice that `main` (in the code above) is a function.  
A function does something. This particular function prints, or outputs 
to the screen, the text, or string, between apostrophes or quotation marks. 
We've decided to call this function main: the name main is just a convention.
We could have called it anything.

To execute the program, you can do one of:

* with the mouse: Click on the Menu "Run", then "Run module"
* with the keyboard: Press F5

The expected output is as follow:

![Output of the first script](./etc/screenshots/python_idle_01.png)

A better practice while writing scripts is to describe by who, what and why 
this script was done.
I suggest to create a skeleton for your future scripts, it is useful each time 
a new script will have to be written. 

Here is an example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
# ----------------------------------------------------------------------------
# Author: Me
# Date:   Today
# Brief:  Simple script to do nothing.
# ----------------------------------------------------------------------------

import os
import sys

# ----------------------------------------------------------------------------

def main():
    """ This is the main function to do something. """
    pass

# ----------------------------------------------------------------------------
# This is the python entry point:
# Here, we just ask to execute the main function.
if __name__ == '__main__':
    main()
# ----------------------------------------------------------------------------
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This ready-to-use script is available in the SPPAS package, 
its name is `skeleton.py`. 

In the example above, the main function is documented: documentation is the
text between """. In this chapter, all these "docstrings" follow a convention, 
named  "The Epytext Markup Language". 
Epytext is a simple lightweight markup language that lets you add
formatting and structure to docstrings. The software Epydoc uses that 
formatting and structure to produce nicely formatted API documentation.
For details, see:

> Epydoc web site: <http://epydoc.sourceforge.net/manual-epytext.html>



### Functions

#### Simple function

Now, we'll play with functions!
So, create a copy of the file `skeleton.py`, and add the following function
`print_vowels()`.
This function declare a list named `vowels`. Each item of the list is a string 
representing a vowel in French encoded in SAMPA (at the phonetic level). 
Of course, such list can be overridden with any other set of phonemes.
Then, the function print each item of the list, by means of a loop.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="21"}
def print_vowels():
    """ Print the list of French vowels on the screen. """
    vowels = [ 'a', 'e', 'E', 'i', 'o', 'u', 'y', '@', '2', '9', 'a~', 'o~', 'U~' ]
    for v in vowels:
        print v
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `main()` function must be changed: 
instead of printing 'Hello World!', it will call the newly created 
function `print_vowels()`.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="31"}
def main():
    """ This is the main function. """
    print_vowels()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Then, save the file in the "pythonscripts" folder and execute the program. 


>*Practice*: 
>Add a function to print plosives and call it in the main function
>(solution: 02_functions.py).

![Output of the second script](./etc/screenshots/python_idle_02.png)

 
One can also create a function to print glides, another one to print 
affricates, and so on.
Hum... this sounds a little bit fastidious!
Lets update, or refactor, our printing function to *make it more generic*. 


#### Function with parameters

There are times when we need to do something different with only slight 
variation each time. Rather than writing the same code with only minor 
differences over and over, we group the code together and use a mechanism 
to allow slight variations each time we use it.
A function is a smaller program with a specific job. In most languages 
they can be "passed" data, called parameters, which allow us to change 
the values they deal with.

Notice that the number of parameters of a function is not limited!

In the example, we can replace the `print_vowels()` function and the
`print_plosives()` function by a single function `print_list(mylist)`
where `mylist` can be any list containing strings or characters.
If the list contains other typed-variables (as int or float), they must
be converted to string to be printed out.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="21"}
def print_list(mylist, message=""):
    """
    Print a list on the screen.

    @param mylist (list) is the list to print
    @param message (string) is an optional message to print before each element 

    """

    for element in mylist:
        print message,str(element)

# ----------------------------------------------------------------------------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#### Function return values

Languages usually have a way to return information from a function, 
and this is called the return data. 
This is done with the `return` key-word. The function stops at this stage, even
if some code is following in the block.

In the following example, the function would return a boolean value (True if
the given string has no character).

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="21"}
def is_empty(mystr):
    """ Return True if mystr is empty. """
    return not len(mystr.strip())
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

>Practice: Add this funtion in a new script and try to print various lists
>(solution: 03_functions.py)

![Expected output of the 3rd script](./etc/screenshots/python_idle_03.png)


### Reading/Writing files

#### Reading data from a file

Now, we'll try to get data from a file. Create a new empty file with the 
following lines (and add as many lines as you want), then, save it with
the name "phonemes.csv" (by using UTF-8 encoding):

    occlusives ; b ; b 
    occlusives ; d ; d 
    fricatives ; f ; f 
    liquids ; l ; l 
    nasals ; m ; m 
    nasals ; n ; n 
    occlusives ; p ; p 
    glides ; w ; w 
    vowels ; a ; a 
    vowels ; e ; e 

The following statements are typical statements used to read the content 
of a file. The  first parameter of the function `open` is the file name, 
including the path (relative or absolute); and the second argument is the
opening mode ('r' is the default value, used for reading).

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="21"}
def main():
    f = open("C:\Users\Me\Desktop\pythonscripts\phonemes.csv", 'r')
    for l in f:
        # do something with the line stored in variable l
        print l
    f.close()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

See the file 04_reading_simple.py for the whole program and try-it
(do not forget to change the file name to your own file!).

Like any program... it exists more than one way to solve the problem.
The following is a more generic solution, with the ability to deal with 
various file encodings, thanks to the `codecs` library:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="21"}
def read_file(filename):
    """
    Read the whole file, return lines into a list.

    @param filename (string) Name of the file to read, including path.
    @return List of lines

    """
    with codecs.open(filename, 'r', encoding="utf8") as f:
        return f.readlines()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

In the previous code, the `codecs.open` functions got 3 arguments: the file 
name, the mode (in that case, 'r' means 'read'), and the encoding.
The `readlines()` function get each line of the file `f` and store it into 
a list.

The main function can be as follow:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="35"}
def main():
    """ This is the main function. """

    lines = read_file("C:\Users\Me\Desktop\pythonscripts\phonemes.csv")

    # before doing something, check the data!
    if not len(lines):
        print 'Hum... the file is empty!'
        sys.exit(1)

    # do something with the lines
    for l in lines:
        print l.strip()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

See the file 05_reading_file.py for the whole program, and try-it
(do not forget to change the file name to your own file!).

Notice that Python `os` module provides methods that can help you to perform 
file-processing operations, such as renaming and deleting files.
See Python documentation for details: <https://docs.python.org/2/>


#### Writing files

Writing a file requires to open it in a writing mode: 

* 'w' is the mode used to write; it will erase any existing file;
* 'a' is the mode used to append data in an existing file.

A file can be opened in an encoding and saved in another one. This could be
useful to write a script to convert the encoding of a set of files in a 
given forlder to UTF-8 for example. The following could help to create 
such a script:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="10"}
# getting all files of a given folder:
path = 'C:\Users\Me\data'
dirs = os.listdir( path )
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="15"}
# Converting encoding of a file:
file_stream = codecs.open(file_location, 'r', file_encoding)
file_output = codecs.open(file_location+'utf8', 'w', 'utf-8')

for l in file_stream:
    file_output.write(l)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 


### Dictionaries

A dictionary is another container type that can store any number of 
Python objects, including other container types. Dictionaries consist 
of pairs (called items) of keys and their corresponding values.
Each key is separated from its value by a colon (:), the items are 
separated by commas, and the whole thing is enclosed in curly braces. 
An empty dictionary without any items is written with just two curly 
braces, like this: {}.
To access dictionary elements, you can use the familiar square brackets 
along with the key to obtain its value.

The next example is a portion of a program that can be used to convert a list
of phonemes from SAMPA to IPA.

To get values from a dictionary, one way is to use directly `dict[key]`,
but it is required to test if key is really in dict, otherwise, Python will
stop the program and send an error.
Alternatively, the `get` function can be used, as `dict.get(key, default=None)`
where default is the value to return if the key is missing. In the previous
example, it is possible to replace `sampadict[phone]` by 
`sampadict.get(phone, phone)`.
Two other functions are useful while using dictionaries:

* dict.keys() return a list with the keys
* dict.values() return a list with values


### Exercises to practice

>Exercise 1: How many vowels are in a list of phonemes?
(solution: 06_list.py)

    
>Exercise 2: Write a SAMPA to IPA converter.
(solution: 07_dict.py)

    
>Exercise 3: Compare 2 sets of data using NLP techniques (Zipf law, Tf.Idf)
(solution: 08_counter.py)
    
