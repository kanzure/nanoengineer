
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


extern FILE *tracef;
#define ERROR(s...) (printError(tracef, "Error", 0, ## s))
#define WARNING(s...) (printError(tracef, "Warning", 0, ## s))
#define ERROR_ERRNO(s...) (printError(tracef, "Error", 1, ## s))
#define WARNING_ERRNO(s...) (printError(tracef, "Warning", 1, ## s))

extern void writeOutputHeader(FILE *f);

extern void writeOutputTrailer(FILE *f, int frameNumber);

extern void snapshot(FILE *f, int n, struct xyz *pos);

extern int minshot(FILE *f, int final, struct xyz *pos, double rms, double hifsq, int frameNumber, char *callLocation);

extern void pv(FILE *f, struct xyz foo);

extern void pvt(FILE *f, struct xyz foo);

extern void pa(FILE *f, int i);

extern void checkatom(FILE *f, int i);

extern void pb(FILE *f, int i);

extern void printAllBonds(FILE *f);

extern void pq(FILE *f, int i);

extern void pvdw(FILE *f, struct vdWbuf *buf, int n);

extern void pcon(FILE *f, int i);

extern void printheader(FILE *f, char *ifile, char *ofile, char *tfile, 
                        int na, int nf, int spf, double temp);

extern void printError(FILE *f, const char *err_or_warn, int doPerror, const char *format, ...);

extern void doneExit(int exitvalue, FILE *f, const char *format, ...);

extern void headcon(FILE *f);

extern void tracon(FILE *f);

