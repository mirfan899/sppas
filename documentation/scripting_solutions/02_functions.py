#!/usr/bin python
"""

@author:       Brigitte Bigi
@date:         2016-May-07
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2016  Brigitte Bigi

@summary:      Simple script to print(phonetics.

""" 

def print_vowels():
    """ 
    Print the list of French vowels on the screen. 
    
    """
    print("a")
    print("e")
    print("E")
    print("i")
    print("o")
    print("u")
    print("y")
    print("@")
    print("2")
    print("9")
    print("a~")
    print("o~")
    print("U~")


def print_plosives():
    """ 
    Print a list of plosives on the screen. 
    
    """
    print("p")
    print("t")
    print("k")
    print("b")
    print("d")
    print("g")

# ----------------------------------------------------------------------------

def main():
    """ 
    This is the main function. 
    
    """
    print("French vowels: ")
    print_vowels()
    
    print("French plosives: ")
    print_plosives()


if __name__ == '__main__':
    main()

# ----------------------------------------------------------------------------

