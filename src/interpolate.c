
#include "simulator.h"

// Make a table for interpolating func(x) by doing
//
//   i=(int)(x-start)/scale;
//   value=t1[i]+x*t2[i];
//
static void
fillInterpolationTable(struct interpolationTable *t, double func(double, void *), double start, double scale, void *parameters)
{
    int i;
    double v1, v2, r1, r2, q;
    double v3, r5, r15, v5, v15;

    t->start = start;
    t->scale = scale;
    
    r2=start;
    v2=func(r2, parameters);
	
    for (i=0; i<TABLEN; i++) {
	r1 = r2;
	v1 = v2;
	r2 = start + (double)((i + 1) * scale);
	v2 = func(r2, parameters);
	/* shift points to minimize excursions above/below func */
	if (i < TABLEN - 1) {
          r5 = (r1 + r2) / 2.0; // halfway between r1 and r2
          v5 = func(r5, parameters);

          r15 = r2 + r2 - r5; // halfway past r2
          v15 = func(r15, parameters);

          v3 = func(r2 + r2 - r1, parameters); // one unit past r2

          v2 = v2 + 0.25 * (v5 - (func(r1, parameters) + v2) / 2.0) + 0.25 * (v15 - (v2 + v3) / 2.0);
	}
		
	q = (v2 - v1) / (r2 - r1); // slope
	t->t1[i] = v1 - q*r1;
	t->t2[i] = q;
    }
}

/** stiffnesses are in N/m, so forces come out in pN (i.e. Dx N) */

static double
lippincott(double r, struct bondStretch *s)
{
  return s->de * (1 - exp(-1e-6 * s->ks * s->r0 * (r - s->r0) * (r - s->r0) / (2 * s->de * r)));
}

static double
morse(double r, struct bondStretch *s)
{
  // the exponent is unitless
  // returns potential in aJ, given r in pm
  return s->de * (1 - exp(-s->beta * (r - s->r0))) * (1 - exp(-s->beta * (r - s->r0)));
}


// use the Morse potential inside R0, Lippincott outside
// result in aJ
double
potentialLippincottMorse(double r, void *p)
{
  struct bondStretch *stretch = (struct bondStretch *)p;
  return (r >= stretch->r0) ? lippincott(r, stretch) : morse(r, stretch);
}

// numerically differentiate the potential for force
//
// the result is in yoctoJoules per picometer = picoNewtons
// yJ / pm = 1e-24 J / 1e-12 m = 1e-12 J / m = pN
double
gradientLippincottMorse(double r, void *p)
{
  struct bondStretch *stretch = (struct bondStretch *)p;
  double r1 = r - 0.5;
  double r2 = r + 0.5;
  double y1 = (r1 >= stretch->r0) ? lippincott(r1, stretch) : morse(r1, stretch);
  double y2 = (r2 >= stretch->r0) ? lippincott(r2, stretch) : morse(r2, stretch);
  // y1, y2 are in attoJoules (1e-18 J)
  // delta r is 1 pm (1e-12 m), so:
  // y1-y2 is attoJoules / pm (1e-6 J / m)
  // 1e6*(y1-y2) is in 1e-12 J/m, or pN

  return 1e6 * (y1 - y2);
}

// Initialize the function interpolation tables for each stretch
void
initializeBondStretchInterpolater(struct bondStretch *stretch)
{
  double scale;
  double rmin;
  double rmax;

  rmin = stretch->r0 * 0.5;
  rmax = stretch->r0 * 1.5;
  scale = (rmax - rmin) / TABLEN;

  stretch->potentialExtensionStiffness = PotentialExtensionMinimumSlope / (2.0 * rmax);
  
  stretch->potentialExtensionIntercept = potentialLippincottMorse(rmax * rmax, stretch)
    - stretch->potentialExtensionStiffness * rmax * rmax;

  fillInterpolationTable(&stretch->potentialLippincottMorse, potentialLippincottMorse, rmin, scale, stretch);
  fillInterpolationTable(&stretch->gradientLippincottMorse, gradientLippincottMorse, rmin, scale, stretch);
}


/* the Buckingham potential for van der Waals / London force */
// result in aJ
double
potentialBuckingham(double r, void *p)
{
  struct vanDerWaalsParameters *vdw = (struct vanDerWaalsParameters *)p;
	
  // rvdW in pm (1e-12 m)
  // evdW in zJ (1e-21 J)
  return 1e-3 * vdw->evdW * (2.48e5 * exp(-12.5*(r/vdw->rvdW)) -1.924*pow(r/vdw->rvdW, -6.0));
}

// the result is in yoctoJoules per picometer = picoNewtons
// yJ / pm = 1e-24 J / 1e-12 m = 1e-12 J / m = pN
//
// NOTE: gradient is divided by r since we end up multiplying it by
// the radius vector to get the force.
double
gradientBuckingham(double r, void *p)
{
  struct vanDerWaalsParameters *vdw = (struct vanDerWaalsParameters *)p;
  double y;

  // rvdW in pm (1e-12 m)
  // evdW in zJ (1e-21 J)
  y= -1e3 * vdw->evdW * (2.48e5 * exp(-12.5 * (r / vdw->rvdW)) * (-12.5 /vdw->rvdW)
                         - 1.924 * pow (1.0 /vdw->rvdW, -6.0) * (-6.0) * pow(r, -7.0));
  return y / r;
}

void
initializeVanDerWaalsInterpolator(struct vanDerWaalsParameters *vdw, int element1, int element2)
{
  double start;
  double scale;
  double end;

  // periodicTable[].vanDerWaalsRadius is in 1e-10 m
  // so rvdW is in 1e-12 m or pm
  vdw->rvdW = 100.0 * (periodicTable[element1].vanDerWaalsRadius +
                  periodicTable[element2].vanDerWaalsRadius);
  // evdW in 1e-21 J or zJ
  vdw->evdW = (periodicTable[element1].e_vanDerWaals + periodicTable[element2].e_vanDerWaals) / 2.0;

  start = vdw->rvdW * 0.4;
  end = vdw->rvdW * 1.5;
  scale = (end - start) / TABLEN;

  fillInterpolationTable(&vdw->potentialBuckingham, potentialBuckingham, start, scale, vdw);
  fillInterpolationTable(&vdw->gradientBuckingham, gradientBuckingham, start, scale, vdw);
}

static void
convertDashToSpace(char *s)
{
  while (*s) {
    if (*s == '-') {
      *s = ' ';
    }
    s++;
  }
}

static void
printBondPAndG(char *bondName, double initial, double increment, double limit)
{
  char elt1[4];
  char elt2[4];
  char order;
  struct atomType *e1;
  struct atomType *e2;
  struct bondStretch *stretch;
  double r;
  double interpolated_potential;
  double interpolated_gradient;
  double direct_potential;
  double direct_gradient;

  convertDashToSpace(bondName);
  if (3 != sscanf(bondName, "%2s %c %2s", elt1, &order, elt2)) {
    fprintf(stderr, "bond format must be: bond:C-1-H\n");
    exit(1);
  }
  e1 = getAtomTypeByName(elt1);
  if (e1 == NULL) {
    fprintf(stderr, "Element %s not defined\n", elt1);
    exit(1);
  }
  e2 = getAtomTypeByName(elt2);
  if (e2 == NULL) {
    fprintf(stderr, "Element %s not defined\n", elt2);
    exit(1);
  }
  
  // XXX this may return completly bizarre result for unknown bond orders.
  stretch = getBondStretch(e1->protons, e2->protons, order);

  printf("# ks=%e r0=%e de=%e beta=%e inflectionR=%e\n",
         stretch->ks,
         stretch->r0,
         stretch->de,
         stretch->beta,
         stretch->inflectionR);

  printf("# table start = %e table end = %e\n",
         stretch->r0 * 0.5,
         stretch->r0 * 1.5);

  for (r=initial; r<limit; r+=increment) {
    interpolated_potential = stretchPotential(NULL, NULL, stretch, r);
    interpolated_gradient = stretchGradient(NULL, NULL, stretch, r);
    direct_potential = potentialLippincottMorse(r, stretch);
    direct_gradient = gradientLippincottMorse(r, stretch);
    printf("%e %e %e %e %e\n", r, interpolated_potential, interpolated_gradient, direct_potential, direct_gradient);
  }
}

static void
printBendPAndG(char *bendName, double initial, double increment, double limit)
{
  fprintf(stderr, "printBendPAndG not implemented yet\n");
  exit(1);
}

static void
printVdWPAndG(char *vdwName, double initial, double increment, double limit)
{
  fprintf(stderr, "printVdWPAndG not implemented yet\n");
  exit(1);
}

void
printPotentialAndGradientFunctions(char *name, double initial, double increment, double limit)
{

  if (!strncmp(name, "bond:", 5)) {
    printBondPAndG(name+5, initial, increment, limit);
  } else if (!strncmp(name, "bend:", 5)) {
    printBendPAndG(name+5, initial, increment, limit);
  } else if (!strncmp(name, "vdw:", 4)) {
    printVdWPAndG(name+4, initial, increment, limit);
  } else {
    fprintf(stderr, "You must specify the type of entry you want printed.\n");
    fprintf(stderr, "For example:\n");
    fprintf(stderr, " bond:C-1-H\n");
    fprintf(stderr, " bend:C-1-C-1-H\n");
    fprintf(stderr, " vdw:C-v-H\n");
    exit(1);
  }
}
