
extern void traceFileVersion(void);

extern void traceHeader(struct part *part);

extern void traceJigHeader(struct part *part);

extern void traceJigData(struct part *part);

extern void printError(const char *file, int line, int error_type,
		       int doPerror, const char *format, ...);

extern void done(const char *format, ...);
