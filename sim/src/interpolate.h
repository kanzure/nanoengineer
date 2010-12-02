// Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
#ifndef INTERPOLATE_H_INCLUDED
#define INTERPOLATE_H_INCLUDED

#define RCSID_INTERPOLATE_H  "$Id$"

extern double potentialLippincottMorse(double r, void *p);

extern double gradientLippincottMorse(double r, void *p);

extern void initializeBondStretchInterpolater(struct bondStretch *stretch);

extern double gradientBuckingham(double r, void *p);

extern double potentialBuckingham(double r, void *p);

extern double potentialModifiedBuckingham(double r, void *p);

extern double gradientModifiedBuckingham(double r, void *p);

extern void initializeVanDerWaalsInterpolator(struct vanDerWaalsParameters *vdw);

extern double potentialCoulomb(double r, void *p);

extern double gradientCoulomb(double r, void *p);

extern double potentialModifiedCoulomb(double r, void *p);

extern double gradientModifiedCoulomb(double r, void *p);

extern void initializeElectrostaticInterpolator(struct electrostaticParameters *es);

extern void printPotentialAndGradientFunctions(char *name, double initial, double increment, double limit);

extern void printBendStretch(void);

#endif
