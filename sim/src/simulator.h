// Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

#ifndef SIMULATOR_H_INCLUDED
#define SIMULATOR_H_INCLUDED

#define RCSID_SIMULATOR_H  "$Id$"

#define MULTIPLE_RCSID_STRING \
    RCSID_SIMULATOR_H \
    RCSID_DEBUG_H \
    RCSID_LIN_ALG_H \
    RCSID_ALLOCATE_H \
    RCSID_HASHTABLE_H \
    RCSID_MINIMIZE_H \
    RCSID_STRUCTCOMPARE_H \
    RCSID_PART_H \
    RCSID_NEWTABLES_H \
    RCSID_INTERPOLATE_H \
    RCSID_READMMP_H \
    RCSID_READXYZ_H \
    RCSID_AMBER_PATTERNS_H \
    RCSID_PAM5_PATTERNS_H \
    RCSID_PATTERN_H \
    RCSID_PRINTERS_H \
    RCSID_PRINTGROMACSTOPLOGY_H \
    RCSID_DYNAMICS_H \
    RCSID_JIGS_H \
    RCSID_POTENTIAL_H \
    RCSID_MINSTRUCTURE_H \
    RCSID_WRITEMOVIE_H \
    RCSID_GLOBALS_H

// SI prefixes:
//
// 1e+24 Y  yotta
// 1e+21 Z  zetta
// 1e+18 E  exa
// 1e+15 P  peta
// 1e+11 T  tera
// 1e+9  G  giga
// 1e+6  M  mega
// 1e+3  k  kilo
// 1e+2  h  hecto
// 1e+1  da deca
//
// 1e-1  d  deci
// 1e-2  c  centi
// 1e-3  m  milli
// 1e-6  u  micro
// 1e-9  n  nano
// 1e-12 p  pico
// 1e-15 f  femto
// 1e-18 a  atto
// 1e-21 z  zepto
// 1e-24 y  yocto

// one Angstrom is 0.1 nm or 1e-10 m

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <signal.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <time.h>
#include <stdarg.h>
#include <errno.h>
#include <string.h>

// XXX the mac build environment doesn't seem to include a values.h,
// and since the windows version doesn't define MAXDOUBLE (which is
// the only reason we need it), it seems it's only useful on linux.
// Commenting it out until we know the right way of finding MAXDOUBLE
// on all platforms.
//#include <values.h>

// it's possible that includeing float.h and using DBL_MAX is the
// right way to go.  It should be tested first, though.
//#include <float.h>

// for some reason, values.h on windows doesn't include this.  we put
// it here until someone can find the right way to get it defined, or
// until M$ decides to comply with standards instead of trying to
// squash them.
#ifndef MAXDOUBLE
#define 	MAXDOUBLE   1.79769313486231570e+308
#endif

#include "debug.h"

#include "lin-alg.h"
#include "allocate.h"
#include "hashtable.h"

#include "minimize.h"
#include "structcompare.h"

#ifdef WWDEBUG
// handy little debug macros
#define SAY(fmt)   { FILE *outf = fopen("/home/wware/FOO", "a"); \
              fprintf(outf, "%s:%d(%s)  ", __FILE__, __LINE__, __FUNCTION__); \
              fprintf(outf, fmt); fclose(outf); }
#define SAY1(fmt,a)   { FILE *outf = fopen("/home/wware/FOO", "a"); \
              fprintf(outf, "%s:%d(%s)  ", __FILE__, __LINE__, __FUNCTION__); \
              fprintf(outf, fmt, a); fclose(outf); }
#define SAY2(fmt,a,b)   { FILE *outf = fopen("/home/wware/FOO", "a"); \
              fprintf(outf, "%s:%d(%s)  ", __FILE__, __LINE__, __FUNCTION__); \
              fprintf(outf, fmt, a, b); fclose(outf); }
#define SAY3(fmt,a,b,c)   { FILE *outf = fopen("/home/wware/FOO", "a"); \
              fprintf(outf, "%s:%d(%s)  ", __FILE__, __LINE__, __FUNCTION__); \
              fprintf(outf, fmt, a, b, c); fclose(outf); }
#define SAY4(fmt,a,b,c,d)   { FILE *outf = fopen("/home/wware/FOO", "a"); \
              fprintf(outf, "%s:%d(%s)  ", __FILE__, __LINE__, __FUNCTION__); \
              fprintf(outf, fmt, a, b, c, d); fclose(outf); }
#else
#define SAY(fmt)
#define SAY1(fmt,a)
#define SAY2(fmt,a,b)
#define SAY3(fmt,a,b,c)
#define SAY4(fmt,a,b,c,d)
#endif

#define MARK()       SAY("\n")
#define SAY_INT(x)   SAY2("%s=%d\n", #x, x)
#define SAY_DBL(x)   SAY2("%s=%lg\n", #x, x)
#define SAY_XYZ(s)   SAY4("%s={%lf,%lf,%lf)\n", #s, (s).x, (s).y, (s).z)
#define SAY_PTR(x)   SAY2("%s=%p\n", #x, x)

#define iabs(x) (x<0 ? -(x) : x)
#ifndef min
#define min(x,y) ((x) < (y) ? (x) : (y))
#endif
#ifndef max
#define max(x,y) ((x) > (y) ? (x) : (y))
#endif

#define PICOSEC (1e-12)

/* van der Waals forces */

#include "part.h"
#include "newtables.h"
#include "interpolate.h"

#include "readmmp.h"
#include "readxyz.h"
#include "printers.h"
#include "dynamics.h"
#include "jigs.h"
#include "amber_patterns.h"
#include "pam5_patterns.h"
#include "pattern.h"
#include "potential.h"
#include "minstructure.h"
#include "writemovie.h"
#include "rigid.h"
#include "printGromacsTopology.h"

#include "globals.h"

/*
 * Callbacks for use with Pyrex, do-nothing functions in the stand-alone
 * simulator.  wware 060101
 */

extern void callback_writeFrame(struct part *part, struct xyz *pos, int last_frame);

// wware 060102  callback for trace file
extern void write_traceline(const char *format, ...);

// Python exception stuff, wware 060109
extern char *py_exc_str;
extern void set_py_exc_str(const char *filename,
			   const int linenum, const char *format, ...);

#define CHECKNAN(x)        ASSERT(!isnan(x))
#define CHECKNANR(x, y)    ASSERTR(!isnan(x), y)
#define CHECKVEC(v)        CHECKNAN(v.x); CHECKNAN(v.y); CHECKNAN(v.z)
#define CHECKVECR(v,r)     CHECKNANR(v.x,r); CHECKNANR(v.y,r); CHECKNANR(v.z,r)

#define ASSERT(c)    BAIL(); \
  if (!(c)) { set_py_exc_str(__FILE__, __LINE__, \
                             "assert failed: %s", #c); return; }
#define ASSERTR(c, x)   BAILR(x); \
  if (!(c)) { set_py_exc_str(__FILE__, __LINE__, \
                             "assert failed: %s", #c); return (x); }
#define NULLPTR(p)  ASSERT((p) != NULL)
#define NULLPTRR(p,x)  ASSERTR((p) != NULL, x)
#define EXCEPTION (py_exc_str != NULL)
#define BAIL()  \
  if (EXCEPTION) { SAY("BAIL\n"); return; }
#define BAILR(x)  \
  if (EXCEPTION) { SAY("BAILR\n"); return x; }

#define RAISE(except) { set_py_exc_str(__FILE__, __LINE__, except); return; }
#define RAISER(except, retval) { set_py_exc_str(__FILE__, __LINE__, except); return (retval); }

#endif

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
