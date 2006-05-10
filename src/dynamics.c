/* Copyright (c) 2006 Nanorex, Inc. All rights reserved. */
#include "simulator.h"

static char const rcsid[] = "$Id$";

/*
  inputs:
  OldPositions[*]
  Positions[*]
  bond[*].an1, .an2, .type
  torq[*].dir1, .dir2, .b1, .b2, .kb1, .kb2
  Constraint[*].*
  
  changes:
  finds non-bonded interacting atoms using orion()
  Force[*] contains accumulated force on atom over calculated iterations
  bond[*].r = vector from bond[*].an1 to bond[*].an2 (delta of positions)
  bond[*].invlen = 1/|r|
  bond[*].ru = unit vector along r
  OldPositions
  Positions[*]
  NewPositions[*]
  AveragePositions[*] = average position across all iterations for this call
  Constraint[*].*
  
  returns:
  AveragePositions
*/

void
oneDynamicsFrame(struct part *part,
                 int iters,
                 struct xyz *averagePositions,
                 struct xyz **pOldPositions,
                 struct xyz **pNewPositions,
                 struct xyz **pPositions,
                 struct xyz *force)
{
    int j;
    int loop;
    double deltaTframe;
    struct xyz f;
    struct xyz *tmp;
    struct jig *jig;
    
    struct xyz *oldPositions = *pOldPositions;
    struct xyz *newPositions = *pNewPositions;
    struct xyz *positions = *pPositions;

    // wware 060109  python exception handling
    NULLPTR(part);
    NULLPTR(averagePositions);
    NULLPTR(oldPositions);
    NULLPTR(newPositions);
    NULLPTR(positions);

    iters = max(iters,1);
    
    deltaTframe = 1.0/iters;
    
    for (j=0; j<part->num_atoms; j++) {
	vsetc(averagePositions[j],0.0);
    }
    
    // See http://www.nanoengineer-1.net/mediawiki/index.php?title=Verlet_integration
    // for a discussion of how dynamics is done in the simulator.

    // we want:
    // x(t+dt) = 2x(t) - x(t-dt) + A dt^2
    // or:
    // newPositions = 2 * positions - oldPositions + A dt^2
    
    // wware 060110  don't handle Interrupted with the BAIL mechanism
    for (loop=0; loop < iters && !Interrupted; loop++) {

	_last_iteration = loop == iters - 1;
        
	Iteration++;
	
	// wware 060109  python exception handling
        updateVanDerWaals(part, NULL, positions); BAIL();
	calculateGradient(part, positions, force); BAIL();
	
        /* first, for each atom, find non-accelerated new pos  */
        /* Atom moved from oldPositions to positions last time,
           now we move it the same amount from positions to newPositions */
        for (j=0; j<part->num_atoms; j++) {
            // f = positions - oldPositions
            vsub2(f,positions[j],oldPositions[j]);
            // newPositions = positions + f
            // or:
            // newPositions = 2 * positions - oldPositions
            vadd2(newPositions[j],positions[j],f);
            // after this, we will need to add A dt^2 to newPositions
        }
	
	// pre-force jigs
	for (j=0;j<part->num_jigs;j++) {	/* for each jig */
	    jig = part->jigs[j];
	    // wware 060109  python exception handling
	    NULLPTR(jig);
	    switch (jig->type) {
	    case LinearMotor:
		jigLinearMotor(jig, positions, newPositions, force, deltaTframe);
		break;
	    default:
		break;
	    }
	}
	
	/* convert forces to accelerations, giving new positions */
	//FoundKE = 0.0;		/* and add up total KE */
	for (j=0; j<part->num_atoms; j++) {
            // to complete Verlet integration, this needs to do:
            // newPositions += A dt^2
            //
            // force[] is in pN, mass is in g, Dt in seconds, f in pm
	    vmul2c(f,force[j],part->atoms[j]->inverseMass); // inverseMass = Dt*Dt/mass

            // XXX: 0.15 probably needs a scaling by Dt
            // 0.15 = deltaX
            // keMax = m v^2 / 2
            // v^2 = 2 keMax / m
            // v = deltaX / Dt = sqrt(2 keMax / m)
            // deltaX = Dt sqrt(2 keMax / m)

            // We probably don't want to do this, because a large raw
            // velocity isn't a problem, it's just when that creates a
            // high force between atoms that it becomes a problem.  We
            // check that elsewhere.
            
	    //if (!ExcessiveEnergyWarning && vlen(f)>0.15) { // 0.15 is just below H flyaway
            // WARNING3("Excessive force %.6f in iteration %d on atom %d -- further warnings suppressed", vlen(f), Iteration, j+1);
            // ExcessiveEnergyWarningThisFrame++;
            //}
	    
	    vadd(newPositions[j],f);
	    vadd(averagePositions[j],newPositions[j]);
	    
	    //vsub2(f, newPositions[j], positions[j]);
	    //ff = vdot(f, f);
	    //FoundKE += atom[j].energ * ff;
	}
	
	// Jigs are executed in the following order: motors,
	// thermostats, grounds, measurements.  Motions from each
	// motor are added together, then thermostats operate on the
	// motor output.  Grounds override anything that moves atoms.
	// Measurements happen after all things that could affect
	// positions, including grounds.

        // motors
	for (j=0;j<part->num_jigs;j++) {	/* for each jig */
	    jig = part->jigs[j];
	    
	    if (jig->type == RotaryMotor) {
		jigMotor(jig, deltaTframe, positions, newPositions, force);
            }
            // LinearMotor handled in preforce above
	}

        // thermostats
	for (j=0;j<part->num_jigs;j++) {	/* for each jig */
	    jig = part->jigs[j];
	    
	    if (jig->type == Thermostat) {
		jigThermostat(jig, deltaTframe, positions, newPositions);
	    }
	}

        // grounds
	for (j=0;j<part->num_jigs;j++) {	/* for each jig */
	    jig = part->jigs[j];
	    
	    if (jig->type == Ground) {
		jigGround(jig, deltaTframe, positions, newPositions, force);
            }
	}

        // measurements
	for (j=0;j<part->num_jigs;j++) {	/* for each jig */
	    jig = part->jigs[j];
	    
	    switch (jig->type) {
	    case Thermometer:
		jigThermometer(jig, deltaTframe, positions, newPositions);
		break;
	    case DihedralMeter:
		jigDihedral(jig, newPositions);
		break;
	    case AngleMeter:
		jigAngle(jig, newPositions);
		break;
	    case RadiusMeter:
		jigRadius(jig, newPositions);
		break;
            default:
		break;
	    }
	}
	
	tmp=oldPositions; oldPositions=positions; positions=newPositions; newPositions=tmp;
        if (ExcessiveEnergyWarningThisFrame > 0) {
            ExcessiveEnergyWarning = 1;
        }
    }
    
    for (j=0; j<part->num_atoms; j++) {
	vmulc(averagePositions[j],deltaTframe);
    }
    *pOldPositions = oldPositions;
    *pNewPositions = newPositions;
    *pPositions = positions;
}

#ifndef WIN32
#define SECONDS_PER_MINUTE 60
#define SECONDS_PER_HOUR (SECONDS_PER_MINUTE * 60)
#define SECONDS_PER_DAY (SECONDS_PER_HOUR * 24)

static char *
formatSeconds(double seconds, char *buf)
{
    double secs = seconds;
    int mins = 0;
    int hours = 0;
    int days = 0;

    if (secs > SECONDS_PER_DAY) {
        days = secs / SECONDS_PER_DAY;
        secs -= days * SECONDS_PER_DAY;
    }
    if (secs > SECONDS_PER_HOUR) {
        hours = secs / SECONDS_PER_HOUR;
        secs -= hours * SECONDS_PER_HOUR;
    }
    if (secs > SECONDS_PER_MINUTE) {
        mins = secs / SECONDS_PER_MINUTE;
        secs -= mins * SECONDS_PER_MINUTE;
    }
    sprintf(buf, "%02d:%02d:%02d:%09.6f", days, hours, mins, secs);
    return buf;
}
#endif

void
dynamicsMovie(struct part *part)
{
    struct xyz *averagePositions = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
    struct xyz *oldPositions = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
    struct xyz *newPositions = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
    struct xyz *positions =  (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
    struct xyz *force = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
    int i;
#ifndef WIN32
    int timefailure = 0;
    struct timeval start;
    struct timeval end;
    double elapsedSeconds;
    char timebuffer[256];
#endif
    
    for (i = 0; i < part->num_atoms; i++) {
	vset(positions[i], part->positions[i]);
	vsub2(oldPositions[i], positions[i], part->velocities[i]);
    }

#ifndef WIN32
    // we should probably use times() to get user and system time
    // instead of wall time, but the clock ticks conversions appear to
    // be system dependant.
    if (gettimeofday(&start, NULL)) {
        timefailure = errno;
        errno = 0;
    }
#endif

    // wware 060110  don't handle Interrupted with the BAIL mechanism
    for (i = 0; i < NumFrames && !Interrupted; i++) {
	if (PrintFrameNums) printf(" %d", i);
	fflush(stdout);
	if ((i & 15) == 15)
	    if (PrintFrameNums) printf("\n");
	oneDynamicsFrame(part, IterPerFrame,
			 averagePositions, &oldPositions, &newPositions, &positions, force);
	writeDynamicsMovieFrame(OutputFile, i, part, averagePositions);
        if (DEBUG(D_DYNAMICS_SIMPLE_MOVIE)) {
            writeSimpleMovieFrame(part, newPositions, force, "");
        }
    }
    if (PrintFrameNums) printf("\n");

#ifndef WIN32
    if (gettimeofday(&end, NULL)) {
        timefailure = errno;
    }
        
    if (timefailure) {
        errno = timefailure;
        perror("gettimeofday");
        errno = 0;
    } else {
        end.tv_sec -= start.tv_sec;
        end.tv_usec -= start.tv_usec;
        if (end.tv_usec < 0) {
            end.tv_sec--;
            end.tv_usec += 1000000;
        }
        elapsedSeconds = (double)end.tv_sec + (double)end.tv_usec / 1e6;
        write_traceline("# Duration: %s, %f sec/frame, %f sec/iteration\n",
                        formatSeconds(elapsedSeconds, timebuffer),
                        elapsedSeconds / (double)i,
                        elapsedSeconds / (double)(i * IterPerFrame));
    }
#endif
    
#if 0
    // do the time-reversal (for debugging)
    tmp=positions; positions=newPositions; newPositions=tmp;
    
    for (i=0; i<NumFrames; i++) {
	printf(" %d", i);
	fflush(stdout);
	if ((i & 15) == 15)
	    printf("\n");
	oneDynamicsFrame(part, IterPerFrame,
			 averagePositions, &oldPositions, &newPositions, &positions, force);
	snapshot(OutputFile, i, averagePositions);
    }
#endif
    
    writeOutputTrailer(OutputFile, part, NumFrames);
    
    free(averagePositions);
    free(oldPositions);
    free(newPositions);
    free(positions);
    free(force);
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
