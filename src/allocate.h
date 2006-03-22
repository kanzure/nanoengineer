#ifndef ALLOCATE_H_INCLUDED
#define ALLOCATE_H_INCLUDED

#define RCSID_ALLOCATE_H  "$Id$"

extern void *allocate(int size);

extern void *reallocate(void *p, int size);

extern void __simfree(void **p);

#define simfree(p)  __simfree((void**) &(p))

extern void demolition(void);

extern char *copy_string(char *s);

extern void *copy_memory(void *src, int len);

extern void *accumulator(void *old, unsigned int len, int zerofill);

extern char *replaceExtension(char *template, char *newExtension);

#endif
