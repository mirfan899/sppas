## A gentle introduction to programming


### Introduction

This section includes examples in Python programming language.
You may want to try out some of the examples that come with the
description. In order to do this, execute the Python IDLE - 
available in the Application-Menu of your operating system),
and write the examples after the prompt ">>>".

![The Python IDLE logo](./etc/logos/python_idle.png)

To get information about the IDLE, get access to 
[the IDLE documentation](https://docs.python.org/2/library/idle.html)

Writing any program consists of writing statements so using a programming 
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
letters, whitespace and so on is very high. Recommendations for Python
language are available in the 
[PEP8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).


### Variables: Assignment and Typing

A *variable* is a name to give to a piece of memory with some information 
inside. Assignment is then the action of setting a variable to a value.
The equal sign (=) is used to assign values to variables.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
 >>>a = 1    
 >>>b = 1.0
 >>>c = "c"
 >>>cc = u"ç"
 >>>hello = "Hello world!"
 >>>vrai = True
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the previous example, `a`, `b`, `c`, `hello` and `vrai` are variables,
`a = 1` is a declaration.

![Variable declarations and print in the Python IDLE](./etc/screenshots/python_idle_example.png)

Assignments to variables with Python language can be performed with the 
following operators:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> a = 10   # simple assignment operator
>>> a += 2   # add and assignment operator, so a is 12
>>> a -= 7   # minus and assignment, so a is 5
>>> a *= 20  # multiply and assignment, so a is 100
>>> a /= 10  # divide and assignment, so a is 10
>>> a        # verify the value of a...
10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Basic Operators

Basic operators are used to use and/or manipulate variables. The 
following is the list of operators that can be used with Python, 
i.e. equal (assignment), plus, minus, multiply, divide:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> a = 10
>>> b = 20  # Assignment
>>> a + b   # Addition
>>> a - b   # Subtraction
>>> a * b   # Multiplication
>>> a / b   # Division
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Data types

The variables are of a data-type. For example, the declarations `a=1` and `a=1.0`
are respectively assigning an integer and a real number. In Python, the command 
`type` allows to get the type of a variable, like in the following:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> type(a)
<type 'int'>
>>> type(b)
<type 'float'>
>>> type(c)
<type 'str'>
>>> type(cc)
<type 'unicode'>
>>> type(vrai)
<type 'bool'>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following is a list of some fundamental data types, and their characteristics:

* *str*   String of characters
* *unicode*  Unicode string of characters
* *int*   Integer in range from -2147483648 to 2147483647
* *bool*  Boolean value, can take value `True` (=1) or `False` (=0)
* *float* Floating point number (max 15 digits)

Python is assigning data types dynamically. As a consequence, the result of the sum 
between an `int` and a `float` is a `float`. The next examples illustrate that 
the type of the variables have to be carefully managed. 

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> a = 10
>>> a += 0.
>>> a
10.0
>>> a += True
>>> a
11.0
>>> a += "a"
Traceback (most recent call last):
  File "<input>", line 1, in <module>
TypeError: unsupported operand type(s) for +=: 'float' and 'str'
>>> a = "a"
>>> a *= 5
>>> a
'aaaaa'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The type of a variable can be changed. This is called a "cast", like in
the following:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> a = 10
>>> b = 2
>>> a/b
5
>>> float(a) / float(b)
5.0
>>> a = 1
>>> b = 1 
>>> str(a) + str(b)
'11'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complex data types are often used to store variables sharing the same 
properties like a list of numbers, and so on. Common types in languages 
are lists/arrays and dictionaries. The following is the assignment of a 
list with name `fruits`, then the assignment of a sub-part of the list to
the `to_buy` list:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> fruits = ['apples', 'tomatoes', 'peers', 'bananas']
>>> to_buy = fruits[1:2]
>>> to_buy
['tomatoes']
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Conditions

Conditions aim to test whether a statement is True or False.
The statement of the condition can include a variable, or be a variable.
If the result of the condition is true and/or false, then a given action 
occurs. Statements of conditions are written with operators, as equal,
less than, greater than, etc.
The following shows examples of conditions/comparisons in Python. Notice that
the comparison of variables of a different data-type is possible (but not
recommended!).

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> var = 100
>>> if var == 100: 
...     print("Value of expression is 100.")
...
Value of expression is 100.

>>> if var == "100":
...     print("This message won't be printed out.")
...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Conditions can expressed in a more complex way like:
 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> if a == b:
...     print('a and b are equals')
... elif a > b:
...    print('a is greater than b')
... else:
...    print('b is greater than a')
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simple operators for comparisons are summarized in the next examples:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> a == b   # check if equals
>>> a != b   # check if different
>>> a > b    # check if a is greater than b
>>> a >= b   # check if a is greater or equal to b
>>> a < b    # check if a is lesser than b
>>> a <= b   # check if a is lesser or equal to b
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
>>> if a == "apples" and b == "peers":
...    print("You need to buy fruits.")

>>> if a == "apples" or b == "apples":
...    print("You already have bought apples.")

>>> if "tomatoas" not in to_buy:
...    print("You do not have to buy tomatoes.")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Loops

The `for` loop statement iterates over the items of any sequence. 
The next Python lines of code print items of a list on the screen:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> to_buy = ['fruits', 'viande', 'poisson', 'oeufs']
>>> for item in to_buy:
...    print(item)
...
fruits
viande
poisson
oeufs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A `while` loop statement repeatedly executes a target statement as long as a
given condition returns `True`. The following example prints exactly the same 
result as the previous one:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> to_buy = ['fruits', 'viande', 'poisson', 'oeufs']
>>> i = 0
>>> while i < len(to_buy):
...  print(to_buy[i])
...  i += 1
...
fruits
viande
poisson
oeufs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


### Dictionaries

A dictionary is a very useful data type. It consists of pairs of keys and 
their corresponding values.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> fruits = dict()
>>> fruits['apples'] = 3
>>> fruits['peers'] = 5
>>> fruits['tomatoas'] = 1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

`fruits['apples']` is a way to get the value - i.e. 3, of the `apple` key.
However, an error is sent if the key is unknown, like `fruits[bananas]`.
Alternatively, the `get` function can be used, like `fruits.get("bananas", 0)`
that returns 0 instead of an error.

The next example is showing how use a simple dictionary:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python}
>>> for key in ['apples', 'peers', 'tomatoes', 'babanas']:
...    value = fruits.get(key, 0)
...    if value < 3:
...        print("You have to buy new {:s}.".format(key))
...
You have to buy new tomatoes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


To learn more about data structures and how to manage them, get access to 
[the Python documentation](https://docs.python.org/2/tutorial/datastructures.html)

