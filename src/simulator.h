// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <signal.h>
#include <time.h>
#include <stdarg.h>
#include <errno.h>
#include <string.h>

#include "debug.h"

#include "lin-alg.h"
#include "allocate.h"
#include "hashtable.h"

#include "minimize.h"
#include "structcompare.h"

#ifdef WWDEBUG
// handy little debug macros
#define MARK()   { FILE *outf = fopen("/home/wware/FOO", "a"); \
              fprintf(outf, "%s:%d\n", __FILE__, __LINE__); fclose(outf); }
#define SAY(fmt)   { FILE *outf = fopen("/home/wware/FOO", "a"); \
              fprintf(outf, "%s:%d  ", __FILE__, __LINE__); \
              fprintf(outf, fmt); fprintf(outf, "\n"); fclose(outf); }
#define SAY1(fmt,a)   { FILE *outf = fopen("/home/wware/FOO", "a"); \
              fprintf(outf, "%s:%d  ", __FILE__, __LINE__); \
              fprintf(outf, fmt, a); fprintf(outf, "\n"); fclose(outf); }
#define SAY2(fmt,a,b)   { FILE *outf = fopen("/home/wware/FOO", "a"); \
              fprintf(outf, "%s:%d  ", __FILE__, __LINE__); \
              fprintf(outf, fmt, a, b); fprintf(outf, "\n"); fclose(outf); }
#define SAY3(fmt,a,b,c)   { FILE *outf = fopen("/home/wware/FOO", "a"); \
              fprintf(outf, "%s:%d  ", __FILE__, __LINE__); \
              fprintf(outf, fmt, a, b, c); fprintf(outf, "\n"); fclose(outf); }
#else
#define MARK()
#define SAY(fmt)
#define SAY1(fmt,a)
#define SAY2(fmt,a,b)
#define SAY3(fmt,a,b,c)
#endif

#define SAY_INT(x)   SAY1("%s=%d", #x, x)
#define SAY_DBL(x)   SAY1("%s=%lg", #x, x)
#define SAY_XYZ(s)   SAY1("%s={%lf,%lf,%lf)", #s, (s).x, (s).y, (s).z)
#define SAY_HEX(x)   SAY1("%s=%p", #x, x)

#define iabs(x) (x<0 ? -(x) : x)
#ifndef min
#define min(x,y) ((x) < (y) ? (x) : (y))
#endif
#ifndef max
#define max(x,y) ((x) > (y) ? (x) : (y))
#endif

#define PICOSEC (1e-12)

// scaling factor for radius in extension gradient calculations
#define DR 1e6

/* van der Waals forces */

#include "newtables.h"
#include "interpolate.h"

#include "readmmp.h"
#include "readxyz.h"
#include "part.h"
#include "printers.h"
#include "dynamics.h"
#include "jigs.h"
#include "potential.h"
#include "minstructure.h"
#include "writemovie.h"

#include "globals.h"

/*
 * Callbacks for use with Pyrex, do-nothing functions in the stand-alone
 * simulator.  wware 060101
 */

extern void callback_writeFrame(struct part *part, struct xyz *pos);

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
