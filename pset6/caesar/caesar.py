from sys import argv
from cs50 import get_string
import string


while True:

    # checking if enough argv and that argv[1] is part of the digits
    if len(argv) == 2 and argv[1].isdigit():

        # creating a list to store all the characters in
        changed_str = []
        value = int(argv[1])

        if value > 0:

            # this will be the string to cipher
            stringhe = get_string("plaintext: ")

            for c in stringhe:

                # checking if every character in the string is lower or uppercase
                if c in string.ascii_lowercase:
                    num = ((ord(c) - 97 + value) % 26) + 97
                    c = str(chr(num))
                    changed_str.append(c)

                # if it is it will be modified according to the value entered in argv
                elif c in string.ascii_uppercase:
                    num = ((ord(c) - 65 + value) % 26) + 65
                    c = str(chr(num))
                    changed_str.append(c)

                else:
                    changed_str.append(c)

            # this will join the list back into a string
            stringhe = "".join(changed_str)

        # prints out the string
        print(f"ciphertext: {stringhe}")

        break

    else:

        print("Usage: python caesar.py k")
        exit(1)