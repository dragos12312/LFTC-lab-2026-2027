/*
Symbol table implemented in C as a hash table with separate chaining. Each bucket is a linked list of nodes. A symbol's position in the table is the pair (bucket index, index inside the bucket). Identifiers and 
constants are kept in the same table.

Compiled as a shared library and used from the Python scanner:
Linux/Mac: gcc -shared -fPIC -o st_lib.so symbol_table.c
Windows:   gcc -shared -o st_lib.dll symbol_table.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Node {
    char *key;
    struct Node *next;
} Node;

typedef struct {
    int size;
    int count;
    Node **buckets;
} SymbolTable;

/* creates an empty table with the given number of buckets */
SymbolTable *st_create(int size)
{
    SymbolTable *st = malloc(sizeof(SymbolTable));
    st->size = size;
    st->count = 0;
    st->buckets = malloc(size * sizeof(Node *));
    for (int i = 0; i < size; i++)
        st->buckets[i] = NULL;
    return st;
}

/* sum of the ASCII codes of the characters, modulo the table size */
int st_hash(SymbolTable *st, const char *key)
{
    int total = 0;
    for (int i = 0; key[i] != '\0'; i++)
        total += (unsigned char)key[i];
    return total % st->size;
}

/* looks for key; if found, writes its position in *bucket and *index and returns 1, otherwise returns 0 */
int st_search(SymbolTable *st, const char *key, int *bucket, int *index)
{
    int b = st_hash(st, key);
    int i = 0;
    for (Node *p = st->buckets[b]; p != NULL; p = p->next) {
        if (strcmp(p->key, key) == 0) {
            *bucket = b;
            *index = i;
            return 1;
        }
        i++;
    }
    return 0;
}

/* adds key if it is not already in the table and writes its position in *bucket and *index. New keys go at the end of the list, so positions that were already given out never change. */
void st_add(SymbolTable *st, const char *key, int *bucket, int *index)
{
    if (st_search(st, key, bucket, index))
        return;

    int b = st_hash(st, key);
    Node *node = malloc(sizeof(Node));
    node->key = malloc(strlen(key) + 1);
    strcpy(node->key, key);
    node->next = NULL;

    int i = 0;
    if (st->buckets[b] == NULL) {
        st->buckets[b] = node;
    } else {
        Node *p = st->buckets[b];
        i = 1;
        while (p->next != NULL) {
            p = p->next;
            i++;
        }
        p->next = node;
    }
    st->count++;
    *bucket = b;
    *index = i;
}

/* returns the symbol at position (bucket, index), or NULL if there is none */
const char *st_get(SymbolTable *st, int bucket, int index)
{
    if (bucket < 0 || bucket >= st->size)
        return NULL;
    Node *p = st->buckets[bucket];
    for (int i = 0; i < index && p != NULL; i++)
        p = p->next;
    return p == NULL ? NULL : p->key;
}

int st_count(SymbolTable *st)
{
    return st->count;
}

/* writes the whole table to a file */
int st_write(SymbolTable *st, const char *file_name)
{
    FILE *f = fopen(file_name, "w");
    if (f == NULL)
        return 0;
    fprintf(f, "Symbol table (hash table in C, size %d, %d symbols)\n",
            st->size, st->count);
    fprintf(f, "position   symbol\n");
    for (int b = 0; b < st->size; b++) {
        int i = 0;
        for (Node *p = st->buckets[b]; p != NULL; p = p->next) {
            char pos[32];
            sprintf(pos, "(%d, %d)", b, i);
            fprintf(f, "%-11s%s\n", pos, p->key);
            i++;
        }
    }
    fclose(f);
    return 1;
}

/* frees all the memory used by the table */
void st_destroy(SymbolTable *st)
{
    for (int b = 0; b < st->size; b++) {
        Node *p = st->buckets[b];
        while (p != NULL) {
            Node *next = p->next;
            free(p->key);
            free(p);
            p = next;
        }
    }
    free(st->buckets);
    free(st);
}
