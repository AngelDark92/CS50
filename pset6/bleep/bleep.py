from cs50 import get_string
from sys import argv
import string


def main():

    # checking for the length of argv
    if len(argv) == 2:

        # trying if the file opens
        try:

            # opening the file to a variable
            diction = open(argv[1], "r")

            # assigning every word in each line to a list
            lista = diction.readlines()
            diction.close()

            # defining clean_phrase as a list
            clean_phrase = []

            # getting the phrase to censor
            print("What message would you like to censor?")
            phrase = (get_string("")).split()

            # for each word in the phrase check it
            for word in phrase:

                # function check takes in the word and the list and appends it to the clean_phrase list
                clean_phrase.append(check(word, lista))

            # rejoins the phrase as per requirements with a space inbetween each word
            print(" ".join(clean_phrase))

        # if it doesn't open, it gives OSError which is caught with this
        except OSError:

            print("Are you sure the path to the file is the right one, and the file is readable?")
            exit(1)

    else:

        print("Usage: python bleep.py ~/dictionary")
        exit(1)


def check(word, lista):

    for words in lista:

        # for each word in list check if in-word is the same
        if word.lower() == words.strip():

            # output takes the length of the current word multiplied by *
            output = "*" * len(word)
            return output

    # if no word is found in the list return it as is
    return word


if __name__ == "__main__":
    main()
