# ----------------------------------------------------------------------------
# Author: Brigitte Bigi
# Date: April,17th,2015
# Brief: Simple script to print a list of vowels.
# ----------------------------------------------------------------------------

# Python libraries:
import os
import sys


# ----------------------------------------------------------------------------
# Functions:
# ----------------------------------------------------------------------------

def is_empty(mystr):
    """ Return True if mystr is empty. """
    s = mystr.strip()
    return not len(s)


def print_list(mylist, message=""):
    """
    Print a list on the screen.

    @param mylist (list) is the list to print
    @param message (string) is an optional message to print before each element

    """
    for element in mylist:
        strelement = str(element)
        if not is_empty(strelement):
            print message,strelement
        else:
            print message,"Empty item."

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

vowels = [ 'a', 'e', 'E', 'i', 'o', 'u', 'y', '@', '2', '9', 'a~', 'o~', 'U~' ]
plosives = ['p', 't', 'k', 'b', 'd', 'g' ]
numbers = [ 1,2,'',3,4]

print_list(vowels,   "Vowel:   ")
print_list(plosives, "Plosive: ")
print_list(numbers,  "Number:  ")

# ----------------------------------------------------------------------------
