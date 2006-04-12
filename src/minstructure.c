/* Copyright (c) 2006 Nanorex, Inc. All rights reserved. */

#include "simulator.h"

static char const rcsid[] = "$Id$";

static struct part *Part;

static void
findRMSandMaxForce(struct configuration *p, double *pRMS, double *pMaxForce)
{
    struct xyz f;
    int i;
    double forceSquared;
    double sum_forceSquared = 0.0;
    double max_forceSquared = -1.0;

    // wware 060109  python exception handling
    NULLPTR(p);
    NULLPTR(pRMS);
    NULLPTR(pMaxForce);
    for (i=0; i<Part->num_atoms; i++) {
        if (Part->atoms[i]->isGrounded) {
            continue;
        }
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

static FILE *minimizeCountFile;

static void
countMinimizeEvaulations(char which)
{
    if (minimizeCountFile == NULL) {
        minimizeCountFile = fopen("/tmp/minimizecounts", "a");
        if (minimizeCountFile == NULL) {
            perror("/tmp/minimizecounts");
            exit(1);
        }
    }
    fputc(which, minimizeCountFile);
    fflush(minimizeCountFile);
}

// This is the potential function which is being minimized.
static void
minimizeStructurePotential(struct configuration *p)
{
    int i;
    struct jig *jig;
    
    updateVanDerWaals(Part, p, (struct xyz *)p->coordinate);
    p->functionValue = calculatePotential(Part, (struct xyz *)p->coordinate);
    for (i=0; i<Part->num_jigs; i++) {
        jig = Part->jigs[i];
        switch (jig->type) {
        case RotaryMotor:
            p->functionValue +=
                jigMinimizePotentialRotaryMotor(Part, jig,
                                                (struct xyz *)p->coordinate,
                                                p->coordinate + jig->coordinateIndex);
            break;
        case LinearMotor:
            p->functionValue +=
                jigMinimizePotentialLinearMotor(Part, jig,
                                                (struct xyz *)p->coordinate,
                                                p->coordinate + jig->coordinateIndex);
            break;
        default:
            break;
        }
    }
    //writeMinimizeMovieFrame(OutputFile, Part, 0, (struct xyz *)p->coordinate, p->functionValue, p->parameter,
    //                        Iteration++, "potential", p->functionDefinition->message);
    if (DEBUG(D_MINIMIZE_POTENTIAL_MOVIE)) { // -D3
	writeSimpleMovieFrame(Part, (struct xyz *)p->coordinate, NULL, "potential %e %e", p->functionValue, p->parameter);
    }
    if (DEBUG(D_MINIMIZE_PARAMETER_GUESS)) {
        countMinimizeEvaulations('p');
    }
}

static double
clamp(double min, double max, double value)
{
    if (value > max) return max;
    if (value < min) return min;
    return value;
}

static double last_rms_force = 0.0;
static double last_max_force = 0.0;
static FILE *parameterGuessFile = NULL;

// A rotary motor should turn no farther than this during a single
// linear minimization.
#define MAX_RADIANS_PER_STEP 0.4

// This is the gradient of the potential function which is being minimized.
static void
minimizeStructureGradient(struct configuration *p)
{
    int i;
    double rms_force;
    double max_force;
    double parameterLimit;
    double motorGradient;
    double plimit;
    struct xyz *forces;
    struct jig *jig;

    // wware 060109  python exception handling
    updateVanDerWaals(Part, p, (struct xyz *)p->coordinate); BAIL();
    if (DEBUG(D_GRADIENT_FROM_POTENTIAL)) { // -D 10
	// wware 060109  python exception handling
	evaluateGradientFromPotential(p); BAIL();
        if (DEBUG(D_MINIMIZE_GRADIENT_MOVIE)) { // -D4
            forces = (struct xyz *)p->gradient;
            for (i=0; i<Part->num_atoms; i++) {
                writeSimpleForceVector((struct xyz *)p->coordinate, i, &forces[i], 6, 1000000.0); // yellow
            }
        }
    } else {
	calculateGradient(Part, (struct xyz *)p->coordinate, (struct xyz *)p->gradient);
	BAIL();
    }

    parameterLimit = MAXDOUBLE;
    for (i=0; i<Part->num_jigs; i++) {
        jig = Part->jigs[i];
        switch (jig->type) {
        case RotaryMotor:
            jigMinimizeGradientRotaryMotor(Part, jig,
                                           (struct xyz *)p->coordinate,
                                           (struct xyz *)p->gradient,
                                           p->coordinate + jig->coordinateIndex,
                                           p->gradient + jig->coordinateIndex);
            motorGradient = fabs(*(p->gradient + jig->coordinateIndex));
	    CHECKNAN(motorGradient);
            if (motorGradient < 1e-8) {
                motorGradient = 1e-8;
            }
            plimit = MAX_RADIANS_PER_STEP / motorGradient;
            if (plimit < parameterLimit) {
                parameterLimit = plimit;
            }
            break;
        case LinearMotor:
            jigMinimizeGradientLinearMotor(Part, jig,
                                           (struct xyz *)p->coordinate,
                                           (struct xyz *)p->gradient,
                                           p->coordinate + jig->coordinateIndex,
                                           p->gradient + jig->coordinateIndex);
            break;
        default:
            break;
        }
    }
    p->functionDefinition->parameter_limit = parameterLimit;

    // dynamics wants gradient pointing downhill, we want it uphill
    //for (i=0; i<3*Part->num_atoms; i++) {
    //  p->gradient[i] = -p->gradient[i];
    //}
    findRMSandMaxForce(p, &rms_force, &max_force); BAIL();

    // The initial parameter guess function is empirically determined.
    // The regression tests were run with D_MINIMIZE_PARAMETER_GUESS
    // enabled (compiled on in simulator.c).  Plots of the max_force
    // vs minimum parameter value columns were examined with gnuplot.
    // A functional form was determined which stayed within the main
    // body of the data points.  Final determination was based on the
    // evaluation counts also output with that debugging flag on.
    // Given that max_force is non-negative, the current form doesn't
    // need the upper range limit in the clamp.
    p->functionDefinition->initial_parameter_guess = clamp(1e-20, 1e3,
                                                           0.7 / (max_force + 1000.0) +
                                                           0.1 / (max_force + 20.0));
    
    writeMinimizeMovieFrame(OutputFile, Part, 0, (struct xyz *)p->coordinate, rms_force, max_force, Iteration++,
			    "gradient", p->functionDefinition->message);
    if (DEBUG(D_MINIMIZE_GRADIENT_MOVIE)) { // -D4
	writeSimpleMovieFrame(Part, (struct xyz *)p->coordinate, (struct xyz *)p->gradient, "gradient %e %e", rms_force, max_force);
    }
    if (DEBUG(D_MINIMIZE_PARAMETER_GUESS)) {
        countMinimizeEvaulations('g');
        if (parameterGuessFile == NULL) {
            parameterGuessFile = fopen("/tmp/parameterguesses", "a");
            if (parameterGuessFile == NULL) {
                perror("/tmp/parameterguesses");
                exit(1);
            }
        } else {
            fprintf(parameterGuessFile, "%e %e %e\n", last_rms_force, last_max_force, p->parameter);
            fflush(parameterGuessFile);
        }
        last_rms_force = rms_force;
        last_max_force = max_force;
    }
}

static int
minimizeStructureTermination(struct functionDefinition *fd,
                             struct configuration *previous,
                             struct configuration *current,
                             double tolerance)
{
    double fp;
    double fq;
    double rms_force;
    double max_force;

    fp = evaluate(previous); BAILR(0);
    fq = evaluate(current); BAILR(0);
    // wware 060109  python exception handling
    evaluateGradient(current); BAILR(0);
    findRMSandMaxForce(current, &rms_force, &max_force); BAILR(0);
    if (tolerance == fd->coarse_tolerance) {
        if (rms_force < 50.0 && max_force < 300.0) {
            return 1;
        }
    } else {
        if (rms_force < 1.0 && max_force < 10.0) {
            return 1;
        }
    }
#define EPSILON 1e-10
    
    DPRINT2(D_MINIMIZE, "delta %e, tol*avgVal %e\n", // -D2
            fabs(fq-fp), tolerance * (fabs(fq)+fabs(fp)+EPSILON)/2.0);
    if (2.0 * fabs(fq-fp) <= tolerance * (fabs(fq)+fabs(fp)+EPSILON)) {
        DPRINT5(D_MINIMIZE,
                "fp: %e fq: %e || delta %e <= tolerance %e * averageValue %e",
                fp, fq,
                fabs(fq-fp), tolerance, (fabs(fq)+fabs(fp)+EPSILON)/2.0);
        return 1;
    }
    return 0;
}

static void
minimizeStructureConstraints(struct configuration *p) 
{
    int i;
    int j;
    double dist;
    struct jig *jig;
    struct xyz *positions = (struct xyz *)p->coordinate;
    struct xyz delta;
    struct atom *a;
    int index;
    
    for (i=0; i<Part->num_jigs; i++) {
        jig = Part->jigs[i];
        switch (jig->type) {
        case Ground:
            for (j=0; j<jig->num_atoms; j++) {
                a = jig->atoms[j];
                index = a->index;
                positions[index] = Part->positions[index];
            }
            break;
        case LinearMotor:
            for (j=0; j<jig->num_atoms; j++) {
                a = jig->atoms[j];
                index = a->index;
                // restrict motion of atom to lay along axis from initial position
                // dist = (positions[index] - Part->positions[index]) dot jig->j.lmotor.axis
                // positions[index] = Part->positions[index] + jig->j.lmotor.axis * dist
                vsub2(delta, positions[index], Part->positions[index]);
                dist = vdot(delta, jig->j.lmotor.axis);
                vmul2c(delta, jig->j.lmotor.axis, dist);
                vadd2(positions[index], Part->positions[index], delta);
            }
            break;
        default:
            break;
        }
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
    int jigDegreesOfFreedom;
    int coordinateCount;
    double rms_force;
    double max_force;
    struct jig *jig;

    NULLPTR(part);
    Part = part;

    jigDegreesOfFreedom = 0;
    coordinateCount = part->num_atoms * 3;
    for (i=0; i<Part->num_jigs; i++) {
        jig = Part->jigs[i];
        jig->coordinateIndex = coordinateCount + jigDegreesOfFreedom;
        jigDegreesOfFreedom += jig->degreesOfFreedom;
    }

    initializeFunctionDefinition(&minimizeStructureFunctions,
                                 minimizeStructurePotential,
                                 coordinateCount + jigDegreesOfFreedom,
                                 1024);
    BAIL();
    
    minimizeStructureFunctions.dfunc = minimizeStructureGradient;
    minimizeStructureFunctions.termination = minimizeStructureTermination;
    minimizeStructureFunctions.constraints = minimizeStructureConstraints;
    minimizeStructureFunctions.coarse_tolerance = 1e-8;
    minimizeStructureFunctions.fine_tolerance = 1e-10;

    initial = makeConfiguration(&minimizeStructureFunctions);
    for (i=0, j=0; i<part->num_atoms; i++) {
	initial->coordinate[j++] = part->positions[i].x;
	initial->coordinate[j++] = part->positions[i].y;
	initial->coordinate[j++] = part->positions[i].z;
    }

    final = minimize(initial, &iter, NumFrames * 100);

    if (final != NULL) {
	// wware 060109  python exception handling
	evaluateGradient(final); BAIL();
	findRMSandMaxForce(final, &rms_force, &max_force); BAIL();

	writeMinimizeMovieFrame(OutputFile, part, 1, (struct xyz *)final->coordinate, rms_force, max_force,
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
    done("Minimize evals: %d, %d; final forces: rms %f pN, high %f pN",
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
