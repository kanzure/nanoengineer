/* Copyright (c) 2006 Nanorex, Inc. All rights reserved. */
#ifndef ALLOCATE_H_INCLUDED
#define ALLOCATE_H_INCLUDED

#define RCSID_ALLOCATE_H  "$Id$"

extern void *allocate(int size);

extern void *reallocate(void *p, int size);

extern char *copy_string(char *s);

extern void *copy_memory(void *src, int len);

extern void *accumulator(void *old, unsigned int len, int zerofill);

extern void destroyAccumulator(void *a);

extern char *replaceExtension(char *template, char *newExtension);

#endif
