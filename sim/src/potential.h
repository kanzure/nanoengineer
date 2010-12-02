// Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
#ifndef POTENTIAL_H_INCLUDED
#define POTENTIAL_H_INCLUDED

#define RCSID_POTENTIAL_H  "$Id$"

extern double stretchPotential(struct part *p, struct stretch *stretch, struct bondStretch *stretchType, double rSquared);

extern double stretchGradient(struct part *p, struct stretch *stretch, struct bondStretch *stretchType, double rSquared);

extern double vanDerWaalsPotential(struct part *p, struct vanDerWaals *vdw, struct vanDerWaalsParameters *parameters, double rSquared);

extern double vanDerWaalsGradient(struct part *p, struct vanDerWaals *vdw, struct vanDerWaalsParameters *parameters, double rSquared);
extern double electrostaticPotential(struct part *p, struct electrostatic *es, struct electrostaticParameters *parameters, double r);

extern double electrostaticGradient(struct part *p, struct electrostatic *es, struct electrostaticParameters *parameters, double r);

extern double calculatePotential(struct part *p, struct xyz *position);

extern void calculateGradient(struct part *p, struct xyz *position, struct xyz *force);

#endif
