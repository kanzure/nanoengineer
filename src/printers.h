
extern void traceHeader(char *inputFileName, char *outputFileName, char *traceFileName, 
                        struct part *part, int numFrames, int stepsPerFrame, double temperature);

extern void traceJigHeader(struct part *part);

extern void traceJigData(struct part *part);

extern void printError(const char *file, int line, int error_type,
		       int doPerror, const char *format, ...);

extern void done(const char *format, ...);
