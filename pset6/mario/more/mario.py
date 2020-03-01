from cs50 import get_int


while True:
    n = int(get_int("Height: "))
    y = n - 1
    if n > 0 and n < 9:

        # did not want to use many for loops
        for i in range(1, n+1):

            #  so I ended up concatenating strings in only one loop
            print((y*" ") + (i*"#") + ("  ") + (i*"#"))
            y -= 1

        break