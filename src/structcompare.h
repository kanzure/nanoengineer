/* Copyright (c) 2006 Nanorex, Inc. All rights reserved. */
#ifndef STRUCTCOMPARE_H_INCLUDED
#define STRUCTCOMPARE_H_INCLUDED

#define RCSID_STRUCTCOMPARE_H  "$Id$"

extern int doStructureCompare(int numberOfAtoms,
                              struct xyz *basePositions,
                              struct xyz *initialPositions,
                              int iterLimit,
                              double deviationLimit,
                              double maxDeltaLimit,
                              double maxScale);


#endif
