## Scripting with Python

We are going to create simple Python scripts and then run them.
Create a new folder - on your Desktop for example;
with name "pythonscripts" for example.
Execute the python IDLE which is available in the Application-Menu 
of your operating system.

![The Python IDLE logo](./etc/img/python_idle.png)


### Hello World!

First of all, create a new empty file either by clicking on "File" 
menu, then "New File", or with the shortcut "CTRL"+N. 

Copy the following code in this newly created file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
print('Hello world!')
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

![Hello world! in a Python script](./etc/screenshots/python_idle_00.png)

Then, save the file in the "pythonscripts" folder. 
By convention, Python source files end with a *.py* extension, 
so the name `01_helloworld.py` could be fine.

To execute the program, you can do one of:

* with the mouse: Click on the Menu "Run", then "Run module"
* with the keyboard: Press F5

The expected output is as follow:

![Output of the first script](./etc/screenshots/python_idle_01.png)

A better practice while writing scripts is to describe by who, what and why 
this script was done. A good practice is to create a skeleton for any future 
script which has to be written. Such ready-to-use script is available in the 
SPPAS package with the name `skeleton.py`. 


### Functions

#### Simple function

A function does something: it stats with its definition then is followed by its
lines of code in a block.

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

At this stage, if a script including this function is executed, it will do... 
nothing! Actually, the function is created, but it must be invoked in the main 
function to be interpreted by Python. 
The new version is as follow:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="40"}
if __name__ == '__main__':
    print_vowels()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


>*Standalone Practice:* create a copy of the file `skeleton.py`, then
>make a function to print Hello World.
>(solution: 01_hello_world.py).

>*Standalone Practice*: 
>add a function to print plosives and call it in the main function
>(solution: 02_functions.py).

![Output of the second script](./etc/screenshots/python_idle_02.png)

 
One can also create a function to print glides, another one to print 
affricates, and so on. Hum... this sounds a little bit fastidious!
Lets update, or refactor, our printing function to *make it more generic*. 


#### Function with parameters

Rather than writing the same lines of code with only a minor difference
over and over, we can declare *parameters* to the function.
Notice that the number of parameters of a function is not limited!

In the example, we can replace the `print_vowels()` function and the
`print_plosives()` function by a single function `print_list(mylist)`
where `mylist` can be any list containing strings or characters.
If the list contains other typed-variables like numerical values, they 
must be converted to string to be printed out.
This can result in the following function:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="27"}
def print_list(mylist, message=""):
    """ Print a list on the screen.

    :param mylist: (list) is the list to print
    :param message: (string) is an optional message to print before each element 

    """
    for item in mylist:
        print("{0} {1}".format(message, item))
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#### Function return values

Functions are used to do a specific job and the result of the function can be
captured by the program.
In the following example, the function would return a boolean value, i.e. 
True if the given string has no character.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="21"}
def is_empty(mystr):
    """ Return True if mystr is empty. """
    
    return len(mystr.strip()) == 0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

>Practice: Add this function in a new script and try to print various lists
>(solution: 03_functions.py)

![Expected output of the 3rd script](./etc/screenshots/python_idle_03.png)


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

>*Standalone Practice:* Add this lines of code in a new script and try it
>(solution: 04_reading_simple.py)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines startFrom="21"}
fp = open("C:\Users\Me\Desktop\pythonscripts\phonemes.csv", 'r')
for line in fp:
    # do something with the line stored in variable l
    print(line.strip())
f.close()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

The following is a more generic solution, with the ability to deal with 
various file encodings, thanks to the `codecs` library:

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

>*Standalone Practice:* Write a script to print the content of a file
>(solution: 05_reading_file.py)

Notice that Python `os` module provides useful methods to perform 
file-processing operations, such as renaming and deleting.
See Python documentation for details: <https://docs.python.org/2/>


#### Writing files

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


### Dictionaries


A dictionary is a very useful data type. It consists of pairs of keys and 
their corresponding values.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
fruits = dict()
fruits['apples'] = 3
fruits['peers'] = 5
fruits['tomatoas'] = 1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

`fruits['apples']` is a way to the the value - i.e. 3, of the `apple` key.
However, an error is sent if the key is unknown, like `fruits[bananas]`.
Alternatively, the `get` function can be used, like `fruits.get("bananas", 0)`
that will return 0.

The next example is showing how use a dictionary:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
for key in ['apples', 'peers', 'tomatoes', 'babanas']:
    value = fruits.get(key, 0)
    if value < 3:
        print("You have to buy new {:s}".format(key))
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Other examples are available in the Python documentation:
<https://docs.python.org/2/tutorial/datastructures.html>


### Exercises to practice

>Exercise 1: How many vowels are in a list of phonemes?
(solution: 06_list.py)

    
>Exercise 2: Write a X-SAMPA to IPA converter.
(solution: 07_dict.py)

    
>Exercise 3: Compare 2 sets of data using NLP techniques (Zipf law, Tf.Idf)
(solution: 08_counter.py)
