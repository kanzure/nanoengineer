// Copyright 2005-2006 Nanorex, Inc.  See LICENSE file for details. 
#ifndef PRINTERS_H_INCLUDED
#define PRINTERS_H_INCLUDED

#define RCSID_PRINTERS_H  "$Id$"

extern void traceFileVersion(void);

extern void traceHeader(struct part *part);

extern void traceJigHeader(struct part *part);

extern void traceJigData(struct part *part, struct xyz *positions);

extern void printError(const char *file, int line, int error_type,
		       int doPerror, const char *format, ...);

extern void testAlert(const char *format, ...);

extern void done(const char *format, ...);

#endif
