
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

// the result is in attoJoules per picometer * 1e6 = picoNewtons
double lippmor(double rSquared) {
    double r,y1,y2;
	
    r=sqrt(rSquared);
    r=r+0.5;
	
    if (r>=R0)
	y2=De *(1-exp(- 1e-6 * Ks * R0 * (r - R0)* (r - R0) / (2 *De* r)));
    else
	y2=De *(1-exp(- Beta * (r - R0))) *(1-exp(- Beta * (r - R0)));
	
    r=r-1.0;
	
    if (r>=R0)
	y1=De *(1-exp(- 1e-6 * Ks * R0 * (r - R0)* (r - R0) / (2 *De* r)));
    else
	y1=De *(1-exp(- Beta * (r - R0))) *(1-exp(- Beta * (r - R0)));
	
    r=r+0.5;
	
    return 1e6*(y1-y2)/r;
}

/* the Buckingham potential for van der Waals / London force */
/* uses global EvdW, RvdW */
double bucking(double rSquared) {
    double r, y;
    r=sqrt(rSquared);
	
    y= -1e3 * EvdW*(2.48e5 * exp(-12.5*(r/RvdW)) *(-12.5/RvdW)
		    -1.924*pow(1.0/RvdW, -6.0)*(-6.0)*pow(r,-7.0));
	
    return y/r;
}

double square(double x) {return x*x;}

/* initialize the function tables for each bending and stretching bondtype */
/* sets global De, Beta, Ks and R0 */
void
initializeBondStretchInterpolater(struct bondStretch *stretch)
{
  double end;
	
  R0 = stretch->r0;
  stretch->table.start = square(R0*0.5);
  end = square(R0*1.5);
  stretch->table.scale = (end - stretch->table.start) / TABLEN;
  Ks = stretch->ks;
  De = stretch->de;
  Beta = stretch->beta;
  maktab(stretch->table.t1, stretch->table.t2, lippmor, stretch->table.start,
         TABLEN, stretch->table.scale);
}

void
initializeVanDerWaalsInterpolator(struct interpolationTable *table, int element1, int element2)
{
  int end;
  
  RvdW = 100.0 * (periodicTable[element1].vanDerWaalsRadius +
                  periodicTable[element2].vanDerWaalsRadius);
  EvdW = (periodicTable[element1].e_vanDerWaals + periodicTable[element2].e_vanDerWaals)/2.0;
				
  table->start= square(RvdW*0.4);
  end=square(RvdW*1.5);
  table->scale = (int)(end - table->start) / TABLEN;
				
  maktab(table->t1, table->t2, bucking, table->start, TABLEN, table->scale);
				
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
