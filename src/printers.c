
// routines to handle printing to the trace file.

#include "simulator.h"

#if 0

void pv(FILE *f, struct xyz foo) {
    fprintf(f, "(%.2f, %.2f, %.2f)",foo.x, foo.y, foo.z);
}
void pvt(FILE *f, struct xyz foo) {
    fprintf(f, "(%.2f, %.2f, %.2f)\n",foo.x, foo.y, foo.z);
}

void pa(FILE *f, int i) {
    int j, b, ba;
    double v;
	
    if (i<0 || i>=Nexatom) fprintf(f, "bad atom number %d\n",i);
    else {
	fprintf(f, "atom %s%d (%d bonds): ", periodicTable[atom[i].elt].symbol, i, atom[i].nbonds);
	for (j=0; j<atom[i].nbonds; j++) {
	    b=atom[i].bonds[j];
	    ba=(i==bond[b].an1 ? bond[b].an2 : bond[b].an1);
	    fprintf(f, "[%d/%d]: %s%d, ", b, bond[b].order,
		      periodicTable[atom[ba].elt].symbol, ba);
	}
	v=vlen(vdif(Positions[i],OldPositions[i]));
	fprintf(f, "\n   V=%.2f, mV^2=%.6f, pos=", v,1e-4*v*v/atom[i].massacc);
	pv(f, Positions[i]);
        fprintf(f, " oldpos=");
        pv(f, OldPositions[i]);
        fprintf(f, " force=");
	pvt(f, Force[i]);
	fprintf(f, "   mass = %f, massacc=%e\n", periodicTable[atom[i].elt].mass,
	       atom[i].massacc);
    }
}

static void printAllAtoms(FILE *f) 
{
    int i;
    for (i=0; i<Nexatom; i++) {
        pa(f, i);
    }
}

void pb(FILE *f, int i) {
    double len;
    struct bondStretch *bt;
    int index;
	
    if (i<0 || i>=Nexbon) fprintf(f, "bad bond number %d\n",i);
    else {
	bt = bond[i].type;
	len = vlen(vdif(Positions[bond[i].an1],Positions[bond[i].an2]));
	fprintf(f, "bond %d[%d] [%s%d(%d)-%s%d(%d)]: length %.1f\n",
		  i, bond[i].order,
		  periodicTable[atom[bond[i].an1].elt].symbol, bond[i].an1, atom[bond[i].an1].elt,
		  periodicTable[atom[bond[i].an2].elt].symbol, bond[i].an2, atom[bond[i].an2].elt,
		  len);
	index=(int)((len*len)-bt->table.start)/bt->table.scale;
	if (index<0 || index>=TABLEN)
	    fprintf(f, "r0=%.1f, index=%d of %d, off table\n",  bt->r0, index, TABLEN);
	else fprintf(f, "r0=%.1f, index=%d of %d, value %f\n", bt->r0, index, TABLEN,
		       bt->table.t1[index] + len*len*bt->table.t2[index]);
    }
}

void printAllBonds(FILE *f) 
{
    int i;
    for (i=0; i<Nexbon; i++) {
        pb(f, i);
    }
}

static void min_debug(char *label, double rms, int frameNumber) 
{
    fprintf(stderr, "---------------- %s -- frame %d\nrms: %f\n", label, frameNumber, rms);
    printAllAtoms(stderr);
    printAllBonds(stderr);
}

void checkatom(FILE *f, int i) {
    int j, b, ba;
    double v;
	
    if (i<0 || i>=Nexatom) fprintf(f, "bad atom number %d\n",i);
    else if (atom[i].elt < 0 || atom[i].elt > MAX_ELEMENT)
	fprintf(f, "bad element in atom %d: %d\n", i, atom[i].elt);
    else if (atom[i].nbonds <0 || atom[i].nbonds >NBONDS)
	fprintf(f, "bad nbonds in atom %d: %d\n", i, atom[i].nbonds);
    else for (j=0; j<atom[i].nbonds; j++) {
	b=atom[i].bonds[j];
	if (b < 0 || b >= Nexbon)
	    fprintf(f, "bad bonds number in atom %d: %d\n", i, b);
	else if (i != bond[b].an1 && i != bond[b].an2) {
	    fprintf(f, "bond %d of atom %d [%d] doesn't point back\n", j, i, b);
	    exit(0);
	}
    }
}


void pq(FILE *f, int i) {
    struct xyz r1, r2;
    if (i<0 || i>=Nextorq) fprintf(f, "bad torq number %d\n",i);
    else {
	fprintf(f, "torq %s%d-%s%d-%s%d, that's %d-%d=%d-%d\n",
		  periodicTable[atom[torq[i].a1].elt].symbol, torq[i].a1,
		  periodicTable[atom[torq[i].ac].elt].symbol, torq[i].ac,
		  periodicTable[atom[torq[i].a2].elt].symbol, torq[i].a2,
		  (torq[i].dir1 ? torq[i].b1->an2 :  torq[i].b1->an1),
		  (torq[i].dir1 ? torq[i].b1->an1 :  torq[i].b1->an2),
		  (torq[i].dir2 ? torq[i].b2->an1 :  torq[i].b2->an2),
		  (torq[i].dir2 ? torq[i].b2->an2 :  torq[i].b2->an1));
		
	r1=vdif(Positions[torq[i].a1],Positions[torq[i].ac]);
	r2=vdif(Positions[torq[i].a2],Positions[torq[i].ac]);
	fprintf(f, "r1= %.1f, r2= %.1f, theta=%.2f (%.0f)\n",
		  vlen(r1), vlen(r2), vang(r1, r2),
		  (180.0/3.1415)*vang(r1, r2));
	fprintf(f, " theta0=%f, Kb=%f, Ks=%f\n",torq[i].type->theta0, torq[i].type->kb,
	       torq[i].type->kb/(vlen(r1) * vlen(r2)));
    }
}

void pcon(FILE *f, int i) {
    struct MOT *mot;
    int j;
	
    if (i<0 || i>=Nexcon) {
	fprintf(f, "Bad constraint number %d\n",i);
	return;
    }
    fprintf(f, "Constraint %d: ",i);

    switch (Constraint[i].type) {
	case CODEground: 
	fprintf(f, "Ground:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEtemp:
	fprintf(f, "Thermometer %s:\n atoms ",Constraint[i].name);
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEstat:
	fprintf(f, "Thermostat %s (%f):\n atoms ",
	       Constraint[i].name,Constraint[i].data);
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEbearing:
	fprintf(f, "Bearing:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODElmotor:
	fprintf(f, "Linear motor:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEspring:
	fprintf(f, "Spring:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEslider:
	fprintf(f, "Slider:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEmotor:
	mot = Constraint[i].motor;
	fprintf(f, "motor; stall torque %.2e, unloaded speed %.2e\n center ",
		  mot->stall, mot->speed);
	pv(f, mot->center);
	fprintf(f, " axis ");
	pvt(f, mot->axis);
		
	fprintf(f, " rot basis ");
	pv(f, mot->roty);
        pv(f, mot->rotz);
	fprintf(f, " angles %.0f, %.0f, %.0f\n",
		  180.0*vang(mot->axis,mot->roty)/Pi,
		  180.0*vang(mot->rotz,mot->roty)/Pi,
		  180.0*vang(mot->axis,mot->rotz)/Pi);
		
	for (j=0;j<Constraint[i].natoms;j++) {
	    fprintf(f, " atom %d radius %.1f angle %.2f\n   center ",
		      Constraint[i].atoms[j], mot->radius[j], mot->atang[j]);
	    pv(f, mot->atocent[j]);
	    fprintf(f, " posn ");
            pvt(f, mot->ator[j]);
	}
	fprintf(f, " Theta=%.2f, theta0=%.2f, moment factor =%e\n",
		  mot->theta, mot->theta0, mot->moment);
	break;
    case CODEangle:   
	fprintf(f, "Angle meter %s:\n atoms ",Constraint[i].name);
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEradius:  
	fprintf(f, "radius measure %s:\n atoms ",Constraint[i].name);
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    }
}
#endif

static int
countOutputColumns(struct jig *j)
{
    switch (j->type) {
    case RotaryMotor:
        return 2;
    case Ground:
    case Thermometer:
    case AngleMeter:
    case RadiusMeter:
    case Thermostat:
    case LinearMotor:
        return 1;
    default:
        return 0;
    }
}

void traceHeader(FILE *f, char *inputFileName, char *outputFileName, char *traceFileName, 
                 struct part *part, int numFrames, int stepsPerFrame, double temperature)
{
    int i, ncols;
    struct jig *j;
    struct tm *ptr;
    time_t tm;
    tm = time(NULL);
    ptr = localtime(&tm);
    
    fprintf(f, "# nanoENGINEER-1.com Simulator Trace File, Version 050310\n");
    fprintf(f, "#\n");
    fprintf(f, "# Date and Time: %s", asctime(ptr));
    fprintf(f, "# Input File:%s\n", inputFileName);
    fprintf(f, "# Output File: %s\n", outputFileName);
    fprintf(f, "# Trace File: %s\n", traceFileName);
    fprintf(f, "# Number of Atoms: %d\n", part->num_atoms);

    if (IDKey != NULL && IDKey[0] != '\0') {
        fprintf(f, "# IDKey: %s\n", IDKey);
    }
    fprintf(f, "# Number of Frames: %d\n", numFrames);
    fprintf(f, "# Steps per Frame: %d\n", stepsPerFrame);
    fprintf(f, "# Temperature: %.1f\n", temperature);
    fprintf(f, "# \n");
    
    ncols = 0;
    
    for (i=0; i<part->num_jigs; i++) {
        ncols += countOutputColumns(part->jigs[i]);
    }
        
    fprintf(f, "# %d columns:\n", ncols);
    
    for (i=0; i<part->num_jigs; i++) {
        j = part->jigs[i];
        switch (j->type) {

        case AngleMeter:
            fprintf(f, "# %s: angle (radians)\n", j->name); 
            break;

        case RadiusMeter:
            fprintf(f, "# %s: distance (pm)\n", j->name); 
            break;
       
        case Ground:
            fprintf(f, "# %s: torque (nn-nm)\n", j->name); 
            break;
                    
        case Thermometer:
            fprintf(f, "# %s: temperature (K)\n", j->name);
            break;
                    
        case Thermostat:
            fprintf(f, "# %s: energy added (zJ)\n", j->name);
            break;

        case LinearMotor:
            fprintf(f, "# %s: displacement (pm)\n", j->name);
            break;
               
        case RotaryMotor:
            fprintf(f, "# %s: speed (GHz)\n", j->name);
            fprintf(f, "# %s: torque (nn-nm)\n", j->name);
            break;
        }
    }    
    fprintf(f, "#\n");
}

void traceJigHeader(FILE *f, struct part *part) {
    struct jig *j;
    int i;
    int ncol;

    fprintf(f, "#     Time ");
    for (i=0; i<part->num_jigs; i++) {
        j = part->jigs[i];
        
	j->data=0.0;
	j->data2=0.0;
	vsetc(j->xdata,0.0);

        switch (j->type) {
        case Ground:      fprintf(f, "Anchor  "); break;
        case Thermometer: fprintf(f, "T.meter "); break;
        case AngleMeter:  fprintf(f, "Angle   "); break;
        case RadiusMeter: fprintf(f, "Radius  "); break;
        case Thermostat:  fprintf(f, "T.stat  "); break;
        case LinearMotor: fprintf(f, "Lmotor  "); break;
        case RotaryMotor: fprintf(f, "sped Motor torq ");
	}
    }
    fprintf(f, "\n#  picosec ");

    for (i=0; i<part->num_jigs; i++) {
        j = part->jigs[i];
        ncol = countOutputColumns(j);
        if (ncol > 0) {
            fprintf(f, "%-8.8s", j->name);
            while (ncol-- > 1) {
                fprintf(f, "        ");
            }
        }
    }
    fprintf(f, "\n#\n");
}


void traceJigData(FILE *f, struct part *part) {
    double x;
    int i;
    struct jig *j;

    fprintf(f, "%10.4f ", Iteration * Dt / PICOSEC);
    
    for (i=0; i<part->num_jigs; i++) {
        j = part->jigs[i];
        switch (j->type) {
        case AngleMeter:
	    fprintf(f, "%8.5f", j->data);
	    break;
        case Ground:
	    x=vlen(j->xdata)/1e4;
	    fprintf(f, "%8.2f", x / j->data);
	    j->data=0.0;
	    vsetc(j->xdata, 0.0);
	    break;
        case Thermometer:
        case RadiusMeter:
        case Thermostat:
        case LinearMotor:
	    fprintf(f, "%8.2f", j->data);
	    j->data = 0.0;
	    break;
        case RotaryMotor:
	    fprintf(f, "%8.3f%8.3f", j->data/(Dt*2e9*Pi),
		    j->data2/((1e-9/Dx)*(1e-9/Dx)));
	    j->data = 0.0;
	    j->data2 = 0.0;
	    break;
	}
    }
    fprintf(f, "\n"); // each snapshot is one line
}

void
printError(FILE *f, const char *file, int line, const char *err_or_warn,
	   int doPerror, const char *format, ...)
{
  va_list args;
  char *err;
  
  if (doPerror) {
      err = strerror(errno);
  }

  fprintf(stderr, "%s at %s:%d: ", err_or_warn, file, line);
  va_start(args, format);
  vfprintf(stderr, format, args);
  va_end(args);
  if (doPerror) {
      fprintf(stderr, ": %s\n", err);
  } else {
      fprintf(stderr, "\n");
  }

  if (f == NULL) {
      return;
  }

  fprintf(f, "# %s: ", err_or_warn);
  va_start(args, format);
  vfprintf(f, format, args);
  va_end(args);
  if (doPerror) {
      fprintf(f, ": %s\n", err);
  } else {
      fprintf(f, "\n");
  }
}

void
doneExit(int exitvalue, FILE *f, const char *format, ...)
{
    va_list args;

    if (f != NULL) {
        fprintf(f, "# Done: ");
        va_start(args, format);
        vfprintf(f, format, args);
        va_end(args);
        fprintf(f, "\n");
    }
    
    exit(exitvalue);
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
