#include "simulator.h"
#include "minimize.h"

#define EPSILON 1e-20

#ifdef TEST
extern void writeConfiguration(struct configuration *p);
#else
void writeConfiguration(struct configuration *p) {}
#endif

int atomCount;

static void
structCompareSetExtra(struct configuration *p)
{
  int i;
  struct xyz translate;
  struct xyz t;
  double rotation[9];
  double oneAxis[9];
  double tmp[9];
  
  if (p->extra != NULL) {
    return;
  }
  p->extra = allocate(sizeof(struct xyz) * atomCount);
  //printf("trying rotation: (%f %f %f)\n", p->coordinate[3], p->coordinate[4], p->coordinate[5]);

  translate.x = p->coordinate[0];
  translate.y = p->coordinate[1];
  translate.z = p->coordinate[2];

  // rotate first around X, then Y, then Z
  matrixRotateX(rotation, p->coordinate[3]);
  matrixRotateY(oneAxis, p->coordinate[4]);
  matrixMultiply(tmp, rotation, oneAxis);
  matrixRotateZ(oneAxis, p->coordinate[5]);
  matrixMultiply(rotation, tmp, oneAxis);

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
  writeConfiguration(p);
  for (i=0; i<atomCount; i++) {
    delta = vdif(BasePositions[i], ((struct xyz *)p->extra)[i]);
    squareSum += vdot(delta, delta);
  }
  p->functionValue = squareSum / atomCount;
}

static void
structCompareGradient(struct configuration *p)
{
  int i;
  struct xyz centerOfMass;
  struct xyz offset; // from centerOfMass
  struct xyz delta; // between like atoms in the two structures
  struct xyz singleTorque; // torque due to a single atom
  struct xyz singleTranslation; // translational force due to a single atom
  struct xyz totalTorque;
  struct xyz totalTranslation;
  double translation;
  double deltaLen;
  
  structCompareSetExtra(p);
  writeConfiguration(p);
  vsetc(centerOfMass, 0.0);
  vsetc(totalTorque, 0.0);
  vsetc(totalTranslation, 0.0);
  
  for (i=0; i<atomCount; i++) {
    vadd(centerOfMass, ((struct xyz *)p->extra)[i]);
  }
  vdivc(centerOfMass, atomCount);
  
  for (i=0; i<atomCount; i++) {
    vsub2(offset, ((struct xyz *)p->extra)[i], centerOfMass);
    vsub2(delta, BasePositions[i], ((struct xyz *)p->extra)[i]);
    // at this point we could adjust delta to reflect different
    // potential functions based on distance
    v2x(singleTorque, offset, delta);
    translation = vdot(offset, delta);
    deltaLen = vlen(delta);
    if (deltaLen > EPSILON) {
      translation /= deltaLen;
    } else {
      translation = 0.0;
    }
    vmul2c(singleTranslation, delta, translation);
    // we assume that torques are small enough to add like vectors.
    vadd(totalTorque, singleTorque);
    vadd(totalTranslation, singleTranslation);
  }
#define DOTRANSLATE_NO
#ifdef DOTRANSLATE
  p->gradient[0] = totalTranslation.x;
  p->gradient[1] = totalTranslation.y;
  p->gradient[2] = totalTranslation.z;
#else
  p->gradient[0] = 0.0;
  p->gradient[1] = 0.0;
  p->gradient[2] = 0.0;
#endif
  p->gradient[3] = totalTorque.x;
  p->gradient[4] = totalTorque.y;
  p->gradient[5] = totalTorque.z;

  /*
  printf("gradient: (%f %f %f) (%f %f %f)\n",
         p->gradient[0],
         p->gradient[1],
         p->gradient[2],
         p->gradient[3],
         p->gradient[4],
         p->gradient[5]);
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

void
doStructureCompare()
{
}



#ifdef TEST

struct xyz *Positions;
struct xyz *OldPositions;
struct xyz *BasePositions;
struct xyz *InitialPositions;

struct xyz Force[1];

static int frame_number = 0;
FILE *movieFile;
FILE *tracef;
char OutFileName[40];
struct A atom[1];
struct B bond[1];
struct Q torq[1];
struct AXLE Constraint[1];
int NumFrames;
int Nexatom;
int Nexbon;
int Nextorq = 0;
int Nexcon = 0;
char *IDKey = NULL;
int KeyRecordInterval = 20;
int IterPerFrame = 1;
double Dt = 1;
double Dx = 1;
int DumpAsText = 0;
int OutputFormat = 1;
int DumpIntermediateText = 0;
int debug_flags = 0;
int Interrupted = 0;
double Pi;

struct atomType periodicTable[MAX_ELEMENT+1];


int Iteration;


void
writeConfiguration(struct configuration *p)
{
  snapshot(movieFile, frame_number++, (struct xyz *)(p->extra));
}

static void
evalConfig(struct functionDefinition *fd, double theta)
{
  struct configuration *c;
  double f;
  
  c = makeConfiguration(fd);
  c->coordinate[0] = 0.0;
  c->coordinate[1] = 0.0;
  c->coordinate[2] = 0.0;
  c->coordinate[3] = 0.0;
  c->coordinate[4] = 0.0;
  c->coordinate[5] = theta * 3.14159265359;

  f = evaluate(c);
  evaluateGradient(c);
  printf("%f %f %f\n", theta, f, c->gradient[5]);
  SetConfiguration(&c, NULL);
}

#define FERD 3

static void
testStructureCompare(FILE *movieFile)
{
  struct functionDefinition fd;
  struct configuration *initial = NULL;
  struct configuration *final = NULL;
  double theta;
  
  atomCount = FERD;
  Nexatom = atomCount;
  BasePositions = (struct xyz *)allocate(sizeof(struct xyz) * atomCount);
  InitialPositions = (struct xyz *)allocate(sizeof(struct xyz) * atomCount);
#if FERD == 3
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
#else
  BasePositions[0].x =   30.0;
  BasePositions[0].y =    0.0;
  BasePositions[0].z =    0.0;
  BasePositions[1].x = - 30.0;
  BasePositions[1].y =    0.0;
  BasePositions[1].z =    0.0;

  InitialPositions[0].x =    0.0;
  InitialPositions[0].y =   30.0;
  InitialPositions[0].z =    0.0;
  InitialPositions[1].x =    0.0;
  InitialPositions[1].y = - 30.0;
  InitialPositions[1].z =    0.0;
#endif

  translateToCenterOfMass(BasePositions, atomCount);
  translateToCenterOfMass(InitialPositions, atomCount);
  
  Positions = InitialPositions;
  writeOutputHeader(movieFile);
  
  fd.func = structComparePotential;
  fd.dfunc = structCompareGradient;
  fd.freeExtra = structCompareFreeExtra;
  fd.dimension = 6;
  fd.functionEvaluationCount = 0;
  fd.gradientEvaluationCount = 0;

  for (theta=0; theta<4; theta+=0.01) {
    evalConfig(&fd, theta);
  }
  if (0) {

  initial = makeConfiguration(&fd);
  initial->coordinate[0] = 0.0;
  initial->coordinate[1] = 0.0;
  initial->coordinate[2] = 0.0;
  initial->coordinate[3] = 0.0;
  initial->coordinate[4] = 0.0;
  initial->coordinate[5] = 0.0;
  
  final = minimize(initial, &Iteration, NumFrames);
  fprintf(stderr, "final minimum at (%f %f %f) (%f %f %f): %f\n",
          final->coordinate[0],
          final->coordinate[1],
          final->coordinate[2],
          final->coordinate[3],
          final->coordinate[4],
          final->coordinate[5],
          evaluate(final));
  SetConfiguration(&initial, NULL);
  SetConfiguration(&final, NULL);
  fprintf(stderr, "after %d iterations, %d function evals, %d gradient evals\n",
          Iteration,
          fd.functionEvaluationCount,
          fd.gradientEvaluationCount);
  }
  
  writeOutputTrailer(movieFile, frame_number);
  fclose(movieFile);
}

int
main(int argc, char **argv)
{
  strcpy(OutFileName, "testStructureCompare.dpb");
  movieFile = fopen(OutFileName, "w");
  if (movieFile == NULL) {
    perror(OutFileName);
    exit(1);
  }
  tracef = fopen("testStructureCompare.tra", "w");
  if (tracef == NULL) {
    perror("testStructureCompare.tra");
    exit(1);
  }
  NumFrames = 400;
  testStructureCompare(movieFile);
  exit(0);
}

#endif
