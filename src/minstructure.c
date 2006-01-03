
#include "simulator.h"

static struct part *Part;

static void
findRMSandMaxForce(struct configuration *p, double *pRMS, double *pMaxForce)
{
    struct xyz f;
    int i;
    double forceSquared;
    double sum_forceSquared = 0.0;
    double max_forceSquared = -1.0;

    for (i=0; i<Part->num_atoms; i++) {
	f = ((struct xyz *)p->gradient)[i];
	forceSquared = vdot(f,f);
	sum_forceSquared += forceSquared;
	if (forceSquared > max_forceSquared) {
	    max_forceSquared = forceSquared;
	}
    }
    *pRMS = sqrt(sum_forceSquared / Part->num_atoms);
    *pMaxForce = sqrt(max_forceSquared);
}

// This is the potential function which is being minimized.
static void
minimizeStructurePotential(struct configuration *p)
{
    updateVanDerWaals(Part, p, (struct xyz *)p->coordinate);
    p->functionValue = calculatePotential(Part, (struct xyz *)p->coordinate);
    //writeMinimizeMovieFrame(outf, Part, 0, (struct xyz *)p->coordinate, p->functionValue, p->parameter,
    //                        Iteration++, "potential", p->functionDefinition->message);
    if (DEBUG(D_MINIMIZE_POTENTIAL_MOVIE)) { // -D3
	writeSimpleMovieFrame(Part, (struct xyz *)p->coordinate, NULL, "potential %e %e", p->functionValue, p->parameter);
    }
}

static double
clamp(double min, double max, double value)
{
    if (value > max) return max;
    if (value < min) return min;
    return value;
}

// This is the gradient of the potential function which is being minimized.
static void
minimizeStructureGradient(struct configuration *p)
{
    int i;
    double rms_force;
    double max_force;
    struct xyz *forces;

    updateVanDerWaals(Part, p, (struct xyz *)p->coordinate);
    if (DEBUG(D_GRADIENT_FROM_POTENTIAL)) { // -D 10
	evaluateGradientFromPotential(p);
	if (DEBUG(D_MINIMIZE_GRADIENT_MOVIE)) { // -D4
	    forces = (struct xyz *)p->gradient;
	    for (i=0; i<Part->num_atoms; i++) {
		writeSimpleForceVector((struct xyz *)p->coordinate, i, &forces[i], 6, 1000000.0);
	    }
	}
    } else {
	calculateGradient(Part, (struct xyz *)p->coordinate, (struct xyz *)p->gradient);
    }

    // dynamics wants gradient pointing downhill, we want it uphill
    //for (i=0; i<3*Part->num_atoms; i++) {
    //  p->gradient[i] = -p->gradient[i];
    //}
    findRMSandMaxForce(p, &rms_force, &max_force);
    p->functionDefinition->initial_parameter_guess = clamp(1e-9, 1e3, 10.0 / max_force);
    writeMinimizeMovieFrame(outf, Part, 0, (struct xyz *)p->coordinate, rms_force, max_force, Iteration++,
			    "gradient", p->functionDefinition->message);
    if (DEBUG(D_MINIMIZE_GRADIENT_MOVIE)) { // -D4
	writeSimpleMovieFrame(Part, (struct xyz *)p->coordinate, (struct xyz *)p->gradient, "gradient %e %e", rms_force, max_force);
    }
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
    double rms_force;
    double max_force;

    Part = part;

    minimizeStructureFunctions.func = minimizeStructurePotential;
    minimizeStructureFunctions.dfunc = minimizeStructureGradient;
    minimizeStructureFunctions.freeExtra = NULL;
    minimizeStructureFunctions.coarse_tolerance = 1e-8;
    minimizeStructureFunctions.fine_tolerance = 1e-10;
    minimizeStructureFunctions.gradient_delta = 0.0; // unused
    minimizeStructureFunctions.dimension = part->num_atoms * 3;
    minimizeStructureFunctions.initial_parameter_guess = 1.0; // recalculated in gradient
    minimizeStructureFunctions.functionEvaluationCount = 0;
    minimizeStructureFunctions.gradientEvaluationCount = 0;
    minimizeStructureFunctions.message = (char *)allocate(1024);
    minimizeStructureFunctions.messageBufferLength = 1024;

    initial = makeConfiguration(&minimizeStructureFunctions);
    for (i=0, j=0; i<part->num_atoms; i++) {
	initial->coordinate[j++] = part->positions[i].x;
	initial->coordinate[j++] = part->positions[i].y;
	initial->coordinate[j++] = part->positions[i].z;
    }

    final = minimize(initial, &iter, NumFrames * 100);

    if (final != NULL) {
	evaluateGradient(final);
	findRMSandMaxForce(final, &rms_force, &max_force);

	writeMinimizeMovieFrame(outf, part, 1, (struct xyz *)final->coordinate, rms_force, max_force,
				Iteration, "final structure", minimizeStructureFunctions.message);

	if (DEBUG(D_MINIMIZE_FINAL_PRINT)) { // -D 11
	    for (i=0, j=0; i<part->num_atoms; i++) {
		part->positions[i].x = final->coordinate[j++];
		part->positions[i].y = final->coordinate[j++];
		part->positions[i].z = final->coordinate[j++];
	    }
	    printPart(stdout, part);
	}
    }

    SetConfiguration(&initial, NULL);
    SetConfiguration(&final, NULL);
    doneNoExit(0, tracef, "Minimize evals: %d, %d; final forces: rms %f, high %f",
	       minimizeStructureFunctions.gradientEvaluationCount,
	       minimizeStructureFunctions.functionEvaluationCount,
	       rms_force,
	       max_force);
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
