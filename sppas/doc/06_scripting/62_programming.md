## A gentle introduction to programming

This section is partially made of selected parts of *the Python website*
and *wikipedia*.


### Definitions

*Programming* is the process of writing instructions for computers to produce
software for users. More than anything, it is a creative and problem-solving
activity. Any problem can be solved in a large number of ways.

An *algorithm* is the step-by-step solution to a certain problem:
algorithms are lists of *instructions* which are followed step by step,
from top to bottom and from left to right.  To practice writing programs
in a programming language, it is required first to think of a the problem
and consider the logical solution before writing it out.

Writing a program is done so using a programming language. Thankfully even
though some languages are vastly different than others, most share a lot of
common ground, so that once anyone knows his/her first language, other
languages are much easier to pick up.

Any program is made of statements.
A *statement* is more casually (and commonly) known as a line of code
is the smallest standalone element which expresses some action to be carried
out while executing the program.
It can be one of: comment, assignment, conditions, iterations, etc.
Most languages have a fixed set of statements defined by the language.s

Lines of code are grouped in *blocks*.
Blocks are delimited by brackets, braces or by the indentation
(depending on the programming language).

The prompt indicates the system is ready to receive input. Most of times, it is
represented by '>'. In the following, the prompt is not mentioned.


### Comments and blocks

Comments are not required by the program to work. But comments are necessary!
It is commonly admitted that about 25% to 30% of lines of a program must be
comments.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 # this is a comment in python, bash and others.
 # I can write what I want after the # symbol :-)~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Variables: Assignment and Typing

A *variable* in any programming language is a named piece of computer memory,
containing some information inside. When declaring a variable, it is usually
also stated what kind of data it should carry.
Assignment is setting a variable to a value.
Dynamically typed languages, such as Python, allow automatic conversions
between types according to defined rules.

Python variables do not have to be explicitly declared:
the declaration happens automatically when a value is assigned to a variable.
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

Here is a list of some fundamental data types, and their characteristics:

* *char*  Character and/or small integer, 1 byte (signed: -128 to 127 or unsigned: 0 to 255)
* *int*   Integer, 4 bytes (signed: -2147483648 to 2147483647 or unsigned:0 to 4294967295)
* *bool*  Boolean value, can take two values `True` or `False`
* *float* Floating point number, 4 bytes

Notice that the number `0` represents the boolean value `False`.

Assignments are performed with *operators*.
Python Assignment Operators are:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 a = 10   # simple assignment operator
 a += 10  # add and assignment operator
 a -= 10
 a *= 10
 a /= 10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notice that a Character is a single letter, number, punctuation or other value;
and a String is a collection of these character values, often manipulated as
if it were a single value.

Complex data types are often used, for example: arrays, lists, tree,
hash-tables, etc. For example, with Python:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 lst = ['a', 'bb', 'ccc', 'dddd', 'eeeee' ]
 sublst = lst[1:2]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Basic Operators

Python Arithmetic Operators:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 a = 10
 b = 20
 a + b  # Addition
 a - b  # Subtraction
 a * b  # Multiplication
 a / b  # Division
 float(a) / float(b) # try it! and compare with the previous one
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Conditions

Decision making structures require that the programmer specify one or more
conditions to be evaluated or tested by the program. The condition statement
is a simple control that tests whether a statement is true or false.
The condition can include a variable, or be a variable.
If the condition is true, then an action occurs.
If the condition is false, nothing is done.

Conditions are performed with the help of comparison operators, as equal,
less than, greater than, etc.

In the following, we give example of conditions/comparisons in Python.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 var = 100
 if var == 100: print "Value of expression is 100"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python programming language assumes any non-zero and non-null values as `True`,
and if it is either zero or null, then it is assumed as `False` value.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 if a == b:
     print 'equals'
 elif a > b:
    print 'a greater than b'
 else:
    print 'b greater than a'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python Comparison Operators:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 a == b  # check if equals
 a != b  # check if different
 a > b   # check if a is greater than b
 a >= b  # check if a is greater or equal to b
 a < b
 a <= b
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Other Python Operators:

* `and` Called Logical AND operator.
If both the operands are true then the condition becomes true.
* `or` Called Logical OR Operator.
If any of the two operands are non zero then the condition becomes true.
* `not` Called Logical NOT Operator.
Use to reverses the logical state of its operand.
If a condition is true then Logical NOT operator will make false.
* `in` Evaluates to true if it finds a variable in the specified sequence
and false otherwise.


### Loops

A "loop" is a process in which a loop is initiated until a condition has
been met.

A `while` loop statement repeatedly executes a target statement as long as a
given condition is true.

The `for` loop has the ability to iterate over the items of any sequence,
such as a list or a string. The following Python program prints items of
a list on the screen:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 l = ['fruits', 'viande', 'poisson', 'oeufs']
 for item in l:
    print item
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
