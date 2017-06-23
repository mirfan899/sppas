#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Simple script to print lists.

""" 

def is_empty(mystr):
    """ Return True if mystr is an empty string.
    
    @param mystr (str) is a string
    @return bool 
    
    """
    s = mystr.strip()
    return len(s) == 0


def print_list(mylist, message=""):
    """ Print a list on the screen.

    @param mylist (list) is the list to print
    @param message (string) is an optional message to print before each element

    """
    for element in mylist:
        strelement = str(element)
        if not is_empty(strelement):
            print(message,strelement)
        else:
            print(message,"Empty item.")

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

vowels = ['a', 'e', 'E', 'i', 'o', 'u', 'y', '@', '2', '9', 'a~', 'o~', 'U~']
plosives = ['p', 't', 'k', 'b', 'd', 'g']
numbers = [1, 2, "", 3, "4"]

print_list(vowels,   "Vowel:   ")
print_list(plosives, "Plosive: ")
print_list(numbers,  "Number:  ")

# ----------------------------------------------------------------------------
