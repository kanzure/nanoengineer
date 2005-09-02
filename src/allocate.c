#include <stdio.h>
#include <stdlib.h>
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
