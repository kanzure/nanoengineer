
struct bondStretch 
{
  char *bondName;

  /** bond type, atom types & order */
  //int typ, ord, a1, a2;

  double ks;   // stiffness in N/m
  double r0;   // base radius in pm, or 1e-12 m
  double de;   // aJ, or 1e-18 J, for Morse
  double beta; // 1e12 m^-1, for Morse

  int isGeneric; // set to non-zero if the above are based on a heuristic
  
  struct interpolationTable table;
};

struct deTableEntry
{
  double de;
};

struct bendData
{
  char *bendName;
  double kb;
  double theta0;
  double cosTheta0;
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


extern void initializeBondTable();

extern struct bondStretch *getBondStretch(int element1, int element2, char bondOrder);

extern struct bendData *getBendData(int element_center,
                                    int element1,
                                    char bondOrder1,
                                    int element2,
                                    char bondOrder2);

extern struct interpolationTable *getVanDerWaalsTable(int element1, int element2);

