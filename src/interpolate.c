
#include "simulator.h"

// Make a table for interpolating func(x) by doing
//
//   i=(int)(x-start)/scale;
//   value=t1[i]+x*t2[i];
//
static void
fillInterpolationTable(struct interpolationTable *t, double func(double), double start, int scale)
{
    int i;
    double v1, v2, r1, r2, q;
    double v3, r5, r15, v5, v15;

    t->start = start;
    t->scale = scale;
    
    r2=start;
    v2=func(r2);
	
    for (i=0; i<TABLEN; i++) {
	r1 = r2;
	v1 = v2;
	r2 = start + (double)((i + 1) * scale);
	v2 = func(r2);
	/* shift points to minimize excursions above/below func */
	if (i < TABLEN - 1) {
          r5 = (r1 + r2) / 2.0; // halfway between r1 and r2
          v5 = func(r5);

          r15 = r2 + r2 - r5; // halfway past r2
          v15 = func(r15);

          v3 = func(r2 + r2 - r1); // one unit past r2

          v2 = v2 + 0.25 * (v5 - (func(r1) + v2) / 2.0) + 0.25 * (v15 - (v2 + v3) / 2.0);
	}
		
	q = (v2 - v1) / (r2 - r1); // slope
	t->t1[i] = v1 - q*r1;
	t->t2[i] = q;
    }
}

static double
square(double r)
{
  return r * r;
}

/** stiffnesses are in N/m, so forces come out in pN (i.e. Dx N) */
static double R0;   // in pm (1e-12 m)
static double Ks;   // in N/m
static double De;   // in aJ (1e-18 J)
static double Beta; // sqrt(Ks/2De) in 1/pm (1e12 m^-1)

static double
lippincott(double r)
{
  return De * (1 - exp(-1e-6 * Ks * R0 * (r - R0) * (r - R0) / (2 * De * r)));
}

static double
morse(double r)
{
  // the exponent is unitless
  // returns potential in aJ, given r in pm
  return De * (1 - exp(-Beta * (r - R0))) * (1 - exp(-Beta * (r - R0)));
}


// use the Morse potential inside R0, Lippincott outside
// result in aJ
static double
potentialLippincottMorse(double rSquared)
{
  double r = sqrt(rSquared);
  return (r >= R0) ? lippincott(r) : morse(r);
}

// numerically differentiate the potential for force
//
// the result is in yoctoJoules per picometer = picoNewtons
// yJ / pm = 1e-24 J / 1e-12 m = 1e-12 J / m = pN
static double
gradientLippincottMorse(double rSquared)
{
  double r = sqrt(rSquared);
  double r1 = r - 0.5;
  double r2 = r + 0.5;
  double y1 = (r1 >= R0) ? lippincott(r1) : morse(r1);
  double y2 = (r2 >= R0) ? lippincott(r2) : morse(r2);
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
  double start;
  double end;
  int scale;
  double rmin;
  double rmax;
	
  R0 = stretch->r0;
  Ks = stretch->ks;
  De = stretch->de;
  Beta = stretch->beta;

  rmin = R0 * 0.5;
  rmax = R0 * 1.5;
  start = rmin * rmin;
  end = (int)(rmax * rmax);
  scale = (end - start) / TABLEN;

  stretch->potentialExtensionStiffness = PotentialExtensionMinimumSlope / (2.0 * rmax);
  
  stretch->potentialExtensionIntercept = potentialLippincottMorse(rmax * rmax)
    - stretch->potentialExtensionStiffness * rmax * rmax;

  fillInterpolationTable(&stretch->potentialLippincottMorse, potentialLippincottMorse, start, scale);
  fillInterpolationTable(&stretch->gradientLippincottMorse, gradientLippincottMorse, start, scale);
}


static double RvdW; // in pm (1e-12 m)
static double EvdW; // in zJ (1e-21 J)

/* the Buckingham potential for van der Waals / London force */
// result in aJ
static double
potentialBuckingham(double rSquared)
{
  double r = sqrt(rSquared);
	
  // RvdW in pm (1e-12 m)
  // EvdW in zJ (1e-21 J)
  return 1e-3 * EvdW * (2.48e5 * exp(-12.5*(r/RvdW)) -1.924*pow(r/RvdW, -6.0));
}

// the result is in yoctoJoules per picometer = picoNewtons
// yJ / pm = 1e-24 J / 1e-12 m = 1e-12 J / m = pN
//
// NOTE: gradient is divided by r since we end up multiplying it by
// the radius vector to get the force.
static double
gradientBuckingham(double rSquared)
{
  double r = sqrt(rSquared);
  double y;

  // RvdW in pm (1e-12 m)
  // EvdW in zJ (1e-21 J)
  y= -1e3 * EvdW * (2.48e5 * exp(-12.5 * (r / RvdW)) * (-12.5 /RvdW)
                    - 1.924 * pow (1.0 /RvdW, -6.0) * (-6.0) * pow(r, -7.0));
  return y / r;
}

void
initializeVanDerWaalsInterpolator(struct vanDerWaalsParameters *vdw, int element1, int element2)
{
  double start;
  double scale;
  int end;

  // periodicTable[].vanDerWaalsRadius is in 1e-10 m
  // so RvdW is in 1e-12 m or pm
  RvdW = 100.0 * (periodicTable[element1].vanDerWaalsRadius +
                  periodicTable[element2].vanDerWaalsRadius);
  // EvdW in 1e-21 J or zJ
  EvdW = (periodicTable[element1].e_vanDerWaals + periodicTable[element2].e_vanDerWaals) / 2.0;

  start = square(RvdW * 0.4);
  end = (int)square(RvdW * 1.5);
  scale = (int)(end - start) / TABLEN;

  fillInterpolationTable(&vdw->potentialBuckingham, potentialBuckingham, start, scale);
  fillInterpolationTable(&vdw->gradientBuckingham, gradientBuckingham, start, scale);
}
