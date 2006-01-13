
extern void *allocate(int size);

extern void *reallocate(void *p, int size);

extern char *copy_string(char *s);

extern void *copy_memory(void *src, int len);

extern void *accumulator(void *old, unsigned int len, int zerofill);

extern char *replaceExtension(char *template, char *newExtension);
