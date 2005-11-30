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
