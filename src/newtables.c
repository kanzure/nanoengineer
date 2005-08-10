
#include "simulator.h"

static struct bondStretch *
getBondStretchEntry(int element1, int element2, char bondOrder);

struct atomType periodicTable[MAX_ELEMENT+1];

static struct bondStretch *
newBondStretch(char *bondName, double ks, double r0, double de, double beta, int generic)
{
  struct bondStretch *stretch;

  stretch = allocate(sizeof(struct bondStretch));
  stretch->bondName = copy_string(bondName);
  stretch->ks = ks;
  stretch->r0 = r0;
  stretch->de = de;
  stretch->beta = beta;
  stretch->isGeneric = generic;
  initializeBondStretchInterpolater(stretch);
  return stretch;
}

static struct bendData *
newBendData(char *bendName, double kb, double theta0)
{
  struct bendData *bend;

  bend = allocate(sizeof(struct bendData));
  bend->bendName = copy_string(bendName);
  bend->kb = kb;
  bend->theta0 = theta0;
  bend->cosTheta0 = cos(theta0);
  return bend;
}

static void
generateBondName(char *bondName, int element1, int element2, char bondOrder)
{
  int elt;
  if (element2 < element1) {
    elt = element1;
    element1 = element2;
    element2 = elt;
  }
  sprintf(bondName, "%s-%c-%s", periodicTable[element1].symbol,
          bondOrder, periodicTable[element2].symbol);
}

static void
generateBendName(char *bendName,
                 int element_center,
                 int element1,
                 char bondOrder1,
                 int element2,
                 char bondOrder2)
{
  int elt;
  char bnd;
  if (element2 < element1) {
    elt = element1;
    element1 = element2;
    element2 = elt;
    bnd = bondOrder1;
    bondOrder1 = bondOrder2;
    bondOrder2 = bnd;
  }
  sprintf(bendName, "%s-%c-%s-%c-%s", periodicTable[element1].symbol,
          bondOrder1, periodicTable[element_center].symbol,
          bondOrder2, periodicTable[element2].symbol);
}

static struct hashtable *bondStretchHashtable;
static struct hashtable *bendDataHashtable;
static struct hashtable *deHashtable;
static struct hashtable *vanDerWaalsHashtable;

static struct bondStretch *
addBondStretch(char *bondName, double ks, double r0, double de, double beta, int generic)
{
  struct bondStretch *stretch;

  stretch = newBondStretch(bondName, ks, r0, de, beta, generic);
  hashtable_put(bondStretchHashtable, bondName, stretch);
  return stretch;
}

static struct bendData *
addBendData(char *bendName, double kb, double theta0)
{
  struct bendData *bend;

  bend = newBendData(bendName, kb, theta0);
  hashtable_put(bendDataHashtable, bendName, bend);
  return bend;
}

static void
addInitialBondStretch(int element1, int element2, char order, double ks, double r0, double de, double beta)
{
  struct bondStretch *stretch;
  char bondName[10]; // expand if atom types become longer than 2 chars
  
  generateBondName(bondName, element1, element2, order);
  stretch = newBondStretch(bondName, ks, r0, de, beta*1e-2, 0);
  hashtable_put(bondStretchHashtable, bondName, stretch);
}

static void
addInitialBendData(char *bendName, double kb, double theta0)
{
  struct bendData *bend;

  bend = newBendData(bendName, kb*1000.0, theta0);
  hashtable_put(bendDataHashtable, bendName, bend);
}

static void
addDeTableEntry(char *bondName, double de)
{
  struct deTableEntry *entry = (struct deTableEntry *)allocate(sizeof(struct deTableEntry));
  entry->de = de;
  hashtable_put(deHashtable, bondName, entry);
}

static void
setElement(int protons,
           int group,
           int period,
           char *symbol,
           char *name,
           double mass,
           double vanDerWaalsRadius,
           double e_vanDerWaals,
           int n_bonds,
           double covalentRadius)
{
  if (e_vanDerWaals < 0.1) {
    e_vanDerWaals = 0.3 + protons * protons / 190.0;
  }
  periodicTable[protons].protons = protons;
  periodicTable[protons].group = group;
  periodicTable[protons].period = period;
  periodicTable[protons].name = name;
  periodicTable[protons].symbol[0] = symbol[0];
  periodicTable[protons].symbol[1] = symbol[1];
  periodicTable[protons].symbol[2] = symbol[2];
  periodicTable[protons].symbol[3] = symbol[3]; // we inadvertantly copy past end of string on many elements.
  periodicTable[protons].mass = mass;
  periodicTable[protons].vanDerWaalsRadius = vanDerWaalsRadius;
  periodicTable[protons].e_vanDerWaals = e_vanDerWaals;
  periodicTable[protons].n_bonds = n_bonds;
  periodicTable[protons].covalentRadius = covalentRadius;
}


void
initializeBondTable()
{
  // groups 9-22 are lanthanides
  // groups 8-31 are transition metals
  //
  // an e_vanDerWaals value < .1 will be calculated in setElement()
  //
  // protons, group, period, symbol, name, mass, vanDerWaalsRadius,
  //    e_vanDerWaals, n_bonds, covalentRadius
  //
  //          Z grp per sym   name           mass    rvdw  evdw bnds rcov
  //
 
  setElement( 0,  1, 1, "X",  "Singlet",    17.000,  1.1,  0.000, 1, 0);
  setElement( 1,  1, 1, "H",  "Hydrogen",    1.6737, 0.77, 0.382, 1, 30);
  setElement( 2,  0, 1, "He", "Helium",      6.646,  1.4,  0.000, 0, 0);
 
  setElement( 3,  1, 2, "Li", "Lithium",    11.525,  0.97, 0.000, 1, 152);
  setElement( 4,  2, 2, "Be", "Beryllium",  14.964,  1.10, 0.000, 2, 114);
  setElement( 5,  3, 2, "B",  "Boron",      17.949,  1.46, 0.000, 3, 83);
  setElement( 6,  4, 2, "C",  "Carbon",     19.925,  1.43, 0.357, 4, 77);
  setElement( 7,  5, 2, "N",  "Nitrogen",   23.257,  1.39, 0.447, 3, 70);
  setElement( 8,  6, 2, "O",  "Oxygen",     26.565,  1.35, 0.406, 2, 66);
  setElement( 9,  7, 2, "F",  "Fluorine",   31.545,  1.29, 0.634, 1, 64);
  setElement(10,  0, 2, "Ne", "Neon",       33.49,   1.82, 0.000, 0, 0);
 
  setElement(11,  1, 3, "Na", "Sodium",     38.1726, 1.29, 0.000, 1, 186);
  setElement(12,  2, 3, "Mg", "Magnesium",  40.356,  1.15, 0.000, 2, 160);
  setElement(13,  3, 3, "Al", "Aluminum",   44.7997, 2.0,  0.000, 3, 125);
  setElement(14,  4, 3, "Si", "Silicon",    46.6245, 1.82, 1.137, 4, 116);
  setElement(15,  5, 3, "P",  "Phosphorus", 51.429,  1.78, 1.365, 3, 110);
  setElement(16,  6, 3, "S",  "Sulfur",     53.233,  1.74, 1.641, 2, 104);
  setElement(17,  7, 3, "Cl", "Chlorine",   58.867,  1.69, 1.950, 1, 99);
  setElement(18,  0, 3, "Ar", "Argon",      62.33,   1.88, 0.000, 0, 0);

  setElement(19,  1, 4, "K",  "Potassium",  64.9256, 1.59, 0.000, 1, 231);
  setElement(20,  2, 4, "Ca", "Calcium",    66.5495, 1.27, 0.000, 2, 197);
  setElement(21,  8, 4, "Sc", "Scandium",   74.646,  2.0,  0.000, 0, 60);
  setElement(22, 23, 4, "Ti", "Titanium",   79.534,  2.0,  0.000, 0, 147);
  setElement(23, 24, 4, "V",  "Vanadium",   84.584,  2.0,  0.000, 0, 132);
  setElement(24, 25, 4, "Cr", "Chromium",   86.335,  2.0,  0.000, 0, 125);
  setElement(25, 26, 4, "Mn", "Manganese",  91.22,   2.0,  0.000, 0, 112);
  setElement(26, 27, 4, "Fe", "Iron",       92.729,  2.0,  0.000, 0, 124);
  setElement(27, 28, 4, "Co", "Cobalt",     97.854,  2.0,  0.000, 0, 125);
  setElement(28, 29, 4, "Ni", "Nickel",     97.483,  2.3,  0.000, 0, 125);
  setElement(29, 30, 4, "Cu", "Copper",    105.513,  2.3,  0.000, 0, 128);
  setElement(30, 31, 4, "Zn", "Zinc",      108.541,  2.3,  0.000, 0, 133);
  setElement(31,  3, 4, "Ga", "Gallium",   115.764,  2.3,  0.000, 0, 135);
  setElement(32,  4, 4, "Ge", "Germanium", 120.53,   2.0,  0.000, 4, 122);
  setElement(33,  5, 4, "As", "Arsenic",   124.401,  2.0,  0.000, 3, 120);
  setElement(34,  6, 4, "Se", "Selenium",  131.106,  1.88, 0.000, 2, 119);
  setElement(35,  7, 4, "Br", "Bromine",   132.674,  1.83, 0.000, 1, 119);
  setElement(36,  0, 4, "Kr", "Krypton",   134.429,  1.9,  0.000, 0,  0);

  setElement(51,  5, 5, "Sb", "Antimony",  124.401,  2.2,  0.000, 3, 144);
  setElement(52,  6, 5, "Te", "Tellurium", 131.106,  2.1,  0.000, 2, 142);
  setElement(53,  7, 5, "I",  "Iodine",    132.674,  2.0,  0.000, 1, 141);
  setElement(54,  0, 5, "Xe", "Xenon",     134.429,  1.9,  0.000, 0, 0);

  bondStretchHashtable = hashtable_new(40);

#include "bonds.h"

#ifdef OLD_BONDS
  addInitialBondStretch( 1, 6, '1',  460.0,  111.3, 0.671, 1.851); // H-C
  addInitialBondStretch( 1, 8, '1',  460.0,   94.2, 0.753, 1.747); // H-O
  addInitialBondStretch( 1,14, '1',  359.4,  125.6, 0.627, 1.693); // H-Si
  addInitialBondStretch( 1,16, '1',  360.0,  125.2, 0.606, 1.769); // H-S
  addInitialBondStretch( 1,17, '1',  380.0,  134.6, 0.716, 1.628); // H-Cl
  addInitialBondStretch( 6, 6, '1',  440.0,  152.3, 0.556, 1.989); // C-C
  addInitialBondStretch( 6, 7, '1',  510.0,  143.8, 0.509, 2.238); // C-N
  addInitialBondStretch( 6, 8, '1',  536.0,  140.2, 0.575, 2.159); // C-O
  addInitialBondStretch( 6, 9, '1',  510.0,  139.2, 0.887, 1.695); // C-F
  addInitialBondStretch( 6,14, '1',  297.0,  188.0, 0.624, 1.543); // C-Si
  addInitialBondStretch( 6,15, '1',  291.0,  185.4, 0.852, 1.306); // C-P
  addInitialBondStretch( 6,16, '1',  321.3,  181.5, 0.539, 1.726); // C-S
  addInitialBondStretch( 6,17, '1',  323.0,  179.5, 0.591, 1.653); // C-Cl
  addInitialBondStretch( 6,35, '1',  230.0,  194.9, 0.488, 1.536); // C-Br
  addInitialBondStretch( 7, 7, '1',  560.0,  138.1, 0.417, 2.592); // N-N

  addInitialBondStretch( 8, 8, '1',  781.0,  147.0, 0.272, 3.789); // O-O
  addInitialBondStretch( 8,14, '1',  550.0,  162.0, 0.89,  1.757); // O-Si
  addInitialBondStretch( 8,15, '1',  290.0,  161.5, 0.994, 1.207); // O-P

  addInitialBondStretch(14,14, '1',  185.0,  233.2, 0.559, 1.286); // Si-Si
  addInitialBondStretch(14,16, '1',  219.37, 213.0, 0.58,  1.375); // Si-S
  addInitialBondStretch(16,16, '1',  310.0,  202  , 0.706, 1.481); // S-S

  addInitialBondStretch( 6, 6, '2',  960.0,  133.7, 1.207, 1.994); // C=C
  addInitialBondStretch( 6, 6, '3', 1560.0,  121.2, 1.616, 2.198); // C<3>C
#endif
  
  deHashtable = hashtable_new(10);

  addDeTableEntry("H-1-N",  0.75);
  addDeTableEntry("N-1-O",  0.383);
  addDeTableEntry("N-1-F",  0.422);
  addDeTableEntry("F-1-S",  0.166);
  addDeTableEntry("O-1-F",  0.302);
  addDeTableEntry("C-1-I",  0.373);
  addDeTableEntry("O-1-Cl", 0.397);
  addDeTableEntry("O-1-I",  0.354);
  addDeTableEntry("S-1-Cl", 0.489);

  bendDataHashtable = hashtable_new(40);

#include "bends.h"

#ifdef OLD_BENDS
  //                 bendName      kb, theta0
  //                         zJ/rad^2, radians
  //
  addInitialBendData("C-1-C-1-C", 450, 1.911);
  addInitialBendData("H-1-C-1-C", 360, 1.909);
  addInitialBendData("H-1-C-1-H", 320, 1.909);
  addInitialBendData("C-1-C-1-F", 650, 1.911);
  addInitialBendData("F-1-C-1-F", 1070, 1.869);
  addInitialBendData("O-1-C-1-O", 460, 1.727);
  addInitialBendData("S-1-C-1-S", 420, 2.024);
  addInitialBendData("C-1-O-1-O", 635, 1.722);
  addInitialBendData("C-1-O-1-P", 770, 2.024);
  addInitialBendData("C-1-O-1-N", 500, 2.094);
  addInitialBendData("C-1-O-1-Si", 400, 2.000);
  addInitialBendData("Si-1-O-1-Si", 150, 2.44);
  addInitialBendData("N-1-O-1-N", 200, 2.286);
  addInitialBendData("P-1-O-1-P", 200, 2.826);

  addInitialBendData("H-1-O-1-C", 770, 1.864);
  addInitialBendData("C-1-O-1-C", 770, 1.864);
  addInitialBendData("C-1-N-1-C", 630, 1.880);
  addInitialBendData("C-1-N-1-N", 740, 1.841);

  addInitialBendData("C-1-C-1-O", 700, 1.876);
  addInitialBendData("N-1-C-1-O", 630, 1.900);
  addInitialBendData("C-1-C-1-N", 570, 1.911);
  addInitialBendData("Si-1-Si-1-Si", 350, 1.943);
  addInitialBendData("Si-1-S-1-Si", 350, 1.726);
  addInitialBendData("S-1-Si-1-S", 350, 1.815);
  addInitialBendData("C-1-Si-1-O", 350, 1.893);
  addInitialBendData("C-1-Si-1-Si", 750, 1.919);
  addInitialBendData("O-1-Si-1-O", 450, 1.980);
  addInitialBendData("Si-1-O-1-P", 450, 1.726); // XXX

  addInitialBendData("Si-1-C-1-Si", 400, 2.016);
  addInitialBendData("C-1-Si-1-C", 480, 1.934);
  addInitialBendData("Cl-1-C-1-Cl", 1080, 1.950);
  addInitialBendData("C-1-C-1-S", 550, 1.902);
  addInitialBendData("C-1-S-1-C", 720, 1.902);
  addInitialBendData("C-1-S-1-S", 1168, 1.795);
  addInitialBendData("C-1-P-1-C", 576, 1.675);
  addInitialBendData("O-1-P-1-O", 450, 1.736);
  addInitialBendData("O-1-P-1-Si", 450, 1.736); // XXX

  addInitialBendData("C-2-C-1-C", 550, 2.119); 
  addInitialBendData("C-3-C-1-C", 200, 3.1415926); 
  addInitialBendData("C-1-C-2-O", 460, 2.138);
#endif

  vanDerWaalsHashtable = hashtable_new(40);
}

static double
getDe(char *bondName)
{
  struct deTableEntry *entry = (struct deTableEntry *)hashtable_get(deHashtable, bondName);
  if (entry != NULL) {
    return entry->de;
  }
  return 0.58;
}

static struct bondStretch *
interpolateGenericBondStretch(char *bondName, int element1, int element2, float order)
{
  struct bondStretch *singleStretch;
  struct bondStretch *doubleStretch;
  double r0;
  double ks;
  double de;
  double beta;

  singleStretch = getBondStretchEntry(element1, element2, '1');
  doubleStretch = getBondStretchEntry(element1, element2, '2');

  // XXX check that singleStretch->r0 and doubleStretch->r0 are > 0!!!

  // interpolate r0 reciprocally:
  r0 = 1.0 / ((order - 1.0) / singleStretch->r0 + (2.0 - order) / doubleStretch->r0);

  // interpolate ks and de linearly:
  ks = (order - 1.0) * singleStretch->ks + (2.0 - order) * doubleStretch->ks ;
  de = (order - 1.0) * singleStretch->de + (2.0 - order) * doubleStretch->de ;

  beta = sqrt(ks / (2.0 * de));
  return addBondStretch(bondName, ks, r0, de, beta*1e-2, 1);
}

/* generate a (hopefully not too bogus) set of bond stretch parameters
   for a bond type that we haven't entered real data for */
static struct bondStretch *
generateGenericBondStretch(char *bondName, int element1, int element2, char bondOrder)
{
  double ks, r0, de, beta;

  switch (bondOrder) {
  default: // XXX Falls through to single bond case.  WRONG!!!!
  case '1':
    ks = 0.0;
    de = getDe(bondName);
    beta = 0.0;
    r0 = periodicTable[element1].covalentRadius + periodicTable[element2].covalentRadius ;
    if (r0 <= 0.0) {
      // XXX warn about this
      // maybe better to just fill out the periodic table...
      r0 = 1.0;
    }
    beta = 0.4 + 125.0 / (r0 * de);
    ks = 200.0 * de * beta * beta ;
    if (ks > 1000.0) {
      ks = 1000.0;
    }
    break;
  case 'a':
    return interpolateGenericBondStretch(bondName, element1, element2, 1.5);
  case 'g':
    return interpolateGenericBondStretch(bondName, element1, element2, 1.3333333333333);
  case '2':
    ks = 0.0;
    de = getDe(bondName);
    beta = 0.0;
    r0 = periodicTable[element1].covalentRadius + periodicTable[element2].covalentRadius ;
    if (r0 <= 0.0) {
      // XXX warn about this
      // maybe better to just fill out the periodic table...
      r0 = 1.0;
    }
    r0 *= 0.8; // XXX this is just completly wrong, assuming double bonds are 80% shorter than single
    beta = 0.4 + 125.0 / (r0 * de);
    ks = 200.0 * de * beta * beta ;
    if (ks > 1000.0) {
      ks = 1000.0;
    }
    break;
  case '3':
    ks = 0.0;
    de = getDe(bondName);
    beta = 0.0;
    r0 = periodicTable[element1].covalentRadius + periodicTable[element2].covalentRadius ;
    if (r0 <= 0.0) {
      // XXX warn about this
      // maybe better to just fill out the periodic table...
      r0 = 1.0;
    }
    r0 *= 0.7; // XXX this is just completly wrong, assuming triple bonds are 70% shorter than single
    beta = 0.4 + 125.0 / (r0 * de);
    ks = 200.0 * de * beta * beta ;
    if (ks > 1000.0) {
      ks = 1000.0;
    }
  }
  
  return addBondStretch(bondName, ks, r0, de, beta*1e-2, 1);
}

/* generate a (hopefully not too bogus) set of bond stretch parameters
   for a bond type that we haven't entered real data for */
static struct bendData *
generateGenericBendData(char *bendName,
                        int element_center,
                        int element1,
                        char bondOrder1,
                        int element2,
                        char bondOrder2)
{
  double len;
  double kb, theta0;

  // XXX only correct for bond order 1 on both bonds  FIX!!!

  len = periodicTable[element_center].covalentRadius +
    periodicTable[element1].covalentRadius +
    periodicTable[element2].covalentRadius;
  
  kb = 45e6 / (len * len) + len * 1.3 - 475.0;
  if (kb > 2000.0) {
    kb = 2000.0;
  }
  theta0 = 1.9106;

  return addBendData(bendName, kb*1000.0, theta0);
}

static struct interpolationTable *
generateVanDerWaals(char *bondName, int element1, int element2)
{
  struct interpolationTable *vdw;

  vdw = (struct interpolationTable *)allocate(sizeof(struct interpolationTable));
  initializeVanDerWaalsInterpolator(vdw, element1, element2);
  hashtable_put(vanDerWaalsHashtable, bondName, vdw);
  return vdw;
}

static struct bondStretch *
getBondStretchEntry(int element1, int element2, char bondOrder)
{
  struct bondStretch *entry;
  char bondName[10]; // expand if atom types become longer than 2 chars
  
  generateBondName(bondName, element1, element2, bondOrder);
  entry = (struct bondStretch *)hashtable_get(bondStretchHashtable, bondName);
  if (entry == NULL) {
    entry = generateGenericBondStretch(bondName, element1, element2, bondOrder);
  }
  return entry;
}

struct bondStretch *
getBondStretch(int element1, int element2, char bondOrder)
{
  struct bondStretch *entry;

  entry = getBondStretchEntry(element1, element2, bondOrder);
  // XXX if (entry->isGeneric) { WARN ABOUT THIS }
  return entry;
}

struct bendData *
getBendData(int element_center,
            int element1,
            char bondOrder1,
            int element2,
            char bondOrder2)
{
  struct bendData *bend;
  char bendName[25]; // expand if atom types become longer than 2 chars
  
  generateBendName(bendName, element_center, element1, bondOrder1, element2, bondOrder2);
  bend = (struct bendData *)hashtable_get(bendDataHashtable, bendName);
  if (bend == NULL) {
    bend = generateGenericBendData(bendName, element_center, element1, bondOrder1, element2, bondOrder2);
  }
  return bend;
}

struct interpolationTable *
getVanDerWaalsTable(int element1, int element2)
{
  struct interpolationTable *vdw;
  char bondName[10]; // expand if atom types become longer than 2 chars

  generateBondName(bondName, element1, element2, 'v');
  vdw = (struct interpolationTable *)hashtable_get(vanDerWaalsHashtable, bondName);
  if (vdw == NULL) {
    vdw = generateVanDerWaals(bondName, element1, element2);
  }
  return vdw;
}


static void
compare(char *bondName, char *parameter, double old, double new)
{
  if (fabs(old - new) > 0.005) {
    printf("%s %s old %f new %f dif: %f\n", bondName, parameter, old, new, old-new);
  }
}

#if 0
void
testNewBondStretchTable()
{
  int i;
  int e1, e2;
  double ks, r0, de, beta;
  struct bondStretch *stretch;
  int b1typ, b2typ, b1, b2, ec1, ec2;
  double kb, theta0;
  struct bendData *bend;
  
  initializeBondTable();
  for (i=0; i<BSTABSIZE; i++) {
    e1 = bstab[i].a1;
    e2 = bstab[i].a2;
    ks = bstab[i].ks;
    r0 = bstab[i].r0;
    de = bstab[i].de;
    beta = bstab[i].beta;
    stretch = getBondStretch(e1, e2, '1');
    compare(stretch->bondName, "ks", ks, stretch->ks);
    compare(stretch->bondName, "r0", r0, stretch->r0);
    compare(stretch->bondName, "de", de, stretch->de);
    compare(stretch->bondName, "beta", beta, stretch->beta);
  }
  for (i=0; i<BENDATASIZE; i++) {
    b1typ = bendata[i].b1typ;
    b2typ = bendata[i].b2typ;
    b1 = findbond(b1typ);
    b2 = findbond(b2typ);
    e1 = b1typ < 0 ? bstab[b1].a1 : bstab[b1].a2 ;
    e2 = b2typ < 0 ? bstab[b2].a1 : bstab[b2].a2 ;
    ec1 = b1typ < 0 ? bstab[b1].a2 : bstab[b1].a1 ;
    ec2 = b2typ < 0 ? bstab[b2].a2 : bstab[b2].a1 ;
    
    kb = bendata[i].kb;
    theta0 = bendata[i].theta0;
    bend = getBendData(ec1, e1, '1', e2, '1');
    //printf("%s %f %f\n", bend->bendName, kb, theta0);
    compare(bend->bendName, "kb", kb/1000000.0, bend->kb/1000000.0);
    compare(bend->bendName, "theta0", theta0, bend->theta0);
  }
  exit(0);
}
#endif
