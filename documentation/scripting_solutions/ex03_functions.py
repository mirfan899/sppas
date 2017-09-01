#!/usr/bin python
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      Simple script to print lists.

""" 


def is_empty(string):
    """ Return True if the given string contains no characters.
    
    :param string: (str) a string to check
    :returns: bool
    
    """
    # Clean the string: remove tabs, carriage returns...
    s = string.strip()
    # Check the length of the cleaned string
    return len(s) == 0


def print_list(mylist, message=""):
    """ Print a list on the screen.

    :param mylist: (list) the list to print
    :param message: (str) an optional message to print before each item

    """
    for item in mylist:
        str_item = str(item)
        if is_empty(str_item) is False:
            print(message, str_item)
        else:
            print(message, "Empty item.")

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

if __name__ == '__main__':

    vowels = ['a', 'e', 'E', 'i', 'o', 'u', 'y', '@', '2', '9', 'a~', 'o~', 'U~']
    plosives = ['p', 't', 'k', 'b', 'd', 'g']
    numbers = [1, 2, "", 3, "4"]

    print_list(vowels,   "Vowel:   ")
    print_list(plosives, "Plosive: ")
    print_list(numbers,  "Number:  ")
