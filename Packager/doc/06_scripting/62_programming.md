## A gentle introduction to programming

Execute the Python IDLE - available in the Application-Menu of your operating
system) and write the examples of this section after the prompt.

![The Python IDLE logo](./etc/img/python_idle.png)


### Definitions

Writing a program consists of writing statements so using a programming 
language. A *statement* is often known as a line of code that can be one
of: 

- comment, 
- documentation,
- assignment, 
- conditions, 
- iterations, etc.

Lines of code are grouped in *blocks*. Depending on the programming 
language, blocks delimited by brackets, braces or by the indentation.

Each language has its own syntax to write these lines and the user has to
follow strictly this syntax for the program to be able to interpret the
program. However, the amount of freedom the user has to use capital 
letters, whitespace and so on is very high. Recommendations are 
available in the 
[Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).


### Comments and documentation

Comments are not required by the program to work. But comments are necessary!
Comments are expected to be appropriate, useful, relevant, adequate
and always reasonable.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 # This program is doing this and that.
 # It is under th terms of that license.
 # and I can continue to write what I want after the # symbol
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The documentation of a program complements the comments. They don't share
the same goal: comments are used in small programs but documentation is 
appended to comments for bigger programs and/or projects. Documentation can 
be automatically extracted and formatted thanks to dedicated tools. 
Documentation is useful for sharing the program. See the
[Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
for details.
Documentation must follow a convention like for example the markup language
[reST - reStructured Text](https://en.wikipedia.org/wiki/ReStructuredText).
Both conventions are used into SPPAS.


### Variables: Assignment and Typing

A *variable* is a name to give to a piece of memory of the with some 
information inside. Assignment is then the action of setting a variable
to a value.
In most languages, the equal sign (=) is used to assign values to variables.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 a = 1    
 b = 1.0
 c = 'c'
 hello = 'Hello world!'
 vrai = True
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the previous example, `a`, `b`, `c`, `hello` and `vrai` are variables,
`a = 1` is a declaration with a typed-statement.

![Variable declarations and print in the Python IDLE](./etc/screenshots/python_idle_example.png)

Here is a list of some fundamental data types, and their characteristics:

* *char*  Character and/or small integer, 1 byte (signed: -128 to 127 or unsigned: 0 to 255)
* *int*   Integer, 4 bytes (signed: -2147483648 to 2147483647 or unsigned:0 to 4294967295)
* *bool*  Boolean value, can take two values `True` or `False`
* *float* Floating point number, 4 bytes

Assignments with Python language can be performed with the following operators:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 a = 10   # simple assignment operator
 a += 10  # add and assignment operator
 a -= 10
 a *= 10
 a /= 10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Data types

Complex data types are often used to store data sharing the same properties
like a list of numbers, and so one.
Common types in languages are arrays, lists, dictionaries, trees, etc. 
The following is the assignment of a list then a sub-part of the list
to variables:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 fruits = ['apples', 'tomatoes', 'peers', 'apricots']
 to_buy = fruits[1:2]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Basic Operators

Basic operators are used to use and/or manipulate variables. The 
following is the list of operators that can be used with Python, 
i.e. equal (assignment), plus, minus, multiply, divide:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 a = 10
 b = 20  # Assignment
 a + b   # Addition
 a - b   # Subtraction
 a * b   # Multiplication
 a / b   # Division
 float(a) / float(b)  # try it! and compare with the previous one
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Conditions

Conditions aim to test whether a statement is true or false.
The statement of the condition can include a variable, or be a variable.
If the result of the condition is true and/or false, then a given action 
occurs. Statements of conditions are written with operators, as equal,
less than, greater than, etc.
In the following, we give example of conditions/comparisons in Python.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 var = 100
 if var == 100: 
     print("Value of expression is 100.")
 if van == "apples":
     print("Please buy apples the next time you'll go for some shopping.")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Conditions can expressed in a more complex way like:
 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 if a == b:
     print('a and b are equals')
 elif a > b:
    print('a is greater than b')
 else:
    print('b is greater than a')
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simple operators for comparisons are summarized in the next examples:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 a == b   # check if equals
 a != b   # check if different
 a > b    # check if a is greater than b
 a >= b   # check if a is greater or equal to b
 a < b    # check if a is lesser than b
 a <= b   # check if a is lesser or equal to b
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is also possible to use the following operators:

- `and`: called "Logical AND operator".
If both the operands are true then the condition becomes true.
- `or`: called Logical OR Operator.
If any of the two operands are non zero then the condition becomes true.
- `not` called Logical NOT Operator.
Use to reverses the logical state of its operand.
If a condition is true then Logical NOT operator will make false.
- `in`: evaluates to true if it finds a variable in the specified sequence
and false otherwise.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
if a == "apples" and b == "peers":
    print("You bought fruits...")
if a == "apples" or b == "apples":
    print("You already have bought apples."
if "tomatoas" not in to_buy:
    print("You do not have to buy tomatoes."
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Loops

The `for` loop statement iterates over the items of any sequence. 
The following Python program prints items of a list on the screen:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 to_buy = ['fruits', 'viande', 'poisson', 'oeufs']
 print("List of items to buy:")
 for item in to_buy:
    print(item)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A `while` loop statement repeatedly executes a target statement as long as a
given condition is true. The following example prints exactly the same result
as the previous one:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 to_buy = ['fruits', 'viande', 'poisson', 'oeufs']
 print("List of items to buy:")
 i = 0
 while i < len(to_buy):
     print(to_buy[i])
     i += 1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
