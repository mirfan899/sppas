## Scripting with Python

This section describes how to create simple Python lines of code in 
separated files commonly called *scripts*, and run them.
Some practical exercises, appropriate to the content of each action, are
proposed and test exercises are suggested at the end of the section.

To practice, you have first to create a new folder in your computer 
- on your Desktop for example; with name "pythonscripts" for example,
and to execute the python IDLE.

For an advanced use of Python, the installation of a dedicated IDE is very
useful. SPPAS is developed with PyCharm:
See [the PyCharm Help webpage](https://www.jetbrains.com/help/pycharm/meet-pycharm.html)



### Comments and documentation

Comments are not required by the program to work. But comments are necessary!
Comments are expected to be appropriate, useful, relevant, adequate
and always reasonable.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 # This script is doing this and that.
 # It is under the terms of a license.
 # and I can continue to write what I want after the # symbol
 # except that it's not the right way to tell the story of my life
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The documentation of a program complements the comments. Both are not sharing
the same goal: comments are used in all kind of programs but documentation is 
appended to comments for the biggest programs and/or projects. Documentation 
is automatically extracted and formatted thanks to dedicated tools. 
Documentation is required for sharing the program. See the
[Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
for details.
Documentation must follow a convention like for example the markup language
[reST - reStructured Text](https://en.wikipedia.org/wiki/ReStructuredText).
Both conventions are used into SPPAS API, programs and scripts.


### Getting started with scripting in Python

In the IDLE, create a new empty file either by clicking on "File" 
menu, then "New File", or with the shortcut "CTRL"+N. 

Copy the following line of code in this newly created file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
print("Hello world!")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

![Hello world! in a Python script](etc/screenshots/python_idle_00.png)

Then, save the file in the "pythonscripts" folder. 
By convention, Python source files end with a *.py* extension, 
and so the name `01_helloworld.py` could be fine.

To execute the program, you can do one of:

* with the mouse: Click on the Menu "Run", then "Run module"
* with the keyboard: Press F5

The expected output is as follow:

![Output of the first script](etc/screenshots/python_idle_01.png)

A better practice while writing scripts is to describe by who, what and why 
this script was done. A nifty trick is to create a skeleton for any future 
script that will be written. Such ready-to-use script is available in the 
SPPAS package with the name `skeleton.py`. 


### Blocks

Blocks in Python are created from the indentation. Tab and spaces can be used
but using spaces is recommended.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>>if a == 3:
...    # this is a block using 4 spaces for indentation
...    print("a is 3")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Functions

#### Simple function

A function does something: it stats with its definition then is followed by
its lines of code in a block.

Here is an example of function:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="27"}
def print_vowels():
    """ Print the list of French vowels on the screen. """
    
    vowels = ['a', 'e', 'E', 'i', 'o', 'u', 'y', '@', '2', '9', 'a~', 'o~', 'U~']
    print("List of French vowels:")
    for v in vowels:
        print(v)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What the `print_vowels()` function is doing?
This function declares a list with name `vowels`. Each item of the list is a 
string representing a vowel in French encoded in X-SAMPA. Of course, this list 
can be overridden with any other set of strings. The next line prints
a message. Then, a loop prints each item of the list.

At this stage, if a script with this function is executed, it will do...
nothing! Actually, the function is created, but it must be invoked in the main 
function to be interpreted by Python. 
The `main` is as follow:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="34"}
if __name__ == '__main__':
    print_vowels()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


>*Practice:* create a copy of the file `skeleton.py`, then
>make a function to print "Hello World!".
>(solution: ex01_hello_world.py).

>*Practice*: 
>Create a function to print plosives and call it in the main function
>(solution: ex02_functions.py).

![Output of the second script](etc/screenshots/python_idle_02.png)

 
One can also create a function to print glides, another one to print 
affricates, and so on. Hum... this sounds a little bit fastidious!


#### Function with parameters

Rather than writing the same lines of code with only a minor difference
over and over, we can declare *parameters* to the function to *make it
more generic*.
Notice that the number of parameters of a function is not limited!

In the example, we can replace the `print_vowels()` function and the
`print_plosives()` function by a single function `print_list(mylist)`
where `mylist` can be any list containing strings or characters.
If the list contains other typed-variables like numerical values, they 
must be converted to string to be printed out.
This can result in the following function:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="27"}
def print_list(mylist, message="  -"):
    """ Print a list on the screen.

    :param mylist: (list) the list to print
    :param message: (string) an optional message to print before each element

    """
    for item in mylist:
        print("{:s} {:s}".format(message, item))
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#### Function return values

Functions are used to do a specific job and the result of the function can be
captured by the program. In the following example, the function would return
a boolean value, i.e. True if the given string has no character.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="27"}
def is_empty(mystr):
    """ Return True if mystr is empty. """
    
    return len(mystr.strip()) == 0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

>*Practice:* Add this function in a new script and try to print various lists
>(solution: ex03_functions.py)

![Expected output of the 3rd script](etc/screenshots/python_idle_03.png)


### Reading/Writing files

#### Reading data from a file

Now, we'll try to get data from a file. Create a new empty file with the 
following lines - and add as many lines as you want; then, save it with
the name "phonemes.csv" by using UTF-8 encoding:

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
of a file. The first parameter of the `open` function is the name of the file, 
including the path (relative or absolute); and the second argument is the
opening mode ('r' is the default value, used for reading).

>*Practice:* Add these lines of code in a new script and try it
>(solution: ex04_reading_simple.py)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="21"}
fp = open("phonemes.csv", 'r')
for line in fp:
    # do something with the line stored in variable l
    print(line.strip())
f.close()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

The following is a solution with the ability to deal with various file
encodings, thanks to the `codecs` library:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="21"}
def read_file(filename):
    """ Get the content of file.

    :param filename: (string) Name of the file to read, including path.
    :returns: List of lines

    """
    with codecs.open(filename, 'r', encoding="utf8") as fp:
        return fp.readlines()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

In the previous code, the `codecs.open` functions got 3 parameters: 
the name of the file, the mode to open, and the encoding. The `readlines()` 
function gets each line of the file and store it into a list.

>*Practice:* Write a script to print the content of a file
>(solution: ex05_reading_file.py)

Notice that Python `os` module provides useful methods to perform 
file-processing operations, such as renaming and deleting.
See Python documentation for details: <https://docs.python.org/2/>


#### Writing data to a file

Writing a file requires to open it in a writing mode: 

* 'w' is the mode to write data; it will erase any existing file;
* 'a' is the mode to append data in an existing file.

A file can be opened in an encoding and saved in another one. This could be
useful to write a script to convert the encoding of a set of files. 
The following could help to create such script:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="10"}
# getting all files of a given folder:
path = 'C:\Users\Me\data'
dirs = os.listdir( path )
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="15"}
# Converting the encoding of a file:
file_stream = codecs.open(file_location, 'r', file_encoding)
file_output = codecs.open(file_location+'utf8', 'w', 'utf-8')

for line in file_stream:
    file_output.write(line)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 


### Python tutorials

Here is a list of web sites with tutorials, from the easiest to the most
complete:

1. [Learn Python, by DataCamp](http://www.learnpython.org/)
2. [Tutorial Points](https://www.tutorialspoint.com/python/)
3. [The Python documentation](https://docs.python.org/2/tutorial/)


### Exercises to practice

>Exercise 1: How many vowels are in a list of phonemes?
(solution: ex06_list.py)

    
>Exercise 2: Write a X-SAMPA to IPA converter.
(solution: ex07_dict.py)


>Exercise 3: Compare 2 sets of data using NLP techniques (Zipf law, Tf.Idf)
(solution: ex08_counter.py)
