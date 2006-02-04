#ifndef NEWTABLES_H_INCLUDED
#define NEWTABLES_H_INCLUDED

#define RCSID_NEWTABLES_H  "$Id$"

/** table length for bond stretch/bending functions */
#define TABLEN 150


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
  
  int isGeneric; // set to non-zero if the above are based on a heuristic
  int warned; // set to non-zero if a warning about using this entry has been printed
  
  struct interpolationTable LippincottMorse;
};

struct vanDerWaalsParameters
{
  char *vdwName;
  
  double rvdW; // in pm (1e-12 m)
  double evdW; // in zJ (1e-21 J)

  // We subtract vInfinity from the potential, so it reaches zero at
  // the end of the interpolation table, rather than have a step
  // there.
  // XXX This changes the depth of the potential well, which may be a problem.
  double vInfinity; // potential at "infinity", the end of the interpolation table

  // Index into the interpolation tables where the potnetial exceeds
  // ExcessiveEnergyLevel.  If a dynamics run references a table entry
  // at less than this index, a warning will be emitted.
  int minPhysicalTableIndex;

  struct interpolationTable Buckingham;
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

  int isGeneric; // set to non-zero if the above are based on a heuristic
  int warned; // set to non-zero if a warning about using this entry has been printed
};

#define MAX_ELEMENT 109

struct atomType
{
  int protons;
  int group;
  int period;
  char symbol[4];
  char *name;
  double mass;                // yg, or yoctograms, or 1e-24 g
  double vanDerWaalsRadius;   // Angstroms, or 1e-10 m
  double e_vanDerWaals;       // zJ, or zeptoJoules, or 1e-21 J
  int n_bonds;
  double covalentRadius;      // Angstroms, or 1e-10 m
};

extern struct atomType periodicTable[MAX_ELEMENT+1];


extern void initializeBondTable(void);

extern void reInitializeBondTable(void);

extern struct bondStretch *getBondStretch(int element1, int element2, char bondOrder);

extern struct bendData *getBendData(int element_center,
                                    enum hybridization centerHybridization,
                                    int element1,
                                    char bondOrder1,
                                    int element2,
                                    char bondOrder2);

extern struct vanDerWaalsParameters *getVanDerWaalsTable(int element1, int element2);

extern struct atomType *getAtomTypeByName(char *symbol);

#endif
