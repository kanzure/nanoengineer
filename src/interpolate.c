
#include "simulator.h"

/* for testing table routines */
#if 0
double t1[TABLEN], t2[TABLEN];
double start=10000.0;
int scale=30;
#endif

/* Make a table for interpolating func(x) by doing
   i=(int)(x-start)/scale;
   value=t1[i]+x*t2[i]; */

static void maktab(double *t1, double *t2, double func(double),
	    double start, int length, int scale) {
    int i;
    double v1, v2, r1, r2, q;
    double ov1, v3, r5, r15, v5, v15;
	
    r2=start;
    v2=func(r2);
	
    for (i=0; i<length; i++) {
	r1=r2;
	v1=v2;
	r2=start+(double)((i+1)*scale);
	v2=func(r2);
        DPRINT(D_TABLES, "%f %f\n", sqrt(r2), v2);
	/* shift points to minimize excursions above/below func */
	if (i<length-1) {
	    r5=(r1+r2)/2.0;
	    r15=r2+r2-r5;
	    v5=func(r5);
	    v15=func(r15);
	    v3=func(r2+r2-r1);
	    v2=v2 + 0.25*(v5-(func(r1)+v2)/2.0) + 0.25*(v15-(v2+v3)/2.0);
	}
		
	q=(v2-v1)/(r2-r1);
	t1[i] = v1 - q*r1;
	t2[i] = q;
    }
}

/* consider atoms a0 and a1 both bonded to atom ac.
   We are given the length of (a0-ac)+(a1-ac), squared, and
   desire to calculate a factor which multiplied by (a1-ac)
   gives the appropriate bending force for a0 */

/* uses globals R0 and R1, the lengths of (a0-ac) & (a1-ac), in pm,
   Kb, in N/m, and Theta0, the nominal angle, in radians */

double bender(double rSquared) {
    double theta,f;
    theta=acos((rSquared-(R0*R0+R1*R1))/(2.0*R0*R1));
	
    if (theta < Theta0)
	f= - Kb*(exp(-2.0*(theta-Theta0)) - exp(-(theta-Theta0)));
    else f=  Kb*sin(Pi * (theta - Theta0) / (Pi - Theta0))*(Pi - Theta0)/Pi;
	
	
    return R0*f / (R1 * sin(theta));
}

/** note -- uses global Ks and R0 */
// a kludge, no coherent units; result will be interpreted as pN
double hooke(double rSquared) {
	double r;
	
	r=sqrt(rSquared);
	return 2.0*Ks*(R0/r-1.0);
	//return Ks*(R0-r);
}

/* use the Morse potential inside R0, Lippincott outside */
/* numerically differentiate the resulting potential for force */
/* uses global De, Beta, Ks and R0 */

	
// ks in N/m
// r0 in pm, or 1e-12 m
// de in aJ, or 1e-18 J
// beta in 1e12 m^-1

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
// the result is in attoJoules per picometer * 1e6 = picoNewtons
//
// NOTE: gradient is divided by r since we end up multiplying it by
// the radius vector to get the force.
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

  return 1e6 * (y1 - y2) / r;
}

// Buckingham potential for van der Waals / London force
// in attoJoules (1e-18 J)
// given pm squared
static double
potentialBuckingham(double rSquared)
{
  double r = sqrt(rSquared);
	
  // EvdW in zJ (1e-21 J)
  // RvdW in pm (1e-12 m)
  return 1e-3 * EvdW * (2.48e5 * exp(-12.5 * (r / RvdW))
                       - 1.924 * pow(r / RvdW, -6.0));
}

// NOTE: gradient is divided by r since we end up multiplying it by
// the radius vector to get the force.
static double
gradientBuckingham(double rSquared)
{
  double r = sqrt(rSquared);
  double y;

  // EvdW in zJ (1e-21 J)
  // RvdW in pm (1e-12 m)
  y= -1e3 * EvdW * (2.48e5 * exp(-12.5 * (r / RvdW)) * (-12.5 /RvdW)
                    - 1.924 * pow (1.0 /RvdW, -6.0) * (-6.0) * pow(r, -7.0));
  return y / r;
}

double square(double x) {return x*x;}

/* initialize the function tables for each bending and stretching bondtype */
/* sets global De, Beta, Ks and R0 */
void
initializeBondStretchInterpolater(struct bondStretch *stretch)
{
  double end;
  double slopeAtInflection;
  
  // ks in N/m
  // r0 in pm, or 1e-12 m
  // de in aJ, or 1e-18 J
  // beta in 1e12 m^-1

  R0 = stretch->r0;
  stretch->table.start = square(R0*0.5);
  if (ToMinimize && 0) {
    end = square(stretch->inflectionR);
  } else {
    end = square(R0*1.5);
  }
  stretch->table.scale = (end - stretch->table.start) / TABLEN;
  Ks = stretch->ks;
  De = stretch->de;
  Beta = stretch->beta;
  DPRINT(D_TABLES, "table: R0: %f Ks: %f De: %f Beta: %f\n", R0, Ks, De, Beta);
  maktab(stretch->table.t1,
         stretch->table.t2,
         PrintStructureEnergy ? potentialLippincottMorse : gradientLippincottMorse,
         stretch->table.start,
         TABLEN,
         stretch->table.scale);

  slopeAtInflection = stretch->table.t2[TABLEN-1];
  //fprintf(stderr, "slope %f max %f\n", slopeAtInflection, MaxStretchSlope);
  if (MaxStretchSlope < slopeAtInflection) {
    MaxStretchSlope = slopeAtInflection;
  }
}

void
initializeVanDerWaalsInterpolator(struct interpolationTable *table, int element1, int element2)
{
  int end;

  // vanDerWaalsRadius in Angstroms, so RvdW in pm
  RvdW = 100.0 * (periodicTable[element1].vanDerWaalsRadius +
                  periodicTable[element2].vanDerWaalsRadius);
  EvdW = (periodicTable[element1].e_vanDerWaals + periodicTable[element2].e_vanDerWaals)/2.0;
				
  table->start= square(RvdW*0.4);
  end=square(RvdW*1.5);
  table->scale = (int)(end - table->start) / TABLEN;

  DPRINT(D_TABLES, "table: RvdW: %f EvdW: %f\n", RvdW, EvdW);
  maktab(table->t1,
         table->t2,
         PrintStructureEnergy ? potentialBuckingham : gradientBuckingham,
         table->start,
         TABLEN,
         table->scale);
				
}

void vdWsetup() {
    int i, j, k;
	
    Nexvanbuf = &vanderRoot;
    Nexvanbuf->fill = 0;
    Nexvanbuf->next = NULL;
	
    /* the space grid */
    for (i=0;i<SPWIDTH; i++)
	for (j=0;j<SPWIDTH; j++)
	    for (k=0;k<SPWIDTH; k++)
		Space[i][j][k] = NULL;
	
}
