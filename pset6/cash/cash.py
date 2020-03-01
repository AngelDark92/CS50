from cs50 import get_float

# counter for the coins needed
counter = 0

# using a dictionary for the cents, just for fun
cents = {"penny": 1, "nickel": 5, "dime": 10, "quarter": 25}

while True:

    owed_ch = int(100 * get_float("Change owed: "))

    # continue code only if owed_ch is positive
    if owed_ch > 0:

        # it's done over many lines but it can be also done over just one

        counter += owed_ch//cents["quarter"]
        owed_ch = owed_ch % cents["quarter"]

        counter += owed_ch//cents["dime"]
        owed_ch = owed_ch % cents["dime"]

        counter += owed_ch//cents["nickel"]
        owed_ch = owed_ch % cents["nickel"]

        counter += owed_ch//cents["penny"]
        owed_ch = owed_ch % cents["penny"]

        """ or it can be written as
        counter = (owed_ch//cents["quarter"]) + ((owed_ch%cents["quarter"])//cents["dime"]) + (((owed_ch%cents["quarter"])%cents["dime"])//cents["nickel"]) + ((((owed_ch%cents["quarter"])%cents["dime"])%cents["nickel"])//cents["penny"])
        but admittedly it's much uglier"""

        # finally printing the counter
        print(counter)
        break