#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define BLOCK 512

// the array needs to be of type byte in order for the expression to work
typedef uint8_t BYTE;

int main(int argc, char *argv[])
{
    // ensure we have 2 arguments
    if (argc != 2)
    {
        fprintf(stderr, "Usage: ./recover (name).raw. \n");
        return 1;
    }

    char *file = argv[1];

    FILE *input = fopen(file, "r");

    // check if file is accessible
    if (input == NULL)
    {
        fprintf(stderr, "The file could not be opened.");
        return 2;
    }



    //initialising buffer array
    BYTE found[512];

    // initialising count for found jpegs
    int jpeg_found = 0;

    // bool value for when start of JPEG has been found
    bool startJPEG = false;

    // variable for name of file in sprintf, needs 8 char spaces
    char name[8];

    // output file
    FILE *output = NULL;

    // contunue loop until end of file
    while (true)
    {

        //read 512 bytes into buffer, returns 0 when no more bytes
        size_t condition = fread(found, 1, BLOCK, input);

        if (condition == 0)
        {
            // break out of loop if it's end of file
            break;
        }

        //start of jpg found?
        // remember found[3] & 0xf0 will return the "anded" bits between the two and compare them to the final 0xe0
        // this accounts for all the possibilities of 0xe... possible for the start of a jpeg.
        if (found[0] == 0xff && found[1] == 0xd8 && found[2] == 0xff && (found[3] & 0xf0) == 0xe0)
        {
            // close any previous file and increment image
            if (output != NULL)
            {
                fclose(output);
                jpeg_found++;
            }

            startJPEG = true;

        }

        else
        {
            // change the bool to false while no new jpeg has been found per 512 bytes block
            startJPEG = false;
        }


        //if jpeg has been found opens a new file
        if (startJPEG)
        {
            sprintf(name, "%03i.jpg", jpeg_found);

            // creates a file opening it in w(rite) assigning the name defined in sprtintf
            output = fopen(name, "w");

        }

        if (output != NULL)
        {
            // write into the file when it's open
            fwrite(found, 1, BLOCK, output);
        }


    }

    // close all files
    fclose(output);

    fclose(input);

    // return 0 if successful
    return 0;

}
