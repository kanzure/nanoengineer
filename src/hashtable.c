
/*

A very simple hashtable implementation.  A hashtable is an array of
hashtable_bucket's.  To find the correct hashtable_bucket, hash the key,
and start at (hash % size) in the array.  If the key field is NULL,
this bucket is empty, and the key doesn't exist in the table.  If the
hash field matches, string compare the key field.  On a miss, add one
(wrapping to the beginning of the array) and check again.

This method is called "Linear Probing" in Knuth Vol 3 p. 518.

*/

#include <stdio.h>
#include <string.h>
#include "allocate.h"
#include "hashtable.h"
  
/* maximum fraction of full buckets in table */
#define RESIDENCY 0.8  

static int
hash_string(char *s)
{
  int hash = 0;
  int shift = 0;
  int c;
  
  while (c=*s++) {
    c <<= shift;
    hash ^= c;
    shift += 8;
    if (shift > 31) {
      shift = 0;
    }
  }
  return hash;
}

/* Hashing works best with a prime number of buckets... */
static int some_primes[] = {
  251, 503, 1009, 2003, 4001, 8009, 16001, 32003, 64007, 128021, 256021,
  512021, 1024021, 2048021, 4096021, 8192003, 16384003, 32768011
};

/* Returns a nice prime table size that can hold at least min_size elements */
static int
hash_next_size(int min_size)
{
  int i;
  int last = sizeof(some_primes) / sizeof(int);
  for (i=0; i<last; i++) {
    if (some_primes[i] > min_size) {
      return some_primes[i];
    }
  }
  /* XXX error processing */
  return 0; /* hash table too big */
}

/* Find the bucket for this key.  Always returns a pointer to a
   bucket.  If the bucket is full (key is non NULL) it matches the
   given key, otherwise this is the bucket you should place the key
   in. */
static struct hashtable_bucket *
hashtable_find_bucket(struct hashtable_bucket *buckets, int size, int hash, char *key)
{
  int index = hash % size;
  struct hashtable_bucket *search_start = &buckets[index];
  struct hashtable_bucket *search_wrap = &buckets[size];
  struct hashtable_bucket *b = search_start;
  
  do {
    if (b->key == NULL) {
      return b;
    }
    if (b->hash == hash && !strcmp(b->key, key)) {
      return b;
    }
    b++;
    if (b >= search_wrap) {
      b = buckets;
    }
  } while (b != search_start);
  /* XXX error processing */
  return NULL; /* this should never happen, since count should be less than size */
}


static void
hashtable_resize(struct hashtable *table, int newsize)
{
  int i;
  int len;
  int old_size = table->size;
  struct hashtable_bucket *old_buckets = table->buckets;
  struct hashtable_bucket *old_bucket;
  struct hashtable_bucket *new_bucket;
  table->size = hash_next_size(newsize);
  if (table->size < 1) {
    /* XXX error processing */
    return;
  }
  len = table->size * sizeof(struct hashtable_bucket);
  table->buckets = (struct hashtable_bucket *)allocate(len);
  memset(table->buckets, 0, len);
  if (old_buckets != NULL) {
    /* rehash existing buckets into new table */
    for (i=0; i<old_size; i++) {
      old_bucket = &old_buckets[i];
      if (old_bucket->key != NULL && old_bucket->value != NULL) {
        /* full bucket, put it in the new table */
        new_bucket = hashtable_find_bucket(table->buckets, table->size, old_bucket->hash, old_bucket->key);
        if (new_bucket->key != NULL) {
          fprintf(stderr, "Duplicate key in hashtable_resize.");
        } else {
          new_bucket->hash = old_bucket->hash;
          new_bucket->key = old_bucket->key;
          new_bucket->value = old_bucket->value;
        }
      }
    }
    free(old_buckets);
  }
}

/* Create a new hashtable which is initially configured to hold up to
   initial_size buckets.  The table will be dynamically resized if
   more buckets are needed. */
struct hashtable *
hashtable_new(int initial_size)
{
  struct hashtable *table;

  table = (struct hashtable *)allocate(sizeof(struct hashtable));
  table->size = 0;
  table->count = 0;
  table->buckets = NULL;
  hashtable_resize(table, initial_size);
  if (table->buckets == NULL) {
    /* XXX error processing */
    free(table);
    return NULL;
  }
  return table;
}

/* Store a value in a hashtable, associated with a given key.  A copy
   of the key is made.  The previous association with this key is
   returned, or NULL if this is a new key for this hashtable.

   Note that you can specify NULL values to be stored, but you cannot
   remove a key association.  This would require searching for
   following buckets that might have to be moved to this one to
   restore table consistancy.  Since I don't see the need to delete at
   this time, I'm not worrying about it.
 */
void *
hashtable_put(struct hashtable *table, char *key, void *value)
{
  void *old;
  int hash = hash_string(key);
  struct hashtable_bucket *bucket = hashtable_find_bucket(table->buckets, table->size, hash, key);
  if (bucket->key == NULL) {
    bucket->hash = hash;
    bucket->key = copy_string(key);
    bucket->value = value;
    table->count++;
    if (((float)table->count) / (float)(table->size) > RESIDENCY) {
      hashtable_resize(table, table->size+1);
    }
    return NULL;
  } else {
    old = bucket->value;
    bucket->value = value;
    return old;
  }
  
}

/* Return the value associated with the given key in the hashtable.
   Returns NULL if there is no association for that key.
 */
void *
hashtable_get(struct hashtable *table, char *key)
{
  int hash = hash_string(key);
  struct hashtable_bucket *bucket = hashtable_find_bucket(table->buckets, table->size, hash, key);
  if (bucket->key == NULL) {
    return NULL;
  }
  return bucket->value;
}

void
hashtable_print(FILE *f, struct hashtable *table)
{
  int i;
  struct hashtable_bucket *b;

  fprintf(f, "begin hashtable--------------------\n");
  fprintf(f, "size: %d count: %d\n", table->size, table->count);
  for (i=0; i<table->size; i++) {
    b = &table->buckets[i];
    if (b->key == NULL) {
      if (b->hash != 0 || b->value != NULL) {
        fprintf(f, "!%5d %5d %20s 0x%08x 0x%08x\n", i, b->hash % table->size, "NULL", b->hash, b->value);
      }
    } else {
      fprintf(f, " %5d %5d %20s 0x%08x 0x%08x\n", i, b->hash % table->size, b->key, b->hash, b->value);
    }
  }
  fprintf(f, "  end hashtable--------------------\n");
}

/* Calls func(key, value) for each key/value pair in the hashtable.
   Keys are presented in an undefined order (dependant on hash values
   and current hashtable size).  Do not change the hashtable during
   the iteration.
 */
void
hashtable_iterate(struct hashtable *table, void func())
{
  int i;
  struct hashtable_bucket *b;
  
  for (i=0; i<table->size; i++) {
    b = &table->buckets[i];
    if (b->key != NULL) {
      func(b->key, b->value);
    }
  }
}


#if 0    
main()
{
  struct hashtable *ht;

  ht = hashtable_new(0);
  hashtable_print(stdout, ht);
  hashtable_put(ht, "one", (void *)0x1);
  hashtable_print(stdout, ht);
  hashtable_put(ht, "two", (void *)0x2);
  hashtable_print(stdout, ht);
  hashtable_put(ht, "three", (void *)0x3);
  hashtable_print(stdout, ht);
  hashtable_put(ht, "four", (void *)0x4);
  hashtable_print(stdout, ht);
  hashtable_put(ht, "five", (void *)0x5);
  hashtable_print(stdout, ht);
  hashtable_put(ht, "six", (void *)0x6);
  hashtable_print(stdout, ht);
  hashtable_put(ht, "seven", (void *)0x7);
  hashtable_print(stdout, ht);
  hashtable_put(ht, "eight", (void *)0x8);
  hashtable_print(stdout, ht);
  hashtable_put(ht, "nine", (void *)0x9);
  hashtable_print(stdout, ht);
}
#endif
