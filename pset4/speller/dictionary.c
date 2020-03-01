// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "dictionary.h"

// Represents number of buckets in a hash table
#define N 26

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node; // Typedef can also be written afterwards as typedef struct node* node

//definition of strdup which I will need later
//https://stackoverflow.com/questions/46013382/c-strndup-implicit-declaration
char *strdup(const char *s)
{
    size_t size = strlen(s) + 1;
    char *p = malloc(size);
    if (p != NULL)
    {
        memcpy(p, s, size);
    }
    return p;
}

// Represents a hash table
node *hashtable[N];

int word_counter = 0;

// Hashes word to a number between 0 and 25, inclusive, based on its first letter
unsigned int hash(const char *word)
{
    return tolower(word[0]) - 'a';
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // Initialize hash table
    for (int i = 0; i < N; i++)
    {
        hashtable[i] = NULL;
    }

    // Open dictionary
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        unload();
        return false;
    }

    // Buffer for a word
    char word[LENGTH + 1];

    // Insert words into hash table
    while (fscanf(file, "%s", word) != EOF)
    {

        //Malloc for a new node
        node *n = malloc(sizeof(node));

        //check if malloc succeeded
        if (!n) //if n is null (0) the not returns 1 which is true, malloc failed
        {
            return false;
        }

        //Copy the new word to the node
        strcpy(n->word, word);

        //Next pointer of n will be null by default
        n->next = NULL;

        // Hashing the current word;
        int i = hash(word);

        // If the hashtable is still as initiated add a new node normally.
        if (hashtable[i] == NULL)
        {
            //assign node to the hashtable in the empty index
            hashtable[i] = n;

            //Increase the word counter global variable
            word_counter++;
        }

        // Else to insert at end of node if list is already full
        else
        {
            //Cursor points at the hashtable [current_hash]
            node *cursor = hashtable[i];

            //While the next cursor is not null, go to "next" memory location
            while (cursor->next != NULL)
            {
                cursor = cursor->next;
            }

            //When cursor->next is null, assign it the new node
            //n->next was already initialised as null
            cursor->next = n;

            //Increase the counter
            word_counter++;
        }

    }

    // Close dictionary
    fclose(file);

    // Indicate success
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{

    return word_counter; //automatically returns n of words loaded

}

// Returns true if word is in dictionary else false
bool check(const char *word)
{

    //Calculate the length of the string
    int len = strlen(word);

    //https://www.geeksforgeeks.org/strdup-strdndup-functions-c/
    char *word_1 = strdup(word);

    //transform string to lowercase https://stackoverflow.com/questions/41148978/how-to-use-tolower-with-char
    for (int j = 0; j < len; j++)
    {
        word_1[j] = tolower(word[j]);
    }

    //calculate the hash for this word
    int k = hash(word_1);

    //cursor points at the found hash in the hashtable
    node *cursor = hashtable[k];

    //Loop to find the word in the hash
    while (cursor != NULL)
    {
        if (!strcmp(word_1, cursor->word))
        {
            //free memory and return true
            free(word_1);
            return true;
        }

        cursor = cursor->next;
    }
    //Frees the memory occupied by strdup
    //Returns false if the last cursor does not contain word
    free(word_1);
    return false;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    //iterate over the whole hashtable which is "N big"
    for (int l = 0; l < N; l++)
    {
        node *cursor = hashtable[l];
        while (cursor != NULL)
        {
            node *temp = cursor;
            cursor = cursor->next;
            free(temp);
        }

    }

    return true;
}
