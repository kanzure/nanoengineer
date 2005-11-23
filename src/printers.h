
#if 0
#define DBGPRINTF(x...) fprintf(stderr, ## x)
#else
#define DBGPRINTF(x...) ((void) 0)
#endif

extern int debug_flags;
#define DEBUG(flag) (debug_flags & (flag))
#define DPRINT(flag, x...) (DEBUG(flag) ? fprintf(stderr, ## x) : (void) 0)

#define D_TABLE_BOUNDS    (1<<0)
#define D_READER          (1<<1)
#define D_MINIMIZE        (1<<2)
#define D_MINIMIZE_POTENTIAL_MOVIE (1<<3)
#define D_MINIMIZE_GRADIENT_MOVIE  (1<<4)


extern FILE *tracef;
#define ERROR(s...) (printError(tracef, __FILE__, __LINE__, "Error", 0, ## s))
#define WARNING(s...) (printError(tracef, __FILE__, __LINE__, "Warning", 0, ## s))
#define ERROR_ERRNO(s...) (printError(tracef, __FILE__, __LINE__, "Error", 1, ## s))
#define WARNING_ERRNO(s...) (printError(tracef, __FILE__, __LINE__, "Warning", 1, ## s))

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
