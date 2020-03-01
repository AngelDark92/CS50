// Resizes a .BMP file

#include <stdio.h>
#include <stdlib.h>

#include "bmp.h"


int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: ./resize n infile outfile\n");
        return 1;
    }

    // these only point to a file hence the *
    char *infile = argv[2];
    char *outfile = argv[3];

    //get the number as an integer
    int multip = atoi(argv[1]);

    //Ensures multip is an integer between 1 and 100
    if (!(multip <= 100 && multip >= 1))
    {
        printf("The first arg needs to be a positive integer 1 to 100.\n");
        return 2;
    }

    // open input file from the pointer
    FILE *inptr = fopen(infile, "r");

    //condition takes the content of the file and compares to null
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 3;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 4;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 5;
    }



    // determine padding for scanlines input file
    int padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    //store old variables
    int old_width = bi.biWidth;
    int old_height = bi.biHeight;

    //change new variables accordin to multiplier
    bi.biWidth *= multip;
    bi.biHeight *= multip;

    //calculates the new padding according to the multip
    int new_pad = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    bi.biSizeImage = (sizeof(RGBTRIPLE) * bi.biWidth + new_pad) * abs(bi.biHeight);
    bf.bfSize = bi.biSizeImage + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

    // write outfile's BITMAPFILEHEADER
    fwrite(&bf, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bi, sizeof(BITMAPINFOHEADER), 1, outptr);



    // iterate over inpfile's scanlines
    for (int i = 0, inp_height = abs(old_height); i < inp_height; i++)
    {
        // array to store each pixel triple
        RGBTRIPLE iter_array [bi.biWidth];

        // iterate over pixels in scanline no padding
        for (int j = 0; j < old_width; j++)
        {
            // temporary storage
            RGBTRIPLE triple;

            // read RGB triple from infile
            fread(&triple, sizeof(RGBTRIPLE), 1, inptr);


            // iterate over output based on the multiplier
            for (int m = 0; m < multip; m++)
            {
                // pointer for the array
                int multip_pointer = multip * j + m;
                // write RGB triple for entire line to array
                iter_array[multip_pointer] = triple;
            }

        }

        for (int k = 0; k < multip; k++)
        {

            fwrite(&iter_array, sizeof(iter_array), 1, outptr);

            for (int l = 0; l < new_pad; l++)
            {
                fputc(0x00, outptr);
            }


        }

        // skip over infile padding, if any
        fseek(inptr, padding, SEEK_CUR);

    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}