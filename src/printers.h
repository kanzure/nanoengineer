
extern void pv(FILE *f, struct xyz foo);

extern void pvt(FILE *f, struct xyz foo);

extern void pa(FILE *f, int i);

extern void checkatom(FILE *f, int i);

extern void pb(FILE *f, int i);

extern void printAllBonds(FILE *f);

extern void pq(FILE *f, int i);

extern void pcon(FILE *f, int i);

extern void traceHeader(FILE *f, char *inputFileName, char *outputFileName, char *traceFileName, 
                        struct part *part, int numFrames, int stepsPerFrame, double temperature);

extern void traceJigHeader(FILE *f, struct part *part);

extern void traceJigData(FILE *f, struct part *part);

extern void printError(FILE *f, const char *file, int line, const char *err_or_warn,
		       int doPerror, const char *format, ...);

extern void doneExit(int exitvalue, FILE *f, const char *format, ...);
