#include "simulator.h"

static int atomCount;

static void
structCompareSetExtra(struct configuration *p)
{
  int i;
  struct xyz translate;
  struct xyz t;
  double rotation[9];
  
  if (p->extra != NULL) {
    return;
  }
  p->extra = allocate(sizeof(struct xyz) * atomCount);

  translate.x = p->coordinate[0];
  translate.y = p->coordinate[1];
  translate.z = p->coordinate[2];

  matrixRotateXYZ(rotation, p->coordinate[3], p->coordinate[4], p->coordinate[5]);

  for (i=0; i<atomCount; i++) {
    vadd2(t, InitialPositions[i], translate);
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

struct configuration *
doStructureCompare(int numberOfAtoms, int *iter, int iterLimit)
{
  struct configuration *initial = NULL;
  struct configuration *final = NULL;

  atomCount = numberOfAtoms;

  translateToCenterOfMass(BasePositions, atomCount);
  translateToCenterOfMass(InitialPositions, atomCount);
  
  structCompareFunctions.func = structComparePotential;
  structCompareFunctions.dfunc = NULL; // use default gradient
  structCompareFunctions.gradient_delta = 1e-8;
  structCompareFunctions.freeExtra = structCompareFreeExtra;
  structCompareFunctions.coarse_tolerance = 1e-3;
  structCompareFunctions.fine_tolerance = 1e-8;
  structCompareFunctions.dimension = 6;
  structCompareFunctions.initial_parameter_guess = 0.001;
  structCompareFunctions.functionEvaluationCount = 0;
  structCompareFunctions.gradientEvaluationCount = 0;

  initial = makeConfiguration(&structCompareFunctions);
  initial->coordinate[0] = 0.0;
  initial->coordinate[1] = 0.0;
  initial->coordinate[2] = 0.0;
  initial->coordinate[3] = 0.0;
  initial->coordinate[4] = 0.0;
  initial->coordinate[5] = 0.0;

  *iter = 0;
  final = minimize(initial, iter, iterLimit);
  SetConfiguration(&initial, NULL);
  return final;
}



#ifdef TEST

struct xyz *BasePositions;
struct xyz *InitialPositions;

static void
testStructureCompare()
{
  struct configuration *final = NULL;
  int Iteration;
  int numberOfAtoms;
  
  numberOfAtoms = 3;
  BasePositions = (struct xyz *)allocate(sizeof(struct xyz) * numberOfAtoms);
  InitialPositions = (struct xyz *)allocate(sizeof(struct xyz) * numberOfAtoms);

  BasePositions[0].x =   30.0;
  BasePositions[0].y =    0.0;
  BasePositions[0].z =    0.0;
  BasePositions[1].x = - 30.0;
  BasePositions[1].y =    0.0;
  BasePositions[1].z =   10.0;
  BasePositions[2].x = - 30.0;
  BasePositions[2].y =    0.0;
  BasePositions[2].z =  -10.0;

  InitialPositions[0].x =    0.0;
  InitialPositions[0].y =   30.0;
  InitialPositions[0].z =    0.0;
  InitialPositions[1].x =   10.0;
  InitialPositions[1].y = - 30.0;
  InitialPositions[1].z =    0.0;
  InitialPositions[2].x =  -10.0;
  InitialPositions[2].y = - 30.0;
  InitialPositions[2].z =    0.0;

  final = doStructureCompare(numberOfAtoms, &Iteration, 400);

  fprintf(stderr, "final minimum at (%f %f %f) (%f %f %f): %e\n",
          final->coordinate[0],
          final->coordinate[1],
          final->coordinate[2],
          final->coordinate[3],
          final->coordinate[4],
          final->coordinate[5],
          evaluate(final));
  fprintf(stderr, "after %d iterations, %d function evals, %d gradient evals\n",
          Iteration,
          final->functionDefinition->functionEvaluationCount,
          final->functionDefinition->gradientEvaluationCount);
  SetConfiguration(&final, NULL);
}

int
main(int argc, char **argv)
{
  testStructureCompare();
  exit(0);
}

#endif
