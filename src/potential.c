
#include "simulator.h"

// incremented each time either the potential or gradient is
// calculated.  Used to match values in bond->valid to determine the
// need to recalculate bond->inverseLength and bond->rUnit.
//
// This is the same as setting bond->valid to 0 for each bond,
// checking for non-zero, and setting to non-zero when calculated.  It
// doesn't require the reset loop at the start of each calculation,
// though.
//
// Probably should allow the use of the same serial number for back to
// back calls to potential and gradient using the same positions.  But
// then we'd have to save r and rSquared as well.
static int validSerial = 0;

// presumes that updateVanDerWaals() has been called already.
static void
setRUnit(struct xyz *position, struct bond *b, double *pr)
{
  struct xyz rv;
  double r;
  double rSquared;
  
  vsub2(rv, position[b->a1->index], position[b->a2->index]);
  rSquared = vdot(rv, rv);
  r = sqrt(rSquared);
  if (r < 0.001) {
    // atoms are on top of each other
    b->inverseLength = 1000;
    vsetc(b->rUnit, 1.0);
  } else {
    b->inverseLength = 1.0 / r;
    vmul2c(b->rUnit, rv, b->inverseLength); /* unit vector along r */
  }
  if (pr) {
    *pr = r;
  }
  b->valid = validSerial;
}

// note: the first two parameters are only used for error processing...
double
stretchPotential(struct part *p, struct stretch *stretch, struct bondStretch *stretchType, double r)
{
  int k;
  double potential;

  /* interpolation */
  double *t1;
  double *t2;
  double start;
  double scale;

  struct interpolationTable *iTable;

  // table lookup equivalent to: potential = potentialLippincottMorse(rSquared);
  iTable = &stretchType->potentialLippincottMorse;
  start = iTable->start;
  scale = iTable->scale;
  t1 = iTable->t1;
  t2 = iTable->t2;
  k = (int)(r - start) / scale;
  if (k < 0) {
    if (!ToMinimize && DEBUG(D_TABLE_BOUNDS) && stretch) { //linear
      fprintf(stderr, "stretch: low --");
      printStretch(stderr, p, stretch);
    }
    potential = t1[0] + r * t2[0];
  } else if (k >= TABLEN) {
    if (ToMinimize) { // extend past end of table using a polynomial
      // XXX switch the following to use Horner's method:
      potential = stretchType->potentialExtensionA
        + stretchType->potentialExtensionB * r
        + stretchType->potentialExtensionC * r * r
        + stretchType->potentialExtensionD * r * r * r;
      //potential = stretchType->potentialExtensionStiffness * r * r
      //          + stretchType->potentialExtensionIntercept;
      //potential = t1[TABLEN-1]+ ((TABLEN-1) * scale + start) * t2[TABLEN-1];
    } else {
      potential=0.0;
      if (DEBUG(D_TABLE_BOUNDS) && stretch) {
        fprintf(stderr, "stretch: high --");
        printStretch(stderr, p, stretch);
      }
    }
  } else if (DirectEvaluate) {
    potential = potentialLippincottMorse(r, stretchType);
  } else {
    potential = t1[k] + r * t2[k];
  }
  return potential;
}

double
stretchGradient(struct part *p, struct stretch *stretch, struct bondStretch *stretchType, double r)
{
  int k;
  double gradient;

  /* interpolation */
  double *t1;
  double *t2;
  double start;
  double scale;

  struct interpolationTable *iTable;

    // table lookup equivalent to: gradient = gradientLippincottMorse(r);
    iTable = &stretchType->gradientLippincottMorse;
    start = iTable->start;
    scale = iTable->scale;
    t1 = iTable->t1;
    t2 = iTable->t2;
    k = (int)(r - start) / scale;
    if (k < 0) {
      if (!ToMinimize && DEBUG(D_TABLE_BOUNDS) && stretch) { //linear
        fprintf(stderr, "stretch: low --");
        printStretch(stderr, p, stretch);
      }
      gradient = t1[0] + r * t2[0];
    } else if (k >= TABLEN) {
      if (ToMinimize) { // extend past end of table using a polynomial
        // XXX switch the following to use Horner's method:
        gradient = stretchType->potentialExtensionB
          + stretchType->potentialExtensionC * r * 2.0
          + stretchType->potentialExtensionD * r * r * 3.0;
        gradient *= DR ;
        //gradient = 2.0 * stretchType->potentialExtensionStiffness * r;
        //gradient = t1[TABLEN-1]+ ((TABLEN-1) * scale + start) * t2[TABLEN-1];
      } else {
        gradient=0.0;
        if (DEBUG(D_TABLE_BOUNDS) && stretch) {
          fprintf(stderr, "stretch: high --");
          printStretch(stderr, p, stretch);
        }
      }
    } else if (DirectEvaluate) {
      gradient = gradientLippincottMorse(r, stretchType);
    } else {
      gradient = t1[k] + r * t2[k];
    }
    return -gradient;
}

double
vanDerWaalsPotential(struct part *p, struct vanDerWaals *vdw, struct vanDerWaalsParameters *parameters, double r)
{
  double potential;
  int k;
  double *t1;
  double *t2;
  double start;
  double scale;
  struct interpolationTable *iTable;
  
  /* table setup  */
  iTable = &parameters->potentialBuckingham;
  start = iTable->start;
  scale = iTable->scale;
  t1 = iTable->t1;
  t2 = iTable->t2;

  k=(int)(r - start) / scale;
  if (k < 0) {
    if (!ToMinimize && DEBUG(D_TABLE_BOUNDS)) { //linear
      fprintf(stderr, "vdW: off table low -- r=%.2f \n",  r);
      printVanDerWaals(stderr, p, vdw);
    }
    k=0;
    potential = t1[k] + r * t2[k];
  } else if (DirectEvaluate) {
    potential = potentialBuckingham(r, parameters);
  } else if (k>=TABLEN) {
    potential = 0.0;
  } else {
    potential = t1[k] + r * t2[k];
  }
  return potential;
}

double
vanDerWaalsGradient(struct part *p, struct vanDerWaals *vdw, struct vanDerWaalsParameters *parameters, double r)
{
  double gradient;
  int k;
  double *t1;
  double *t2;
  double start;
  double scale;
  struct interpolationTable *iTable;
      
  /* table setup  */
  iTable = &parameters->gradientBuckingham;
  start = iTable->start;
  scale = iTable->scale;
  t1 = iTable->t1;
  t2 = iTable->t2;
					
  k=(int)(r - start) / scale;
  if (k < 0) {
    if (!ToMinimize && DEBUG(D_TABLE_BOUNDS)) { //linear
      fprintf(stderr, "vdW: off table low -- r=%.2f \n",  r);
      printVanDerWaals(stderr, p, vdw);
    }
    k=0;
    gradient = t1[k] + r * t2[k];
  } else if (DirectEvaluate) {
    gradient = gradientBuckingham(r, parameters);
  } else if (k>=TABLEN) {
    gradient = 0.0;
  } else {
    gradient = t1[k] + r * t2[k];
  }
  return gradient;
}

double
calculatePotential(struct part *p, struct xyz *position)
{
  int j;
  double rSquared;
  struct xyz v1;
  struct xyz v2;
  double z;
  double theta;
  double ff;
  double potential = 0.0;

  struct stretch *stretch;
  struct bond *bond;
  struct bond *bond1;
  struct bond *bond2;
  struct bend *bend;
  struct bendData *bType;
  double torque;
  struct vanDerWaals *vdw;
  struct xyz rv;
  double r;

  validSerial++;

  for (j=0; j<p->num_stretches; j++) {
    stretch = &p->stretches[j];
    bond = stretch->b;

    // we presume here that rUnit is invalid, and we need rSquared
    // anyway.
    setRUnit(position, bond, &r);
            
    potential += stretchPotential(p, stretch, stretch->stretchType, r);
  }
  if (DEBUG(D_STRETCH_ONLY)) { // -D6
    return potential;
  }
			
  /* now the potential for each bend */
			
  for (j=0; j<p->num_bends; j++) {
    bend = &p->bends[j];

    bond1 = bend->b1;
    bond2 = bend->b2;

    // Update rUnit for both bonds, if necessary.  Note that we
    // don't need r or rSquared here.
    if (bond1->valid != validSerial) {
      setRUnit(position, bond1, NULL);
    }
    if (bond2->valid != validSerial) {
      setRUnit(position, bond2, NULL);
    }
      
    // v1, v2 are the unit vectors FROM the central atom TO the
    // neighbors.  Reverse them if we have to.
    if (bend->dir1) {
      vsetn(v1, bond1->rUnit);
    } else {
      vset(v1, bond1->rUnit);
    }
    if (bend->dir2) {
      vsetn(v2, bond2->rUnit);
    } else {
      vset(v2, bond2->rUnit);
    }

    // XXX figure out how close we can get / need to get.
    // we assume we only get this close to linear on actually linear
    // bonds, for which the potential should be zero at this point.
    if (-0.99 < vdot(v1,v2)) {

#define ACOS_POLY_A -0.0820599
#define ACOS_POLY_B  0.142376
#define ACOS_POLY_C -0.137239
#define ACOS_POLY_D -0.969476

      z = vlen(vsum(v1, v2));
      // this is the equivalent of theta=arccos(z);
      theta = Pi + z * (ACOS_POLY_D +
                   z * (ACOS_POLY_C +
                   z * (ACOS_POLY_B +
                   z *  ACOS_POLY_A   )));

      // XXX check that this is all ok...
      // bType->kb in yJ/rad^2 (1e-24 J/rad^2)
      bType = bend->bendType;
      torque = (theta - bType->theta0) * bType->kb;

      ff = torque * bond1->inverseLength;
      potential += ff * ff / 2.0;
      ff = torque * bond2->inverseLength;
      potential += ff * ff / 2.0;
    }
  }

  /* do the van der Waals/London forces */
  for (j=0; j<p->num_vanDerWaals; j++) {
    vdw = p->vanDerWaals[j];

    // The vanDerWaals array changes over time, and might have
    // NULL's in it as entries are deleted.
    if (vdw == NULL) {
      continue;
    }
      
    vsub2(rv, position[vdw->a1->index], position[vdw->a2->index]);
    rSquared = vdot(rv, rv);
    r = sqrt(rSquared);
    potential += vanDerWaalsPotential(p, vdw, vdw->parameters, r);
  }
    
  return potential;
}

void
calculateGradient(struct part *p, struct xyz *position, struct xyz *force)
{
  int j;
  double rSquared;
  double gradient;
  struct xyz v1;
  struct xyz v2;
  double z;
  double theta;
  double ff;

  struct stretch *stretch;
  struct bond *bond;
  struct bond *bond1;
  struct bond *bond2;
  struct bend *bend;
  struct bendData *bType;
  double torque;
  struct vanDerWaals *vdw;
  struct xyz rv;
  struct xyz q1;
  struct xyz q2;
  struct xyz foo;
  struct xyz f;
  double r;

  validSerial++;
    
  /* clear force vectors */
  for (j=0; j<p->num_atoms; j++) {
    vsetc(force[j], 0.0);
  }

  for (j=0; j<p->num_stretches; j++) {
    stretch = &p->stretches[j];
    bond = stretch->b;

    // we presume here that rUnit is invalid, and we need r and
    // rSquared anyway.
    setRUnit(position, bond, &r);

    gradient = stretchGradient(p, stretch, stretch->stretchType, r);
    vmul2c(f, bond->rUnit, gradient);
    vadd(force[bond->a1->index], f);
    vsub(force[bond->a2->index], f);
    if (DEBUG(D_MINIMIZE_GRADIENT_MOVIE_DETAIL)) { // -D5
      writeSimpleForceVector(position, bond->a1->index, &f, 1);
      vmulc(f, -1.0);
      writeSimpleForceVector(position, bond->a2->index, &f, 1);
    }
  }
  if (DEBUG(D_STRETCH_ONLY)) { // -D6
    return;
  }
			
  /* now the forces for each bend */
			
  for (j=0; j<p->num_bends; j++) {
    bend = &p->bends[j];

    bond1 = bend->b1;
    bond2 = bend->b2;

    // Update rUnit for both bonds, if necessary.  Note that we
    // don't need r or rSquared here.
    if (bond1->valid != validSerial) {
      setRUnit(position, bond1, NULL);
    }
    if (bond2->valid != validSerial) {
      setRUnit(position, bond2, NULL);
    }
      
    // v1, v2 are the unit vectors FROM the central atom TO the
    // neighbors.  Reverse them if we have to.
    if (bend->dir1) {
      vsetn(v1, bond1->rUnit);
    } else {
      vset(v1, bond1->rUnit);
    }
    if (bend->dir2) {
      vsetn(v2, bond2->rUnit);
    } else {
      vset(v2, bond2->rUnit);
    }

    // XXX figure out how close we can get / need to get
    // apply no force if v1 and v2 are close to being linear
    if (-0.99 < vdot(v1,v2)) {

      z = vlen(vsum(v1, v2));
      // this is the equivalent of theta=arccos(z);
      theta = Pi + z * (ACOS_POLY_D +
                   z * (ACOS_POLY_C +
                   z * (ACOS_POLY_B +
                   z *  ACOS_POLY_A   )));

      v2x(foo, v1, v2);       // foo = v1 cross v2
      foo = uvec(foo);        // hmmm... not sure why this has to be a unit vector.
      q1 = uvec(vx(v1, foo)); // unit vector perpendicular to v1 in plane of v1 and v2
      q2 = uvec(vx(foo, v2)); // unit vector perpendicular to v2 in plane of v1 and v2

      bType = bend->bendType;
      torque = (theta - bType->theta0) * bType->kb;
      ff = torque * bond1->inverseLength;
      vmulc(q1, ff);
      ff = torque * bond2->inverseLength;
      vmulc(q2, ff);

      vadd(force[bend->ac->index], q1);
      vsub(force[bend->a1->index], q1);
      vadd(force[bend->ac->index], q2);
      vsub(force[bend->a2->index], q2);
    }
  }

  /* do the van der Waals/London forces */
  for (j=0; j<p->num_vanDerWaals; j++) {
    vdw = p->vanDerWaals[j];

    // The vanDerWaals array changes over time, and might have
    // NULL's in it as entries are deleted.
    if (vdw == NULL) {
      continue;
    }
      
    vsub2(rv, position[vdw->a1->index], position[vdw->a2->index]);
    rSquared = vdot(rv, rv);
    r = sqrt(rSquared);
    
    gradient = vanDerWaalsGradient(p, vdw, vdw->parameters, r);
    
    vmul2c(f, rv, gradient);
    vadd(force[vdw->a1->index], f);
    vsub(force[vdw->a2->index], f);
  }
}
