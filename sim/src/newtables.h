// Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
#ifndef NEWTABLES_H_INCLUDED
#define NEWTABLES_H_INCLUDED

#define RCSID_NEWTABLES_H  "$Id$"

/** table length for bond stretch/bending functions */
#define TABLEN 150

#define QUALITY_INTERPOLATED 4
#define QUALITY_GUESSED      3
#define QUALITY_INACCURATE   0


struct interpolationTable {
  double start;
  double scale;
  // y = ax^3 + bx^2 + cx + d    or...
  // y = ((ax + b)x + c)x + d
  // y' = 3ax^2 + 2bx + c        or...
  // y' = (3ax + 2b)x + c
  double a[TABLEN];
  double b[TABLEN];
  double c[TABLEN];
  double d[TABLEN];
};

struct bondStretch 
{
  char *bondName;

  /** bond type, atom types & order */
  //int typ, ord, a1, a2;

  double ks;   // stiffness in N/m
  double r0;   // base radius in pm, or 1e-12 m
  double de;   // aJ, or 1e-18 J
  double beta; // sqrt(ks/2 de), 1e12 m^-1, for Morse
  
  double inflectionR; // r value in pm where d^2(Lippincott(r)) / dr^2 == 0

  // These are the indices into the interpolation tables where the
  // potential exceeds ExcessiveEnergyLevel.  If a dynamics run
  // references table entries outside these bounds, a warning will be
  // emitted.
  int maxPhysicalTableIndex;
  int minPhysicalTableIndex;

  // For minimize, the potential function extends as a cubic
  // polynomial beyond the end of the interpolation table:
  // potential = potentialExtensionA
  //           + potentialExtensionB * r
  //           + potentialExtensionC * r^2
  //           + potentialExtensionD * r^3
  double potentialExtensionA;
  double potentialExtensionB;
  double potentialExtensionC;
  double potentialExtensionD;
  
  int parameterQuality; // how sure are we of these parameters

  // Non-zero if this stretch should be pure quadratic, instead of
  // Lippincott-Morse.  Set to 1 if GROMACS should consider this
  // stretch to be a chemical bond (for purposes of excluding
  // non-bonded interactions), or 6 for a quadratic potential without
  // the bond.
  int quadratic;
  
  int warned; // set to non-zero if a warning about using this entry has been printed
  
  struct interpolationTable LippincottMorse;
};

struct vanDerWaalsParameters
{
  char *vdwName;
  
  double rvdW; // in pm (1e-12 m)
  double evdW; // in zJ (1e-21 J)

  // Transition interval for smooth cutoff.  Normal function is used
  // for 0<r<cutoffRadiusStart.  For
  // cutoffRadiusStart<r<cutoffRadiusEnd the function is multiplied by
  // a smooth transition function.  For cutoffRadiusEnd<r, the value
  // is identically zero.  See smoothCutoff() in interpolate.c.  If
  // cutoffRadiusEnd<=cutoffRadiusStart, no transition function is
  // used, instead, the potential is translated by vInfinity, so it
  // reaches zero at cutoffRadiusEnd.
  double cutoffRadiusStart; // in pm (1e-12 m)
  double cutoffRadiusEnd; // in pm (1e-12 m)
  
  // If no transition function is used, we subtract vInfinity from the
  // potential, so it reaches zero at the end of the interpolation
  // table, rather than have a step there.
  // XXX This changes the depth of the potential well, which may be a problem.
  double vInfinity; // potential at "infinity", the end of the interpolation table

  // Index into the interpolation tables where the potential exceeds
  // ExcessiveEnergyLevel.  If a dynamics run references a table entry
  // at less than this index, a warning will be emitted.
  int minPhysicalTableIndex;

  struct interpolationTable Buckingham;
};

struct electrostaticParameters
{
  char *electrostaticName;

  double k; // in aJ pm (1e-30 J m), potential is k/r, gradient is -k/r^2

  double vInfinity; // potential at "infinity", the end of the interpolation table
  
  double cutoffRadiusStart; // in pm (1e-12 m)
  double cutoffRadiusEnd; // in pm (1e-12 m)

  // Index into the interpolation tables where the potential exceeds
  // ExcessiveEnergyLevel.  If a dynamics run references a table entry
  // at less than this index, a warning will be emitted.
  int minPhysicalTableIndex;

  struct interpolationTable Coulomb;
};

struct deTableEntry
{
  double de;
};

struct bendData
{
  char *bendName;
  double kb;      // stiffness in yJ / rad^2 (1e-24 J/rad^2)
  double theta0;
  double cosTheta0;

  int parameterQuality; // how sure are we of these parameters
  int warned; // set to non-zero if a warning about using this entry has been printed
};

#define MAX_ELEMENT 109

struct atomType
{
  int protons;
  int group;
  int period;
  char *symbol;
  char *name;
  double mass;                // yg, or yoctograms, or 1e-24 g
  double vanDerWaalsRadius;   // Angstroms, or 1e-10 m
  double e_vanDerWaals;       // zJ, or zeptoJoules, or 1e-21 J
  int n_bonds;
  double covalentRadius;      // pm, or 1e-12 m
  double charge;              // multiple of proton charge
  int refCount;
  int isVirtual;              // type for a gromacs virtual interaction site
  struct atomType *parent;
};

struct patternParameter
{
  double value;
  double angleUnits;
  char *stringValue;
};

extern int numStruts;

extern struct atomType *getAtomTypeByIndex(int atomTypeIndex);

extern int isAtomTypeValid(int atomTypeIndex);

extern struct bondStretch *newBondStretch(char *bondName,
                                          double ks,
                                          double r0,
                                          double de,
                                          double beta,
                                          double inflectionR,
                                          int quality,
                                          int quadratic);

extern struct bendData *newBendData(char *bendName, double kb, double theta0, int quality);

extern struct atomType *getAtomTypeByName(char *symbol);

extern struct patternParameter *getPatternParameter(char *name);

extern void initializeBondTable(void);

extern void destroyBondTable(void);

extern void reInitializeBondTable(void);

extern double getBondEquilibriumDistance(int element1, int element2, char bondOrder);

extern struct bondStretch *getBondStretch(int element1, int element2, char bondOrder);

extern struct bendData *getBendData(int element_center,
                                    enum hybridization centerHybridization,
                                    int element1,
                                    char bondOrder1,
                                    int element2,
                                    char bondOrder2);

extern struct vanDerWaalsParameters *getVanDerWaalsTable(int element1, int element2);

extern struct electrostaticParameters *getElectrostaticParameters(int element1, int element2);

#endif
