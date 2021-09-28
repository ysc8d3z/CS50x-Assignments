// Implements a dictionary's functionality

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <strings.h>
#include <ctype.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Number of buckets in hash table
const unsigned int N = 100000;

// Hash table
node *table[N];

// Counts number of words in dictionary
long dictSize = 0;

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // Hash word to obtain a hash value
    int hashValue = hash(word);
    
    // Access linked list at that index in the has table
    node *cursor = table[hashValue];
    
    // Traverse linked list, looking for the word 
    while (cursor != NULL)
    {
        if (strcasecmp(cursor->word, word) == 0)
        {
            return true;
        }
        
        cursor = cursor->next;
    }
    
    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    long sum = 0;

    for (int i = 0; i < strlen(word); i++)
    {
        sum += tolower(word[i]);
    }

    return sum % N;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    // Open dictionary file
    FILE *dictPtr = fopen(dictionary, "r");
    if (dictPtr == NULL)
    {
        return false;
    }

    // Initialize array to store each word
    char tmpWord[LENGTH + 1];

    // Read strings from file one at a time
    while (fscanf(dictPtr, "%s", tmpWord) != EOF)
    {
        // Create a new node for each word
        node *n = malloc(sizeof(node));
        if (n == NULL)
        {
            return false;
        }

        strcpy(n->word, tmpWord);

        // Hash word to obtain a hash value
        int hashValue = hash(tmpWord);

        // Insert node into hash table at that location
        n->next = table[hashValue];
        table[hashValue] = n;
        dictSize++;
    }

    fclose(dictPtr);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    // Returns a global variable that increments each time a new node is added, aka the number of words
    return dictSize;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    for (int i = 0; i < N; i++)
    {
        node *cursor = table[i];
        while (cursor != NULL)
        {
            node *tmp = cursor;
            cursor = cursor->next;
            free(tmp);
        }
    
        if (cursor == NULL && i == N - 1)
        {
            return true;
        }
            
    }
    
    return false;
}
