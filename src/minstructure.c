
#include "simulator.h"

static struct part *Part;

// This is the potential function which is being minimized.
static void
minimizeStructurePotential(struct configuration *p)
{
  updateVanDerWaals(Part, p, (struct xyz *)p->coordinate);
  p->functionValue = calculatePotential(Part, (struct xyz *)p->coordinate);
}

// This is the gradient of the potential function which is being minimized.
static void
minimizeStructureGradient(struct configuration *p)
{
  updateVanDerWaals(Part, p, (struct xyz *)p->coordinate);
  calculateGradient(Part, (struct xyz *)p->coordinate, (struct xyz *)p->gradient);
}

static struct functionDefinition minimizeStructureFunctions;

void
minimizeStructure(struct part *part)
{
  int iter;
  struct configuration *initial;
  struct configuration *final;
  int i;
  int j;
  
  Part = part;
    
  minimizeStructureFunctions.func = minimizeStructurePotential;
  minimizeStructureFunctions.dfunc = minimizeStructureGradient;
  minimizeStructureFunctions.freeExtra = NULL;
  minimizeStructureFunctions.coarse_tolerance = 1e-3;
  minimizeStructureFunctions.fine_tolerance = 1e-8;
  minimizeStructureFunctions.gradient_delta = 0.0; // unused
  minimizeStructureFunctions.dimension = part->num_atoms * 3;
  minimizeStructureFunctions.initial_parameter_guess = 1.0;
  minimizeStructureFunctions.functionEvaluationCount = 0;
  minimizeStructureFunctions.gradientEvaluationCount = 0;

  initial = makeConfiguration(&minimizeStructureFunctions);
  for (i=0, j=0; i<part->num_atoms; i++) {
    initial->coordinate[j++] = part->positions[i].x;
    initial->coordinate[j++] = part->positions[i].y;
    initial->coordinate[j++] = part->positions[i].z;
  }

  final = minimize(initial, &iter, NumFrames);

  minshot(outf, part, 1, (struct xyz *)final->coordinate, 0.0, 0.0, iter, "final structure");
  
  SetConfiguration(&initial, NULL);
  SetConfiguration(&final, NULL);
}
