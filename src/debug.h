/* Copyright (c) 2006 Nanorex, Inc. All rights reserved. */
#ifndef DEBUG_H_INCLUDED
#define DEBUG_H_INCLUDED

#define RCSID_DEBUG_H  "$Id$"

#if 0
#define DBGPRINTF(fmt) fprintf(stderr, fmt)
#define DBGPRINTF1(fmt,a) fprintf(stderr, fmt, a)
#define DBGPRINTF2(fmt,a,b) fprintf(stderr, fmt, a, b)
#else
#define DBGPRINTF(fmt) ((void) 0)
#define DBGPRINTF1(fmt,a) ((void) 0)
#define DBGPRINTF2(fmt,a,b) ((void) 0)
#endif

extern int debug_flags;
#define DEBUG(flag) (debug_flags & (flag))
#define DPRINT(flag, fmt) (DEBUG(flag) ? fprintf(stderr, fmt) : (void) 0)
#define DPRINT1(flag, fmt,a) (DEBUG(flag) ? fprintf(stderr, fmt,a) : (void) 0)
#define DPRINT2(flag, fmt,a,b) (DEBUG(flag) ? fprintf(stderr, fmt,a,b) : (void) 0)
#define DPRINT3(flag, fmt,a,b,c) (DEBUG(flag) ? fprintf(stderr, fmt,a,b,c) : (void) 0)
#define DPRINT4(flag, fmt,a,b,c,d) (DEBUG(flag) ? fprintf(stderr, fmt,a,b,c,d) : (void) 0)
#define DPRINT5(flag, fmt,a,b,c,d,e) (DEBUG(flag) ? fprintf(stderr, fmt,a,b,c,d,e) : (void) 0)
#define DPRINT6(flag, fmt,a,b,c,d,e,f) (DEBUG(flag) ? fprintf(stderr, fmt,a,b,c,d,e,f) : (void) 0)

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
#define D_STRESS_MOVIE    (1<<12)
#define D_VERIFY_VDW      (1<<13)
#define D_MINIMIZE_PARAMETER_GUESS (1<<14)
#define D_DYNAMICS_SIMPLE_MOVIE (1<<15)
#define D_SKIP_TORSION (1<<16)
#define D_SKIP_OUT_OF_PLANE (1<<17)
#define D_GRADIENT_COMPARISON (1<<18)
#define D_PYREX_SIM (1<<19)

#define TYPE_ERROR 1
#define TYPE_WARNING 2
#define TYPE_INFO 3

#define ERROR(fmt) (printError(__FILE__, __LINE__, TYPE_ERROR, 0, fmt))
#define ERROR1(fmt,a) (printError(__FILE__, __LINE__, TYPE_ERROR, 0, fmt, a))
#define ERROR2(fmt,a,b) (printError(__FILE__, __LINE__, TYPE_ERROR, 0, fmt, a, b))
#define ERROR3(fmt,a,b,c) (printError(__FILE__, __LINE__, TYPE_ERROR, 0, fmt, a, b, c))
#define WARNING(fmt) (printError(__FILE__, __LINE__, TYPE_WARNING, 0, fmt))
#define WARNING1(fmt,a) (printError(__FILE__, __LINE__, TYPE_WARNING, 0, fmt, a))
#define WARNING2(fmt,a,b) (printError(__FILE__, __LINE__, TYPE_WARNING, 0, fmt, a, b))
#define WARNING3(fmt,a,b,c) (printError(__FILE__, __LINE__, TYPE_WARNING, 0, fmt, a, b, c))
#define INFO(fmt) (printError(__FILE__, __LINE__, TYPE_INFO, 0, fmt))
#define INFO1(fmt,a) (printError(__FILE__, __LINE__, TYPE_INFO, 0, fmt, a))
#define INFO2(fmt,a,b) (printError(__FILE__, __LINE__, TYPE_INFO, 0, fmt, a, b))
#define INFO3(fmt,a,b,c) (printError(__FILE__, __LINE__, TYPE_INFO, 0, fmt, a, b, c))
#define INFO4(fmt,a,b,c,d) (printError(__FILE__, __LINE__, TYPE_INFO, 0, fmt, a, b, c, d))
#define ERROR_ERRNO(fmt) (printError(__FILE__, __LINE__, TYPE_ERROR, 1, fmt))
#define ERROR_ERRNO1(fmt,a) (printError(__FILE__, __LINE__, TYPE_ERROR, 1, fmt, a))
#define WARNING_ERRNO(fmt) (printError(__FILE__, __LINE__, TYPE_WARNING, 1, fmt))
#define WARNING_ERRNO1(fmt,a) (printError(__FILE__, __LINE__, TYPE_WARNING, 1, fmt, a))

#endif
