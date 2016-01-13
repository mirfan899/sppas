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

def print_vowels():
    """ Print the list of French vowels on the screen. """
    vowels = [ 'a', 'e', 'E', 'i', 'o', 'u', 'y', '@', '2', '9', 'a~', 'o~', 'U~' ]
    for v in vowels:
        print "  ",v

def print_plosives():
    """ Print a list of plosives on the screen. """
    plosives = ['p', 't', 'k', 'b', 'd', 'g' ]
    for p in plosives:
        print "  ",p

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

print "French vowels: "
print_vowels()
print "French plosives: "
print_plosives()

# ----------------------------------------------------------------------------

