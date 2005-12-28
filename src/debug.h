
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
#define D_MINIMIZE_GRADIENT_MOVIE_DETAIL  (1<<5)
#define D_SKIP_STRETCH    (1<<6)
#define D_SKIP_BEND       (1<<7)
#define D_PRINT_BEND_STRETCH (1<<8)
#define D_SKIP_VDW        (1<<9)
#define D_GRADIENT_FROM_POTENTIAL (1<<10)
#define D_MINIMIZE_FINAL_PRINT (1<<11)
#define D_STRESS_MOVIE (1<<12)

extern FILE *tracef;
#define ERROR(s...) (printError(tracef, __FILE__, __LINE__, "Error", 0, ## s))
#define WARNING(s...) (printError(tracef, __FILE__, __LINE__, "Warning", 0, ## s))
#define ERROR_ERRNO(s...) (printError(tracef, __FILE__, __LINE__, "Error", 1, ## s))
#define WARNING_ERRNO(s...) (printError(tracef, __FILE__, __LINE__, "Warning", 1, ## s))
