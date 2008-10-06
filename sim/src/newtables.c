// Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 

#include "simulator.h"

static char const rcsid[] = "$Id$";

static struct bondStretch *
getBondStretchEntry(int element1, int element2, char bondOrder);

static struct hashtable *periodicHashtable = NULL;
static struct hashtable *patternParameterHashtable = NULL;

struct atomType *
getAtomTypeByIndex(int atomTypeIndex)
{
  char buf[256];
  struct atomType *entry;

  if (periodicHashtable == NULL) {
    ERROR("getAtomTypeByIndex called before periodic table initialization");
    return NULL;
  }
  sprintf(buf, "%d", atomTypeIndex);
  entry = (struct atomType *)hashtable_get(periodicHashtable, buf);
  if (entry == NULL) {
    entry = (struct atomType *)hashtable_get(periodicHashtable, "0");
    WARNING1("using undefined atomType %d", atomTypeIndex);
    hashtable_put(periodicHashtable, buf, entry); // this should suppress further warnings
  }
  return entry;
}

int
isAtomTypeValid(int atomTypeIndex)
{
  char buf[256];
  struct atomType *entry;

  if (periodicHashtable == NULL) {
    ERROR("isAtomTypeValid called before periodic table initialization");
    return 0;
  }
  sprintf(buf, "%d", atomTypeIndex);
  entry = (struct atomType *)hashtable_get(periodicHashtable, buf);
  if (entry == NULL) {
    return 0;
  }
  return 1;
}

struct atomType *
getAtomTypeByName(char *symbol)
{
  if (periodicHashtable == NULL) {
    ERROR("getAtomTypeByName called before periodic table initialization");
    return NULL;
  }
  return (struct atomType *)hashtable_get(periodicHashtable, symbol);
}

// returns non-zero if it correctly parses bondName and fills in
// remaining arguments
static int
parseBondName(char *bondName, int *element1, int *element2, char *bondOrder)
{
  // will accept El-o-El, El--El, or El-El.  Latter two default to
  // bondOrder==1
  char *tok;
  struct atomType *at;
  
  if ((tok = strtok(bondName, "-")) == NULL) {
    return 0;
  }
  at = getAtomTypeByName(tok);
  if (at == NULL) {
    return 0;
  }
  *element1 = at->protons;
  if ((tok = strtok(NULL, "-")) == NULL) {
    return 0;
  }
  *bondOrder = '1';
  if (tok[1] == '\0') {
    switch (tok[0]) {
    case '1':
    case '2':
    case '3':
    case 'a':
    case 'g':
    case 'v':
      *bondOrder = tok[0];
      if ((tok = strtok(NULL, "-")) == NULL) {
        return 0;
      }
      break;
    }
  }
  at = getAtomTypeByName(tok);
  if (at == NULL) {
    return 0;
  }
  *element2 = at->protons;
  if ((tok = strtok(NULL, "-")) == NULL) {
    return 1;
  }
  return 0;
}

// returns non-zero if it correctly parses bendName and fills in
// remaining arguments
static int
parseBendName(char *bendName,
              int *element_center,
              enum hybridization *centerHybridization,
              int *element1,
              char *bondOrder1,
              int *element2,
              char *bondOrder2)
{
  // will accept:
  //  Ea-o-Ec.hyb-o-Eb
  //  Ea-o-Ec-o-Eb
  //  Ea--Ec--Eb
  //  Ea-Ec-Eb
  // and other varients with pieces elided.  Bond orders default to 1,
  // hybridization to sp3.
  char *tok1;
  char *tok2;
  char *saveptr1;
  char *saveptr2;
  struct atomType *at;
  
  if ((tok1 = strtok_r(bendName, "-", &saveptr1)) == NULL) {
    return 0;
  }
  at = getAtomTypeByName(tok1);
  if (at == NULL) {
    return 0;
  }
  *element1 = at->protons;
  if ((tok1 = strtok_r(NULL, "-", &saveptr1)) == NULL) {
    return 0;
  }
  *bondOrder1 = '1';
  if (tok1[1] == '\0') {
    switch (tok1[0]) {
    case '1':
    case '2':
    case '3':
    case 'a':
    case 'g':
      *bondOrder1 = tok1[0];
      if ((tok1 = strtok_r(NULL, "-", &saveptr1)) == NULL) {
        return 0;
      }
      break;
    }
  }
  if ((tok2 = strtok_r(tok1, ".", &saveptr2)) == NULL) {
    return 0;
  }
  at = getAtomTypeByName(tok2);
  if (at == NULL) {
    return 0;
  }
  *element_center = at->protons;
  if ((tok2 = strtok_r(NULL, ".", &saveptr2)) == NULL) {
    *centerHybridization = sp3;
  } else if (!strcmp(tok2, "sp3d")) {
    *centerHybridization = sp3d;
  } else if (!strcmp(tok2, "sp3")) {
    *centerHybridization = sp3;
  } else if (!strcmp(tok2, "sp2_g")) {
    *centerHybridization = sp2_g;
  } else if (!strcmp(tok2, "sp2")) {
    *centerHybridization = sp2;
  } else if (!strcmp(tok2, "sp")) {
    *centerHybridization = sp;
  } else {
    return 0;
  }
  if ((tok1 = strtok_r(NULL, "-", &saveptr1)) == NULL) {
    return 0;
  }
  *bondOrder2 = '1';
  if (tok1[1] == '\0') {
    switch (tok1[0]) {
    case '1':
    case '2':
    case '3':
    case 'a':
    case 'g':
      *bondOrder2 = tok1[0];
      if ((tok1 = strtok_r(NULL, "-", &saveptr1)) == NULL) {
        return 0;
      }
      break;
    }
  }
  at = getAtomTypeByName(tok1);
  if (at == NULL) {
    return 0;
  }
  *element2 = at->protons;
  if ((tok1 = strtok_r(NULL, "-", &saveptr1)) == NULL) {
    return 1;
  }
  return 0;
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
  sprintf(bondName, "%s-%c-%s", getAtomTypeByIndex(element1)->symbol,
          bondOrder, getAtomTypeByIndex(element2)->symbol);
}

static void
generateBendName(char *bendName,
                 int element_center,
                 enum hybridization centerHybridization,
                 int element1,
                 char bondOrder1,
                 int element2,
                 char bondOrder2)
{
  int elt;
  char bnd;
  if (element1 > element2 || (element1 == element2 && bondOrder1 > bondOrder2)) {
    elt = element1;
    element1 = element2;
    element2 = elt;
    bnd = bondOrder1;
    bondOrder1 = bondOrder2;
    bondOrder2 = bnd;
  }
  sprintf(bendName, "%s-%c-%s.%s-%c-%s", getAtomTypeByIndex(element1)->symbol,
          bondOrder1, getAtomTypeByIndex(element_center)->symbol,
          hybridizationString(centerHybridization),
          bondOrder2, getAtomTypeByIndex(element2)->symbol);
}

// returns a static string which needs to be copied for storage
static char *
canonicalizeBondName(char *bondName)
{
  int element1;
  int element2;
  char bondOrder;
  static char newName[256]; // XXX Can overflow for long atom type names
  char *bn = copy_string(bondName);
  
  if (parseBondName(bn, &element1, &element2, &bondOrder)) {
    generateBondName(newName, element1, element2, bondOrder);
    free(bn);
    return newName;
  }
  free(bn);
  fprintf(stderr, "malformed bond name: %s\n", bondName);
  // we need a name, so we use the bad one -- this entry will
  // probably never be found.
  return bondName;
}

static char *
canonicalizeBendName(char *bendName)
{
  int element_center;
  enum hybridization centerHybridization;
  int element1;
  char bondOrder1;
  int element2;
  char bondOrder2;
  static char newName[256]; // XXX Can overflow for long atom type names

  if (parseBendName(bendName, &element_center, &centerHybridization,
                    &element1, &bondOrder1,
                    &element2, &bondOrder2))
  {
    generateBendName(newName, element_center, centerHybridization,
                     element1, bondOrder1,
                     element2, bondOrder2);
    return newName;
  }
  return NULL;
}

// ks in N/m
// r0 in pm, or 1e-12 m
// de in aJ, or 1e-18 J
// beta in 1e12 m^-1
struct bondStretch *
newBondStretch(char *bondName, double ks, double r0, double de, double beta, double inflectionR, int quality, int quadratic)
{
  struct bondStretch *stretch;

  stretch = allocate(sizeof(struct bondStretch));
  stretch->bondName = copy_string(bondName);
  stretch->ks = ks;
  stretch->r0 = r0;
  stretch->de = de;
  stretch->beta = beta;
  stretch->inflectionR = inflectionR;
  stretch->parameterQuality = quality;
  stretch->quadratic = quadratic;
  stretch->warned = 0;
  stretch->maxPhysicalTableIndex = -1; // flag to indicate interpolator not initialized
  return stretch;
}

// kb in yJ / rad^2 (yoctoJoules per radian squared, or 1e-24 J/rad^2)
// theta0 in radians
struct bendData *
newBendData(char *bendName, double kb, double theta0, int quality)
{
  struct bendData *bend;

  // typical kb values around 1e6 yJ/rad^2
  bend = allocate(sizeof(struct bendData));
  bend->bendName = copy_string(bendName);
  bend->kb = kb;
  bend->theta0 = theta0;
  bend->cosTheta0 = cos(theta0);
  bend->parameterQuality = quality;
  bend->warned = 0;
  return bend;
}

static struct hashtable *bondStretchHashtable = NULL;
static struct hashtable *bendDataHashtable = NULL;
static struct hashtable *deHashtable = NULL;
static struct hashtable *vanDerWaalsHashtable = NULL;
static struct hashtable *electrostaticHashtable = NULL;

// ks in N/m
// r0 in pm, or 1e-12 m
// de in aJ, or 1e-18 J
// beta in 1e12 m^-1
static struct bondStretch *
addBondStretch(char *bondName, double ks, double r0, double de, double beta, double inflectionR, int quality, int quadratic)
{
  struct bondStretch *stretch;
  struct bondStretch *old;

  stretch = newBondStretch(bondName, ks, r0, de, beta, inflectionR, quality, quadratic);
  old = hashtable_put(bondStretchHashtable, bondName, stretch);
  if (old != NULL) {
    fprintf(stderr, "duplicate bondStretch: %s\n", bondName);
    free(old->bondName);
    free(old);
  }
  return stretch;
}

// kb in yoctoJoules / radian^2 (1e-24 J/rad^2)
static struct bendData *
addBendData(char *bendName, double kb, double theta0, int quality)
{
  struct bendData *bend;
  struct bendData *old;

  bend = newBendData(bendName, kb, theta0, quality);
  old = hashtable_put(bendDataHashtable, bendName, bend);
  if (old != NULL) {
    fprintf(stderr, "duplicate bend data: %s\n", bendName);
    free(old->bendName);
    free(old);
  }
  return bend;
}

// ks in N/m
// r0 in pm, or 1e-12 m
// de in aJ, or 1e-18 J
// beta in 1e10 m^-1
static void
addInitialBondStretch(double ks,
                      double r0,
                      double de,
                      double beta,
                      double inflectionR,
                      int quality,
                      int quadratic,
                      char *bondName)
{
  struct bondStretch *stretch;
  struct bondStretch *old;
  char *canonicalName;
  
  canonicalName = canonicalizeBondName(bondName);
  if (beta < 0) {
    beta = sqrt(ks / (2.0 * de)) / 10.0 ;
  }
  if (inflectionR < 0) {
    inflectionR = r0 * 1.5;
  }
  stretch = newBondStretch(canonicalName, ks, r0, de, beta*1e-2, inflectionR, quality, quadratic);
  old = hashtable_put(bondStretchHashtable, canonicalName, stretch);
  if (old != NULL) {
    free(old->bondName);
    free(old);
  }
}

// kb in aJ / rad^2 (1e-18 J/rad^2)
// theta0 in radians
static void
addInitialBendData(double kb, double theta0, int quality, char *bendName)
{
  struct bendData *bend;
  struct bendData *old;
  char *bn;
  char *canonicalName;
  
  bn = copy_string(bendName);
  canonicalName = canonicalizeBendName(bn);
  if (canonicalName == NULL) {
    fprintf(stderr, "malformed bend name: %s\n", bendName);
    // we need a name, so we use the bad one -- this entry will
    // probably never be found.
    canonicalName = bendName;
  }

  // typical kb values around 1 aJ/rad^2
  bend = newBendData(canonicalName, kb*1e6, theta0, quality);
  old = hashtable_put(bendDataHashtable, canonicalName, bend);
  if (old != NULL) {
    fprintf(stderr, "duplicate bend entry: %s\n", bendName);
    free(old->bendName);
    free(old);
  }
}

static void
addDeTableEntry(char *bondName, double de)
{
  struct deTableEntry *entry;
  struct deTableEntry *old;
  
  entry = (struct deTableEntry *)allocate(sizeof(struct deTableEntry));
  entry->de = de;
  old = hashtable_put(deHashtable, bondName, entry);
  if (old != NULL) {
    fprintf(stderr, "duplicate de entry: %s\n", bondName);
    free(old);
  }
}

static struct vanDerWaalsParameters *
addVanDerWaalsInteraction(char *bondName, double rvdW, double evdW,
                          double cutoffRadiusStart, double cutoffRadiusEnd)
{
  struct vanDerWaalsParameters *vdw;
  struct vanDerWaalsParameters *old;
  char *canonicalName;
  
  canonicalName = canonicalizeBondName(bondName);
  vdw = (struct vanDerWaalsParameters *)allocate(sizeof(struct vanDerWaalsParameters));
  vdw->vdwName = copy_string(canonicalName);
  vdw->rvdW = rvdW;
  vdw->evdW = evdW;

  if (cutoffRadiusStart < 0.0) {
    vdw->cutoffRadiusStart = rvdW;
  } else {
    vdw->cutoffRadiusStart = cutoffRadiusStart;
  }

  if (cutoffRadiusEnd < 0.0) {
    vdw->cutoffRadiusEnd = VanDerWaalsCutoffFactor * rvdW;
  } else {
    vdw->cutoffRadiusEnd = cutoffRadiusEnd;
  }
  
  initializeVanDerWaalsInterpolator(vdw);
  old = hashtable_put(vanDerWaalsHashtable, bondName, vdw);
  if (old != NULL) {
    fprintf(stderr, "duplicate vdw: %s\n", bondName);
    free(old->vdwName);
    free(old);
  }
  return vdw;
}

static struct vanDerWaalsParameters *
generateVanDerWaals(char *bondName, int element1, int element2)
{
  struct atomType *type1;
  struct atomType *type2;
  double rvdW;
  double evdW;
  
  // getAtomTypeByIndex().vanDerWaalsRadius is in 1e-10 m
  // maximum rvdw is 2.25e-10 m for Si, so highest cutoff radius is 675 pm
  // minimum rvdw is 0.97e-10 m for Li, so lowest cutoff radius is 291 pm
  // Carbon is 1.94e-10 m, cutoff at 582 pm
  // Hydrogen is 1.5e-10 m, cutoff for H~C interaction at 516 pm
  // so rvdW is in 1e-12 m or pm
  type1 = getAtomTypeByIndex(element1);
  type2 = getAtomTypeByIndex(element2);
  if (type1->vanDerWaalsRadius == 0.0 || type2->vanDerWaalsRadius == 0.0) {
    return NULL;
  }
  rvdW = 100.0 * (type1->vanDerWaalsRadius + type2->vanDerWaalsRadius);
  // evdW in 1e-21 J or zJ
  evdW = (type1->e_vanDerWaals + type2->e_vanDerWaals) / 2.0;

  return addVanDerWaalsInteraction(bondName, rvdW, evdW, -1.0, -1.0);
}

static struct electrostaticParameters *
addElectrostaticInteraction(char *electrostaticName, double q1, double q2,
                          double cutoffRadiusStart, double cutoffRadiusEnd)
{
  struct electrostaticParameters *es;
  struct electrostaticParameters *old;
  
  es = (struct electrostaticParameters *)allocate(sizeof(struct electrostaticParameters));
  es->electrostaticName = copy_string(electrostaticName);
  es->k = COULOMB * q1 * q2 / DielectricConstant;

  if (cutoffRadiusEnd < 0.0) {
    es->cutoffRadiusEnd = es->k / MinElectrostaticSensitivity;
  } else {
    es->cutoffRadiusEnd = cutoffRadiusEnd;
  }

  if (cutoffRadiusStart < 0.0) {
    es->cutoffRadiusStart = 0.9 * es->cutoffRadiusEnd;
  } else {
    es->cutoffRadiusStart = cutoffRadiusStart;
  }
  
  initializeElectrostaticInterpolator(es);
  old = hashtable_put(electrostaticHashtable, electrostaticName, es);
  if (old != NULL) {
    fprintf(stderr, "duplicate electrostatic: %s\n", electrostaticName);
    free(old->electrostaticName);
    free(old);
  }
  return es;
}

static struct electrostaticParameters *
generateElectrostatic(char *electrostaticName, int element1, int element2)
{
  double q1;
  double q2;

  q1 = getAtomTypeByIndex(element1)->charge;
  q2 = getAtomTypeByIndex(element2)->charge;
  
  return addElectrostaticInteraction(electrostaticName, q1, q2, -1.0, -1.0);
}

static void
setElement(int protons,
           int group,
           int period,
           char *parentSymbol,
           char *symbol,
           char *name,
           double mass,
           double vanDerWaalsRadius,
           double e_vanDerWaals,
           int n_bonds,
           double covalentRadius,
           double charge,
           int isVirtual)
{
  struct atomType *entry;
  struct atomType *oldEntry;
  char buf[256];
  
  if (e_vanDerWaals < 0.0) {
    e_vanDerWaals = 0.3 + protons * protons / 190.0;
  }
  entry = (struct atomType *)allocate(sizeof(struct atomType));
  
  entry->protons = protons;
  entry->group = group;
  entry->period = period;
  entry->name = copy_string(name);
  entry->symbol = copy_string(symbol);
  entry->mass = mass;
  entry->vanDerWaalsRadius = vanDerWaalsRadius;
  entry->e_vanDerWaals = e_vanDerWaals;
  entry->n_bonds = n_bonds;
  entry->covalentRadius = covalentRadius;
  entry->charge = charge;
  entry->refCount = 2;
  entry->isVirtual = isVirtual;
  entry->parent = getAtomTypeByName(parentSymbol);

  oldEntry = hashtable_put(periodicHashtable, symbol, entry);
  if (oldEntry != NULL) {
    oldEntry->refCount--;
    if (oldEntry->refCount < 1) {
      free(oldEntry->name);
      free(oldEntry->symbol);
      free(oldEntry);
    }
  }
  sprintf(buf, "%d", protons);
  oldEntry = hashtable_put(periodicHashtable, buf, entry);
  if (oldEntry != NULL) {
    oldEntry->refCount--;
    if (oldEntry->refCount < 1) {
      free(oldEntry->name);
      free(oldEntry->symbol);
      free(oldEntry);
    }
  }
}

static int
tokenizeInt(int *errp)
{
  char *token = strtok(NULL, " \n");
  if (token != NULL) {
    return atoi(token);
  }
  *errp = 1;
  return 0;
}

static double
tokenizeDouble(int *errp)
{
  char *token = strtok(NULL, " \n");
  double value;
  if (token != NULL) {
    return atof(token);
  }
  *errp = 1;
  return 0.0;
}

static void
destroyElement(void *e)
{
  struct atomType *element = (struct atomType *)e;

  if (element == NULL || element->refCount-- > 1) {
    return;
  }

  free(element->name);
  element->name = NULL;
  free(element->symbol);
  element->symbol = NULL;
  free(element);
}

static void
destroyBondStretch(void *s)
{
  struct bondStretch *stretch = (struct bondStretch *)s;
  if (stretch != NULL) {
    if (stretch->bondName != NULL) {
      free(stretch->bondName);
      stretch->bondName = NULL;
    }
  }
  free(stretch);
}

static void
destroyBendData(void *b)
{
  struct bendData *bend = (struct bendData *)b;
  if (bend != NULL) {
    if (bend->bendName != NULL) {
      free(bend->bendName);
      bend->bendName = NULL;
    }
  }
  free(bend);
}

static void
destroyDeEntry(void *de)
{
  if (de != NULL) {
    free(de);
  }
}

static void
destroyVanDerWaals(void *v)
{
  struct vanDerWaalsParameters *vdw = (struct vanDerWaalsParameters *)v;
  if (vdw != NULL) {
    if (vdw->vdwName != NULL) {
      free(vdw->vdwName);
      vdw->vdwName = NULL;
    }
  }
  free(vdw);
}

static void
destroyElectrostatic(void *e)
{
  struct electrostaticParameters *es = (struct electrostaticParameters *)e;
  if (es != NULL) {
    if (es->electrostaticName != NULL) {
      free(es->electrostaticName);
      es->electrostaticName = NULL;
    }
  }
  free(es);
}

static void
destroyStaticBondTable(void)
{
  hashtable_destroy(periodicHashtable, destroyElement);
  periodicHashtable = NULL;
  hashtable_destroy(bondStretchHashtable, destroyBondStretch);
  bondStretchHashtable = NULL;
  hashtable_destroy(bendDataHashtable, destroyBendData);
  bendDataHashtable = NULL;
  hashtable_destroy(deHashtable, destroyDeEntry);
  deHashtable = NULL;
  hashtable_destroy(vanDerWaalsHashtable, destroyVanDerWaals);
  vanDerWaalsHashtable = NULL;
  hashtable_destroy(electrostaticHashtable, destroyElectrostatic);
  electrostaticHashtable = NULL;
  hashtable_destroy(patternParameterHashtable, free);
  patternParameterHashtable = NULL;
}

static void
addPatternParameter(char *name, double value, double angleUnits, char *stringValue)
{
  struct patternParameter *param =
    (struct patternParameter *)allocate(sizeof(struct patternParameter));
  param->value = value;
  param->angleUnits = angleUnits;
  param->stringValue = stringValue ? copy_string(stringValue) : NULL ;
  param = (struct patternParameter *)hashtable_put(patternParameterHashtable,
                                                   name, (void *)param);
  if (param) {
    free(param->stringValue);
    free(param);
  }
}

struct patternParameter *
getPatternParameter(char *name)
{
  struct patternParameter *param =
    (struct patternParameter *)hashtable_get(patternParameterHashtable, name);
  if (param != NULL) {
    return param;
  }
  fprintf(stderr, "getPatternParameter(%s): parameter not defined in sim-params.txt\n", name);
  ERROR("pattern parameter not defined in sim-params.txt");
  RAISER("pattern parameter not defined in sim-params.txt", NULL);
}

int numStruts = 0;

static void
addStrutDefinition(char *name, double ks, double r0, double x1, double y1, double x2, double y2)
{
  char buf[256];
  
  if (!strncmp(name, "PAM5-", 5)) {
    name += 5;
  }
  numStruts++;
  sprintf(buf, "strut-%d", numStruts);
  addPatternParameter(buf, 0.0, 0.0, name);

  sprintf(buf, "PAM5-Stack:vDa%s-x", name);
  addPatternParameter(buf, x1, 1.0, NULL);
  sprintf(buf, "PAM5-Stack:vDa%s-y", name);
  addPatternParameter(buf, y1, 1.0, NULL);
  sprintf(buf, "PAM5-Stack:vDb%s-x", name);
  addPatternParameter(buf, x2, 1.0, NULL);
  sprintf(buf, "PAM5-Stack:vDb%s-y", name);
  addPatternParameter(buf, y2, 1.0, NULL);

  sprintf(buf, "vDa%s-1-vDb%s", name, name);
  addInitialBondStretch(ks, r0, 1.0, -1.0, -1.0, 9, 6, buf);
}

static int
readBondTableOverlay(char *filename)
{
  char buf[4096];
  char *token;
  int lineNumber = 0;
  int err;
  int protons;
  int group;
  int period;
  char *parentSymbol;
  char *symbol;
  char *name;
  double mass;
  double rvdW;
  double evdW;
  int nBonds;
  double rCovalent;
  double charge;
  int isVirtual;
  double ks;
  double r0;
  double de;
  double beta;
  double inflectionR;
  double x1;
  double y1;
  double x2;
  double y2;
  int quality;
  int quadratic;
  double ktheta;
  double theta0;
  double cutoffRadiusStart;
  double cutoffRadiusEnd;
  double value;
  double angleUnits = 1.0; // default to radians
  FILE *f = fopen(filename, "r");
  
  if (f == NULL) {
    // silent about not finding file
    return 0;
  }
  write_traceline("# reading parameter file: %s\n", filename);
  while (fgets(buf, 4096, f)) {
    lineNumber++;
    token = strtok(buf, " \n");
    if (token) {
      if (!strncmp(token, "#", 1) ) {
        continue;
      } else if (!strcmp(token, "units")) {
        err = 0;
        name = strtok(NULL, " \n");
        if (!strcmp(name, "degrees")) {
          angleUnits = Pi / 180.0;
        } else if (!strcmp(name, "radians")) {
          angleUnits = 1.0;
        } else {
          fprintf(stderr, "unknown unit at file %s line %d\n", filename, lineNumber);
        }
        if (err || name == NULL) {
          fprintf(stderr, "format error at file %s line %d\n", filename, lineNumber);
        }
      } else if (!strcmp(token, "element")) {
        err = 0;
        protons = tokenizeInt(&err);
        group = tokenizeInt(&err);
        period = tokenizeInt(&err);
        parentSymbol = strtok(NULL, " \n");
        symbol = strtok(NULL, " \n");
        name = strtok(NULL, " \n");
        mass = tokenizeDouble(&err);
        rvdW = tokenizeDouble(&err);
        evdW = tokenizeDouble(&err);
        nBonds = tokenizeInt(&err);
        rCovalent = tokenizeDouble(&err);
        charge = tokenizeDouble(&err);
        isVirtual = tokenizeInt(&err);
        if (err || symbol == NULL || name == NULL) {
          fprintf(stderr, "format error at file %s line %d\n", filename, lineNumber);
        } else {
          setElement(protons, group, period, parentSymbol, symbol, name, mass, rvdW, evdW, nBonds, rCovalent, charge, isVirtual);
          DPRINT13(D_READER, "setElement: %d %d %d %s %s %s %f %f %f %d %f %f %d\n", protons, group, period, parentSymbol, symbol, name, mass, rvdW, evdW, nBonds, rCovalent, charge, isVirtual);
        }
      } else if (!strcmp(token, "stretch")) {
        err = 0;
        ks = tokenizeDouble(&err);
        r0 = tokenizeDouble(&err);
        de = tokenizeDouble(&err);
        beta = tokenizeDouble(&err);
        inflectionR = tokenizeDouble(&err);
        quality = tokenizeInt(&err);
        quadratic = tokenizeInt(&err);
        name = strtok(NULL, " \n");
        if (err || name == NULL) {
          fprintf(stderr, "format error at file %s line %d\n", filename, lineNumber);
        } else {
          addInitialBondStretch(ks, r0, de, beta, inflectionR, quality, quadratic, name);
          DPRINT8(D_READER, "addBondStretch: %f %f %f %f %f %d %d %s\n", ks, r0, de, beta, inflectionR, quality, quadratic, name);

        }
      } else if (!strcmp(token, "bend")) {
        err = 0;
        ktheta = tokenizeDouble(&err);
        theta0 = tokenizeDouble(&err) * angleUnits;
        quality = tokenizeInt(&err);
        name = strtok(NULL, " \n");
        if (err || name == NULL) {
          fprintf(stderr, "format error at file %s line %d\n", filename, lineNumber);
        } else {
          addInitialBendData(ktheta, theta0, quality, name);
          DPRINT4(D_READER, "addBendData: %f %f %d %s\n", ktheta, theta0, quality, name);
        }
      } else if (!strcmp(token, "vdw")) {
        err = 0;
        rvdW = tokenizeDouble(&err);
        evdW = tokenizeDouble(&err);
        cutoffRadiusStart = tokenizeDouble(&err);
        cutoffRadiusEnd = tokenizeDouble(&err);
        name = strtok(NULL, " \n");
        if (err || name == NULL) {
          fprintf(stderr, "format error at file %s line %d\n", filename, lineNumber);
        } else {
          addVanDerWaalsInteraction(name, rvdW, evdW, cutoffRadiusStart, cutoffRadiusEnd);
          DPRINT5(D_READER, "addVanDerWaalsInteraction: %f %f %f %f %s\n", rvdW, evdW, cutoffRadiusStart, cutoffRadiusEnd, name);
        }
      } else if (!strcmp(token, "pattern")) {
        err = 0;
        name = strtok(NULL, " \n");
        value = tokenizeDouble(&err);
        if (err || name == NULL) {
          fprintf(stderr, "format error at file %s line %d\n", filename, lineNumber);
        } else {
          addPatternParameter(name, value, angleUnits, NULL);
          DPRINT2(D_READER, "addPatternParameter: %s %f\n", name, value);
        }
      } else if (!strcmp(token, "strut")) {
        err = 0;
        name = strtok(NULL, " \n");
        ks = tokenizeDouble(&err);
        r0 = tokenizeDouble(&err);
        x1 = tokenizeDouble(&err);
        y1 = tokenizeDouble(&err);
        x2 = tokenizeDouble(&err);
        y2 = tokenizeDouble(&err);
        if (err || name == NULL) {
          fprintf(stderr, "format error at file %s line %d\n", filename, lineNumber);
        } else {
          addStrutDefinition(name, ks, r0, x1, y1, x2, y2);
          DPRINT7(D_READER, "addStrutDefinition: %s %f %f %f %f %f %f\n", name, ks, r0, x1, y1, x2, y2);
        }
        //} else {
        //fprintf(stderr, "unrecognized line type at file %s line %d: %s\n", filename, lineNumber, token);
      }
    }
  }
  fclose(f);
  return 1;
}

static void
initializeStaticBondTable(void)
{
  destroyStaticBondTable();
  
  periodicHashtable = hashtable_new(64);
  bondStretchHashtable = hashtable_new(40);
  deHashtable = hashtable_new(10);
  bendDataHashtable = hashtable_new(40);
  vanDerWaalsHashtable = hashtable_new(40);
  electrostaticHashtable = hashtable_new(40);
  patternParameterHashtable = hashtable_new(40);
  
  // groups 9-22 are lanthanides
  // groups 8-31 are transition metals
  //
  // mass in yg (yoctograms, or 1e-24 g)
  // rvdW is in 1e-10 m or angstroms or 0.1 nm
  // evdW in zJ (zepto Joules, or milli atto Joules, or 1e-21 J)
  //   an e_vanDerWaals value < 0 will be calculated in setElement()
  // rCovalent in pm (picoMeters, or 1e-12 m)
  // chrg in multiples of proton charge
  // NOTE: change MAX_VDW_RADIUS in part.[ch] if adding an atom larger than Si
  //
  // protons, group, period, symbol, name, mass, vanDerWaalsRadius,
  //    e_vanDerWaals, n_bonds, covalentRadius, charge, isVirtual
  //
  //          Z grp per par    sym   name           mass    rvdW  evdW bnds rcov chrg virt
  //

  setElement(999, 0, 0, NULL, "All", "AllAtomTypes", 0.0,  0.0,   0.0,   0,   0, 0, 0);
  setElement(998, 0, 0, "All","Elt", "Elements",     0.0,  0.0,   0.0,   0,   0, 0, 0);
 
  setElement( 0,  1, 1, "Elt", "X",  "Singlet",    17.000,  1.1,  -1.00, 1,   0, 0, 0);
  setElement( 1,  1, 1, "Elt", "H",  "Hydrogen",    1.6737, 1.5 , 0.382, 1,  30, 0, 0);
  setElement( 2,  0, 1, "Elt", "He", "Helium",      6.646,  1.4,  -1.00, 0,   0, 0, 0);
 
  setElement( 3,  1, 2, "Elt", "Li", "Lithium",    11.525,  0.97, -1.00, 1, 152, 0, 0);
  setElement( 4,  2, 2, "Elt", "Be", "Beryllium",  14.964,  1.10, -1.00, 2, 114, 0, 0);
  setElement( 5,  3, 2, "Elt", "B",  "Boron",      17.949,  1.99, -1.00, 3,  83, 0, 0);
  setElement( 6,  4, 2, "Elt", "C",  "Carbon",     19.925,  1.94, 0.357, 4,  77, 0, 0);
  setElement( 7,  5, 2, "Elt", "N",  "Nitrogen",   23.257,  1.82, 0.447, 3,  70, 0, 0);
  setElement( 8,  6, 2, "Elt", "O",  "Oxygen",     26.565,  1.74, 0.406, 2,  66, 0, 0);
  setElement( 9,  7, 2, "Elt", "F",  "Fluorine",   31.545,  1.65, 0.634, 1,  64, 0, 0);
  setElement(10,  0, 2, "Elt", "Ne", "Neon",       33.49,   1.82, -1.00, 0,   0, 0, 0);
 
  setElement(11,  1, 3, "Elt", "Na", "Sodium",     38.1726, 1.29, -1.00, 1, 186, 0, 0);
  setElement(12,  2, 3, "Elt", "Mg", "Magnesium",  40.356,  1.15, -1.00, 2, 160, 0, 0);
  setElement(13,  3, 3, "Elt", "Al", "Aluminum",   44.7997, 2.0,  -1.00, 3, 125, 0, 0);
  setElement(14,  4, 3, "Elt", "Si", "Silicon",    46.6245, 2.25, 1.137, 4, 116, 0, 0);
  setElement(15,  5, 3, "Elt", "P",  "Phosphorus", 51.429,  2.18, 1.365, 3, 110, 0, 0);
  setElement(16,  6, 3, "Elt", "S",  "Sulfur",     53.233,  2.10, 1.641, 2, 104, 0, 0);
  setElement(17,  7, 3, "Elt", "Cl", "Chlorine",   58.867,  2.03, 1.950, 1,  99, 0, 0);
  setElement(18,  0, 3, "Elt", "Ar", "Argon",      62.33,   1.88, -1.00, 0,   0, 0, 0);

  setElement(19,  1, 4, "Elt", "K",  "Potassium",  64.9256, 1.59, -1.00, 1, 231, 0, 0);
  setElement(20,  2, 4, "Elt", "Ca", "Calcium",    66.5495, 1.27, -1.00, 2, 197, 0, 0);
  setElement(21,  8, 4, "Elt", "Sc", "Scandium",   74.646,  2.0,  -1.00, 0,  60, 0, 0);
  setElement(22, 23, 4, "Elt", "Ti", "Titanium",   79.534,  2.0,  -1.00, 0, 147, 0, 0);
  setElement(23, 24, 4, "Elt", "V",  "Vanadium",   84.584,  2.0,  -1.00, 0, 132, 0, 0);
  setElement(24, 25, 4, "Elt", "Cr", "Chromium",   86.335,  2.0,  -1.00, 0, 125, 0, 0);
  setElement(25, 26, 4, "Elt", "Mn", "Manganese",  91.22,   2.0,  -1.00, 0, 112, 0, 0);
  setElement(26, 27, 4, "Elt", "Fe", "Iron",       92.729,  2.0,  -1.00, 0, 124, 0, 0);
  setElement(27, 28, 4, "Elt", "Co", "Cobalt",     97.854,  2.0,  -1.00, 0, 125, 0, 0);
  setElement(28, 29, 4, "Elt", "Ni", "Nickel",     97.483,  2.3,  -1.00, 0, 125, 0, 0);
  setElement(29, 30, 4, "Elt", "Cu", "Copper",    105.513,  2.3,  -1.00, 0, 128, 0, 0);
  setElement(30, 31, 4, "Elt", "Zn", "Zinc",      108.541,  2.3,  -1.00, 0, 133, 0, 0);
  setElement(31,  3, 4, "Elt", "Ga", "Gallium",   115.764,  2.3,  -1.00, 0, 135, 0, 0);
  setElement(32,  4, 4, "Elt", "Ge", "Germanium", 120.53,   2.0,  -1.00, 4, 122, 0, 0);
  setElement(33,  5, 4, "Elt", "As", "Arsenic",   124.401,  2.0,  -1.00, 3, 120, 0, 0);
  setElement(34,  6, 4, "Elt", "Se", "Selenium",  131.106,  1.88, -1.00, 2, 119, 0, 0);
  setElement(35,  7, 4, "Elt", "Br", "Bromine",   132.674,  1.83, -1.00, 1, 119, 0, 0);
  setElement(36,  0, 4, "Elt", "Kr", "Krypton",   134.429,  1.9,  -1.00, 0,   0, 0, 0);

  setElement(51,  5, 5, "Elt", "Sb", "Antimony",  124.401,  2.2,  -1.00, 3, 144, 0, 0);
  setElement(52,  6, 5, "Elt", "Te", "Tellurium", 131.106,  2.1,  -1.00, 2, 142, 0, 0);
  setElement(53,  7, 5, "Elt", "I",  "Iodine",    132.674,  2.0,  -1.00, 1, 141, 0, 0);
  setElement(54,  0, 5, "Elt", "Xe", "Xenon",     134.429,  1.9,  -1.00, 0,   0, 0, 0);
#define MAX_REAL_ELEMENT 54

#include "bonds.gen"

  addDeTableEntry("H-1-N",  0.75);
  addDeTableEntry("N-1-O",  0.383);
  addDeTableEntry("N-1-F",  0.422);
  addDeTableEntry("F-1-S",  0.166);
  addDeTableEntry("O-1-F",  0.302);
  addDeTableEntry("C-1-I",  0.373);
  addDeTableEntry("O-1-Cl", 0.397);
  addDeTableEntry("O-1-I",  0.354);
  addDeTableEntry("S-1-Cl", 0.489);

#include "bends.gen"
}

static const char bends_rcsid[] = RCSID_BENDS_H;
static const char bonds_rcsid[] = RCSID_BONDS_H;

static char *systemBondTableOverlayFileName = NULL;
static time_t systemBondTableOverlayModificationTime = 0;

static char *userBondTableOverlayFileName = NULL;
static time_t userBondTableOverlayModificationTime = 0;

void
initializeBondTable(void)
{
  struct stat statBuf;
  char *home;
  char *rest;
  int len;
  int reloadSystemOverlay = 0;
  int reloadUserOverlay = 0;

  if (UseAMBER) {
    if (AmberNonbondedParametersFileName != NULL) {
      read_amber_itp_file(AmberNonbondedParametersFileName);
    }
    if (AmberBondedParametersFileName != NULL) {
      read_amber_itp_file(AmberBondedParametersFileName);
    }
  }
  if (bondStretchHashtable == NULL) {
    reloadSystemOverlay = 1;
    reloadUserOverlay = 1;
  }
  if (SystemParametersFileName != NULL) {
    if (systemBondTableOverlayFileName == NULL ||
        strcmp(systemBondTableOverlayFileName, SystemParametersFileName)) {
      if (systemBondTableOverlayFileName != NULL) {
        free(systemBondTableOverlayFileName);
      }
      systemBondTableOverlayFileName = copy_string(SystemParametersFileName);
      systemBondTableOverlayModificationTime = 0;
    }
    if (!stat(SystemParametersFileName, &statBuf)) {
      if (systemBondTableOverlayModificationTime < statBuf.st_mtime) {
        reloadSystemOverlay = 1;
        systemBondTableOverlayModificationTime = statBuf.st_mtime;
      }
    }      
  }
  
  if (userBondTableOverlayFileName == NULL) {
    home = getenv("HOME");
    if (home == NULL) {
      home = getenv("USERPROFILE"); // windows
    }
    if (home == NULL) {
      home = "";
    }
    rest = "/Nanorex/sim-params.txt";
    len = strlen(home) + strlen(rest) + 1;
    userBondTableOverlayFileName = (char *)allocate(len);
    strcpy(userBondTableOverlayFileName, home);
    strcat(userBondTableOverlayFileName, rest);
    UserParametersFileName = userBondTableOverlayFileName;
  }
  if (!stat(userBondTableOverlayFileName, &statBuf)) {
    if (userBondTableOverlayModificationTime < statBuf.st_mtime) {
      reloadUserOverlay = 1;
      userBondTableOverlayModificationTime = statBuf.st_mtime;
    }
  }
  if (reloadSystemOverlay || reloadUserOverlay) {
    initializeStaticBondTable();

    numStruts = 0;    
    LoadedSystemParameters =
      readBondTableOverlay(systemBondTableOverlayFileName);
    LoadedUserParameters =
      readBondTableOverlay(userBondTableOverlayFileName);
  }
}

void
destroyBondTable(void)
{
  destroyStaticBondTable();
  if (systemBondTableOverlayFileName != NULL) {
    free(systemBondTableOverlayFileName);
    systemBondTableOverlayFileName = NULL;
  }
  if (userBondTableOverlayFileName != NULL) {
    free(userBondTableOverlayFileName);
    userBondTableOverlayFileName = NULL;
    UserParametersFileName = NULL;
  }
}

static void
clearBondWarnings(char *bondName, void *entry)
{
  ((struct bondStretch *)entry)->warned = 0;
}

static void
clearBendWarnings(char *bendName, void *entry)
{
  ((struct bendData *)entry)->warned = 0;
}

void
reInitializeBondTable()
{
  if (bondStretchHashtable != NULL) {
    hashtable_iterate(bondStretchHashtable, clearBondWarnings);
  }
  if (bendDataHashtable != NULL) {
    hashtable_iterate(bendDataHashtable, clearBendWarnings);
  }
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

// This finds the r value of the inflection point in the Lippincott
// potential function.  We're looking for the spot outside of r0 where
// the second derivitive of Lippincott(r) is zero.  The second
// derivitive has two identical exponential terms in it, which will be
// positive throughout the region of interest, and never zero.  Since
// we're just looking for the zero, and the exponentials multiply
// other terms, we just set them to 1.  The resulting function must
// also have a zero at the same point.  That function can then be
// simplified to:
//
// (r^2 - r0^2)^2     4000000 de r0
// --------------  -  -------------  =  0
//       r                  ks
//
// which can be solved analytically for r, but is really messy.  It
// starts out negative at r = r0, and we just wait until it's
// positive, at which point there has to be a zero.  We could be a LOT
// more elegant about the search, if it matters!
static double findInflectionR(double r0, double ks, double de)
{
  double r = r0;
  double a;
  double b;
 
  // We stop the interpolation table at the inflection point if we're
  // minimizing, otherwise continue to 1.5 * r0.  See Lippincott in
  // interpolate.c.
  if (1 || !ToMinimize) { // disabled by: (1 ||
    // this value is actually ignored
    return 1.5 * r0;
  }
   
  b = -1;
  while (b < 0) {
    a = (r * r - r0 * r0);
    b = a * a / r - 4000000 * de * r0 / ks;
    r = r + 0.1;
  }
  return r;
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
  return addBondStretch(bondName, ks, r0, de, beta*1e-2, findInflectionR(r0, ks, de), QUALITY_INTERPOLATED, 0);
}

/* generate a (hopefully not too bogus) set of bond stretch parameters
   for a bond type that we haven't entered real data for */
static struct bondStretch *
generateGenericBondStretch(char *bondName, int element1, int element2, char bondOrder)
{
  double ks, r0, de, beta;
  int quality = QUALITY_GUESSED;

  switch (bondOrder) {
  default: // XXX Falls through to single bond case.  WRONG!!!!
    quality = QUALITY_INACCURATE;
  case '1':
    ks = 0.0;
    de = getDe(bondName);
    beta = 0.0;
    r0 = getAtomTypeByIndex(element1)->covalentRadius + getAtomTypeByIndex(element2)->covalentRadius ;
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
    quality = QUALITY_INACCURATE;
    ks = 0.0;
    de = getDe(bondName);
    beta = 0.0;
    r0 = getAtomTypeByIndex(element1)->covalentRadius + getAtomTypeByIndex(element2)->covalentRadius ;
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
    quality = QUALITY_INACCURATE;
    ks = 0.0;
    de = getDe(bondName);
    beta = 0.0;
    r0 = getAtomTypeByIndex(element1)->covalentRadius + getAtomTypeByIndex(element2)->covalentRadius ;
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
  
  return addBondStretch(bondName, ks, r0, de, beta*1e-2, findInflectionR(r0, ks, de), quality, 0);
}

/* generate a (hopefully not too bogus) set of bond stretch parameters
   for a bond type that we haven't entered real data for */
static struct bendData *
generateGenericBendData(char *bendName,
                        int element_center,
                        enum hybridization centerHybridization,
                        int element1,
                        char bondOrder1,
                        int element2,
                        char bondOrder2)
{
  double len;
  double kb, theta0;

  if (element_center < 0 || element_center > MAX_REAL_ELEMENT ||
      element1 < 0 || element1 > MAX_REAL_ELEMENT ||
      element2 < 0 || element2 > MAX_REAL_ELEMENT)
  {
    return NULL;
  }
  
  // XXX only correct for bond order 1 on both bonds  FIX!!!

  len = getAtomTypeByIndex(element_center)->covalentRadius +
    getAtomTypeByIndex(element1)->covalentRadius +
    getAtomTypeByIndex(element2)->covalentRadius;
  
  kb = 45e6 / (len * len) + len * 1.3 - 475.0;
  if (kb > 2000.0) {
    kb = 2000.0;
  }

  switch (centerHybridization) {
  case sp:
    theta0 = Pi;
    break;
  case sp2:
  case sp2_g:
    theta0 = 2.0 * Pi / 3.0;
    break;
  case sp3:
    theta0 = 1.9106;
    break;
  case sp3d:
    // XXX also need axial/equatorial info
    theta0 = Pi / 2.0;
    break;
  default:
    theta0 = 1.9106;
    break;
  }
  
  // kb in zeptoJoules / radian^2 (1e-21 J/rad^2)

  return addBendData(bendName, kb*1000.0, theta0, 1);
}

static struct bondStretch *
getBondStretchEntry(int element1, int element2, char bondOrder)
{
  struct bondStretch *entry;
  char bondName[256]; // XXX Can overflow for long atom type names
  
  generateBondName(bondName, element1, element2, bondOrder);
  entry = (struct bondStretch *)hashtable_get(bondStretchHashtable, bondName);
  if (entry == NULL) {
    entry = generateGenericBondStretch(bondName, element1, element2, bondOrder);
  }
  return entry;
}

// returns distance in pm
double
getBondEquilibriumDistance(int element1, int element2, char bondOrder)
{
  struct bondStretch *stretch;

  stretch = getBondStretchEntry(element1, element2, bondOrder);
  return stretch->r0;
}

struct bondStretch *
getBondStretch(int element1, int element2, char bondOrder)
{
  struct bondStretch *entry;
  char bondName[256]; // XXX Can overflow for long atom type names

  entry = getBondStretchEntry(element1, element2, bondOrder);
  if (entry->parameterQuality < QualityWarningLevel && !entry->warned) {
    if (!ComputedParameterWarning) {
      WARNING("Using a reduced quality parameter, see the trace output for details");
      ComputedParameterWarning = 1;
    }
    generateBondName(bondName, element1, element2, bondOrder);
    INFO2("Using quality %d parameters for %s stretch", entry->parameterQuality, bondName);
    INFO4("Computed ks: %e, r0: %e, de: %e, beta: %e",
          entry->ks,
          entry->r0,
          entry->de,
          entry->beta);
    entry->warned = 1;
  }
  if (entry->maxPhysicalTableIndex == -1) {
    // Only call initializeBondStretchInterpolater when we're actually
    // going to use it.  That way, we don't warn about too large of an
    // ExcessiveEnergyLevel
    initializeBondStretchInterpolater(entry);
  }
  return entry;
}

struct bendData *
getBendData(int element_center,
            enum hybridization centerHybridization,
            int element1,
            char bondOrder1,
            int element2,
            char bondOrder2)
{
  struct bendData *bend;
  char bendName[256]; // XXX Can overflow for long atom type names
  
  generateBendName(bendName, element_center, centerHybridization, element1, bondOrder1, element2, bondOrder2);
  bend = (struct bendData *)hashtable_get(bendDataHashtable, bendName);
  if (bend == NULL) {
    bend = generateGenericBendData(bendName, element_center, centerHybridization, element1, bondOrder1, element2, bondOrder2);
  }
  if (bend == NULL) {
    return NULL;
  }
  if (bend->parameterQuality < QualityWarningLevel && !bend->warned) {
    if (!ComputedParameterWarning) {
      WARNING("Using a reduced quality parameter, see the trace output for details");
      ComputedParameterWarning = 1;
    }
    INFO2("Using quality %d parameters for %s bend", bend->parameterQuality, bendName);
    INFO2("Computed kb: %e, theta0: %e", bend->kb, bend->theta0);
    bend->warned = 1;
  }
  return bend;
}

struct vanDerWaalsParameters *
getVanDerWaalsTable(int element1, int element2)
{
  struct vanDerWaalsParameters *vdw;
  char bondName[256]; // XXX Can overflow for long atom type names

  generateBondName(bondName, element1, element2, 'v');
  vdw = (struct vanDerWaalsParameters *)hashtable_get(vanDerWaalsHashtable, bondName);
  if (vdw == NULL) {
    vdw = generateVanDerWaals(bondName, element1, element2);
  }
  return vdw;
}

struct electrostaticParameters *
getElectrostaticParameters(int element1, int element2)
{
  struct electrostaticParameters *es;
  char electrostaticName[256]; // XXX Can overflow for long atom type names

  generateBondName(electrostaticName, element1, element2, 'e');
  es = (struct electrostaticParameters *)hashtable_get(electrostaticHashtable, electrostaticName);
  if (es == NULL) {
    es = generateElectrostatic(electrostaticName, element1, element2);
  }
  return es;
}


#if 0
static void
compare(char *bondName, char *parameter, double old, double new)
{
  if (fabs(old - new) > 0.005) {
    printf("%s %s old %f new %f dif: %f\n", bondName, parameter, old, new, old-new);
  }
}

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
