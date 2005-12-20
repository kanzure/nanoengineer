#include "simulator.h"

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

static void
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
    
    iters = max(iters,1);

    deltaTframe = 1.0/iters;
	
    for (j=0; j<part->num_atoms; j++) {
	vsetc(averagePositions[j],0.0);
    }
	
    for (loop=0; loop<iters && !Interrupted; loop++) {
		
	Iteration++;

        updateVanDerWaals(part, NULL, positions);
	calculateGradient(part, positions, force);

        /* first, for each atom, find non-accelerated new pos  */
        /* Atom moved from oldPositions to positions last time,
           now we move it the same amount from positions to newPositions */
        for (j=0; j<part->num_atoms; j++) {
            vsub2(f,positions[j],oldPositions[j]);
            vadd2(newPositions[j],positions[j],f);
        }
		
	// pre-force jigs
	for (j=0;j<part->num_jigs;j++) {	/* for each jig */
          jig = part->jigs[j];
          switch (jig->type) {
          case RotaryMotor:
            jigMotorPreforce(jig, positions, force, deltaTframe);
            break;
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
	    /*
	      ff=vlen(force[j]);
	      fprintf(stderr, "--> Total force on atom %d is %.2f, displacement %f\n", j,
	      ff, ff*atom[j].massacc);
	    */
	    vmul2c(f,force[j],part->atoms[j]->inverseMass); // inverseMass = Dt*Dt/mass
				
	    if (vlen(f)>15.0) {
		fprintf(stderr, "High force %.2f in iteration %d\n",vlen(f), Iteration);
                printAtom(stderr, part, part->atoms[j]);
	    }
				
	    vadd(newPositions[j],f);
	    vadd(averagePositions[j],newPositions[j]);
				
	    vsub2(f, newPositions[j], positions[j]);
	    //ff = vdot(f, f);
	    //FoundKE += atom[j].energ * ff;
	}

	    
	/* now the jigs */
	for (j=0;j<part->num_jigs;j++) {	/* for each jig */
          jig = part->jigs[j];

          switch (jig->type) {
          case Ground:
            jigGround(jig, deltaTframe, positions, newPositions, force);
            break;
          case RotaryMotor:
            jigMotor(jig, deltaTframe, positions, newPositions, force);
            break;
          case Thermometer:
            jigThermometer(jig, deltaTframe, positions, newPositions);
            break;
          case Thermostat:
            jigThermostat(jig, deltaTframe, positions, newPositions);
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
          case LinearMotor:
            break; // handled in preforce above
          }
	}
			
	tmp=oldPositions; oldPositions=positions; positions=newPositions; newPositions=tmp;
    }
	
    for (j=0; j<part->num_atoms; j++) {
	vmulc(averagePositions[j],deltaTframe);
    }
    *pOldPositions = oldPositions;
    *pNewPositions = newPositions;
    *pPositions = positions;
}

void
dynamicsMovie(struct part *part)
{
  struct xyz *averagePositions = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
  struct xyz *oldPositions = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
  struct xyz *newPositions = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
  struct xyz *positions =  (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
  struct xyz *force = (struct xyz *)allocate(sizeof(struct xyz) * part->num_atoms);
  int i;
  
  for (i=0; i<part->num_atoms; i++) {
    vset(positions[i], part->positions[i]);
    vsub2(oldPositions[i], positions[i], part->velocities[i]);
  }
        
  for (i=0; i<NumFrames; i++) {
    if (PrintFrameNums) printf(" %d", i);
    fflush(stdout);
    if ((i & 15) == 15)
      if (PrintFrameNums) printf("\n");
    oneDynamicsFrame(part, IterPerFrame,
                     averagePositions, &oldPositions, &newPositions, &positions, force);
    writeDynamicsMovieFrame(outf, i, part, averagePositions);
  }
  if (PrintFrameNums) printf("\n");

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
    snapshot(outf, i, averagePositions);
  }
#endif
  
  writeOutputTrailer(outf, part, NumFrames);

  free(averagePositions);
  free(oldPositions);
  free(newPositions);
  free(positions);
  free(force);
}
