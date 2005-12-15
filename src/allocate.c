#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "allocate.h"

void *
allocate(int size)
{
  void *ret = malloc(size);
  if (ret == NULL) {
    fprintf(stderr, "Out of memory\n");
    exit(1);
  }
  return ret;
}

void *
reallocate(void *p, int size)
{
  void *ret = realloc(p, size);
  if (ret == NULL) {
    fprintf(stderr, "Out of memory\n");
    exit(1);
  }
  return ret;
}

char *
copy_string(char *s)
{
  char *ret = (char *)allocate(strlen(s)+1);
  return strcpy(ret, s);
}

void *
copy_memory(void *src, int len)
{
  void *ret = allocate(len);
  return memcpy(ret, src, len);
}

// find the smallest power of 2 greater than len
static unsigned int
quantize_length(unsigned int len)
{
  unsigned int i;
  unsigned int j;
  
  for (i=8; i<(8*sizeof(int)); i++) {
    j = (1<<i);
    if (j > len) {
      return j;
    }
  }
  fprintf(stderr, "Out of memory, requesting %d bytes\n", len);
  exit(1);
}

/* Automatically reallocate storage for a buffer that has an unknown
 * final size.  To create a new accumulator, pass in old==NULL.  To
 * reuse an existing accumulator, pass it in as old.  The new desired
 * size in bytes is len.  If zerofill is non-zero, all bytes between
 * the old and new length will be zero filled.
 *
 * Call this every time before placing a new element in the
 * accumulator.  If you may place new elements non-sequentially, you
 * should set zerofill on every call for a given accumulator.
 *
 * If it's non-NULL, the argument 'old' points four bytes into an
 * allocated block. The four preceding bytes give the length of the
 * most recent allocation for that block. That's why we back up from
 * old to get the value for accumulator, which is a block of size
 * length+sizeof(unsigned int).
 */
void *
accumulator(void *old, unsigned int len, int zerofill)
{
  unsigned int *accumulator;     // points to length word, or NULL if a new accumulator
  unsigned int new_len;          // includes the length word
  unsigned int accum_length;     // includes the length word
  unsigned int old_accum_length; // includes the length word
  // The value stored in the length word includes the length word itself.

  // allocate something even if len==0
  new_len = (len ? len : 1) + sizeof(int);
  if (old == NULL) {
    accumulator = NULL;
    old_accum_length = sizeof(int);
  } else {
    accumulator = ((unsigned int *)old) - 1;
    old_accum_length = *accumulator;
  }
  if (new_len > old_accum_length) {
    accum_length = quantize_length(new_len);
    accumulator = (unsigned int *)reallocate(accumulator, accum_length);
    *accumulator = accum_length;
    if (zerofill) {
      memset(((char *)accumulator)+old_accum_length, 0,
             accum_length - old_accum_length);
    }
    return (void *)(accumulator+1);
  }
  return old;
}
