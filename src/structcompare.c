
#include "simulator.h"

static char const rcsid[] = "$Id$";

static int atomCount;
static int allowScaling; // non-zero if a scale difference will be allowed

static struct xyz *BasePositions;
static struct xyz *InitialPositions;

// The "extra" field in this case is the array of coordinates of the
// atom positions.  The position and orientation of the structure as a
// whole is stored in the coordinate array, and it is that position
// which is minimized.  The set of atom positions is a temporary value
// used by the potential function.  This is the routine that defines
// the meaning of the transformations described by the coordinates
// being minimized.
static void
structCompareSetExtra(struct configuration *p)
{
  int i;
  struct xyz translate;
  struct xyz t;
  double rotation[9];
  double scale = 1.0;
  
  if (p->extra != NULL) {
    return;
  }
  p->extra = allocate(sizeof(struct xyz) * atomCount);

  translate.x = p->coordinate[0];
  translate.y = p->coordinate[1];
  translate.z = p->coordinate[2];
  if (allowScaling) {
    scale = p->coordinate[6];
  }

  matrixRotateXYZ(rotation, p->coordinate[3], p->coordinate[4], p->coordinate[5]);

  for (i=0; i<atomCount; i++) {
    vadd2(t, InitialPositions[i], translate);
    if (allowScaling) {
      vmulc(t, scale);
    }
    matrixTransform(&((struct xyz *)p->extra)[i], rotation, &t);
  }
}

static void
structCompareFreeExtra(struct configuration *p)
{
  if (p->extra != NULL) {
    free(p->extra);
    p->extra = NULL;
  }
}

#ifndef isnormal
int
isnormal(double a)
{
    return (a > 0.0 || a <= 0.0);
}
#endif

// Handle the final result for a structure compare.  Pass in an upper
// limit for the standard deviation of atom positions between the two
// structures, and an upper limit for the maximum distance that any
// single atom has moved between the two structures, and an upper
// limit to the scale difference between the structures.  Returns
// non-zero if the configuration exceeds any of these limits.
//
// May want to do a Chi-Squared test here, but I'm not sure of the
// applicability.  Besides, generating Chi-Square values for large
// numbers of degrees of freedom is non-trivial.
static int
structCompareResult(struct configuration *p,
                    double deviationLimit,
                    double maxDeltaLimit,
                    double maxScale)
{
  int i;
  int ret = 0;
  struct xyz delta;
  double squareSum = 0.0;
  double deltaLenSquared;
  double maxDeltaLenSquared = 0.0;
  double maxDeltaLen;
  double standardDeviation;
  double scale = 1.0;
  
  structCompareSetExtra(p);
  for (i=0; i<atomCount; i++) {
    delta = vdif(BasePositions[i], ((struct xyz *)p->extra)[i]);
    deltaLenSquared = vdot(delta, delta);
    squareSum += deltaLenSquared;
    if (maxDeltaLenSquared < deltaLenSquared) {
      maxDeltaLenSquared = deltaLenSquared;
    }
  }
  if (atomCount < 2) {
    standardDeviation = 0.0;
  } else {
    standardDeviation = squareSum / (atomCount - 1);
  }
  maxDeltaLen = sqrt(maxDeltaLenSquared);
  if (allowScaling) {
    scale = fabs(p->coordinate[6]);
    if (scale < 1.0) {
      if (scale > 0.0) {
        scale = 1.0 / scale;
      } // shouldn't ever be zero!
    }
  }
  
  printf("at: translate (%f %f %f)\n       rotate (%f %f %f)\n        scale %f,\nstandard deviation = %e, max delta = %e\n",
         p->coordinate[0], p->coordinate[1], p->coordinate[2],
         p->coordinate[3], p->coordinate[4], p->coordinate[5],
         scale, standardDeviation, maxDeltaLen);

  if (standardDeviation != 0.0 && !isnormal(standardDeviation)) {
    printf("standard deviation not defined\n");
    ret = 1;
  }
  if (standardDeviation > deviationLimit) {
    printf("standard deviation exeeded deviationLimit of %e\n", deviationLimit);
    ret = 1;
  }
  if (maxDeltaLen != 0.0 && !isnormal(maxDeltaLen)) {
    printf("maximum delta not defined\n");
    ret = 1;
  }
  if (maxDeltaLen > maxDeltaLimit) {
    printf("maximum delta exceeded max delta limit of %e\n", maxDeltaLimit);
    ret = 1;
  }
  if (scale != 0.0 && !isnormal(scale)) {
    printf("scale not defined\n");
    ret = 1;
  }
  if (scale > maxScale) {
    printf("scale exceeded limit of %e\n", maxScale);
    ret = 1;
  }
  return ret;
}

// This is the potential function which is being minimized.  We're
// basically doing a least-squares fit for the coordinates of the
// structure as a whole.
static void
structComparePotential(struct configuration *p)
{
  int i;
  struct xyz delta;
  double squareSum = 0.0;

  structCompareSetExtra(p);
  for (i=0; i<atomCount; i++) {
    delta = vdif(BasePositions[i], ((struct xyz *)p->extra)[i]);
    squareSum += vdot(delta, delta);
  }
  p->functionValue = squareSum / atomCount;
  /*
  printf("at: (%f %f %f) (%f %f %f) == %e\n",
         p->coordinate[0], p->coordinate[1], p->coordinate[2],
         p->coordinate[3], p->coordinate[4], p->coordinate[5],
         p->functionValue);
  */
}

// Before starting to rotate the structures, we translate both of them
// to their respective centers of mass.  We're taking each atom as a
// unit mass, ignoring element type.
static void
translateToCenterOfMass(struct xyz *pos, int atomCount)
{
  struct xyz centerOfMass;
  int i;
  
  vsetc(centerOfMass, 0.0);
  for (i=0; i<atomCount; i++) {
    vadd(centerOfMass, pos[i]);
  }
  vdivc(centerOfMass, -atomCount);
  for (i=0; i<atomCount; i++) {
    vadd(pos[i], centerOfMass);
  }
}

static struct functionDefinition structCompareFunctions;

// Compare two structures to see if they are the same.  The atom
// positions must have been pre-loaded into BasePositions and
// InitialPositions.  The structures are translated to their
// respective centers of mass.  Then, the InitialPositions structure
// is rotated, translated, and optionally scaled (if maxScale > 1.0)
// to minimize the least-square distance between corresponding atoms
// in the two structures.  At most iterLimit iterations of the
// minimize routine are performed.
//
// Prints the final coordinates reached.  
//
// Pass in an upper limit for the standard deviation of atom positions
// between the two structures, and an upper limit for the maximum
// distance that any single atom has moved between the two
// structures, and an upper limit to the scale difference between the
// structures.  Returns non-zero if the configuration exceeds any of
// these limits.
int
doStructureCompare(int numberOfAtoms,
                   struct xyz *basePositions,
                   struct xyz *initialPositions,
                   int iterLimit,
                   double deviationLimit,
                   double maxDeltaLimit,
                   double maxScale)
{
  int iter;
  int ret;
  struct configuration *initial = NULL;
  struct configuration *final = NULL;

  atomCount = numberOfAtoms;
  BasePositions = basePositions;
  InitialPositions = initialPositions;
  allowScaling = maxScale > 1.0;

  translateToCenterOfMass(BasePositions, atomCount);
  translateToCenterOfMass(InitialPositions, atomCount);

  initializeFunctionDefinition(&structCompareFunctions,
                               structComparePotential,
                               allowScaling ? 7 : 6,
                               0);

  structCompareFunctions.gradient_delta = 1e-8;
  structCompareFunctions.freeExtra = structCompareFreeExtra;
  structCompareFunctions.coarse_tolerance = 1e-3;
  structCompareFunctions.fine_tolerance = 1e-8;
  structCompareFunctions.initial_parameter_guess = 0.001;

  initial = makeConfiguration(&structCompareFunctions);
  initial->coordinate[0] = 0.0;
  initial->coordinate[1] = 0.0;
  initial->coordinate[2] = 0.0;
  initial->coordinate[3] = 0.0;
  initial->coordinate[4] = 0.0;
  initial->coordinate[5] = 0.0;
  if (allowScaling) {
    initial->coordinate[6] = 1.0;
  }

  final = minimize(initial, &iter, iterLimit);
  ret = structCompareResult(final, deviationLimit, maxDeltaLimit, maxScale);
  SetConfiguration(&initial, NULL);
  SetConfiguration(&final, NULL);
  return ret;
}



#ifdef TEST

static void
testStructureCompare()
{
  int numberOfAtoms;
  struct xyz *basePositions;
  struct xyz *InitialPositions;
  
  numberOfAtoms = 3;
  basePositions = (struct xyz *)allocate(sizeof(struct xyz) * numberOfAtoms);
  InitialPositions = (struct xyz *)allocate(sizeof(struct xyz) * numberOfAtoms);

  basePositions[0].x =   30.0;
  basePositions[0].y =    0.0;
  basePositions[0].z =    0.0;
  basePositions[1].x = - 30.0;
  basePositions[1].y =    0.0;
  basePositions[1].z =   10.0;
  basePositions[2].x = - 30.0;
  basePositions[2].y =    0.0;
  basePositions[2].z =  -10.0;

  initialPositions[0].x =    0.0;
  initialPositions[0].y =   30.0;
  initialPositions[0].z =    0.0;
  initialPositions[1].x =   10.0;
  initialPositions[1].y = - 30.0;
  initialPositions[1].z =    0.0;
  initialPositions[2].x =  -10.0;
  initialPositions[2].y = - 30.0;
  initialPositions[2].z =    0.0;

  doStructureCompare(numberOfAtoms, basePositions, initialPositions, 400, 1e-2, 1e-1, 0.0);
}

int
main(int argc, char **argv)
{
  testStructureCompare();
  exit(0);
}

#endif
