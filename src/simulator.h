// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <signal.h>
#include <time.h>
#include <stdarg.h>
#include <errno.h>
#include <string.h>

#include "lin-alg.h"
#include "allocate.h"
#include "hashtable.h"

#include "minimize.h"
#include "structcompare.h"

#ifdef WWDEBUG
// handy little debug macros
#define MARK()   { FILE *outf = fopen("/home/wware/FOO", "a"); \
              fprintf(outf, "%s:%d\n", __FILE__, __LINE__); fclose(outf); }
#define SAY(fmt...)   { FILE *outf = fopen("/home/wware/FOO", "a"); \
              fprintf(outf, "%s:%d  ", __FILE__, __LINE__); \
              fprintf(outf, ##fmt); fprintf(outf, "\n"); fclose(outf); }
#define SAY_INT(x)   SAY("%s=%d", #x, x)
#define SAY_HEX(x)   SAY("%s=%p", #x, x)
#else
#define MARK()
#define SAY(fmt...)
#define SAY_INT(x)
#define SAY_HEX(x)
#endif

#define iabs(x) (x<0 ? -(x) : x)
#define min(x,y) (x<y ? x : y)
#define max(x,y) (x>y ? x : y)

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
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
