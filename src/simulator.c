// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.

#include "simulator.h"

int debug_flags = 0;

int Interrupted = 0; /* set to 1 when a SIGTERM is received */

/** indicate next avail/total number of stretch bonds, bend bonds, and atoms */
int Nexbon=0, Nextorq=0, Nexatom=0;

/** positions and forces on the atoms */
// units for positions are 1e-12 meters == picometers
// units for force are piconewtons
struct xyz Force[NATOMS];
struct xyz OldForce[NATOMS]; /* used in minimize */
struct xyz AveragePositions[NATOMS];
static struct xyz position_arrays[4*NATOMS];

// these point into position_arrays
struct xyz *OldPositions, *NewPositions, *Positions, *BestPositions; 

// steepest descent terminates when rms_force is below this value (in picoNewtons)
#define RMS_CUTOVER (50.0)
/* additionally, sqrt(max_forceSquared) must be less than this: */
#define MAX_CUTOVER (RMS_CUTOVER * 3.0)
#define MAX_CUTOVER_SQUARED (MAX_CUTOVER * MAX_CUTOVER)

// conjugate gradient terminates when rms_force is below this value (in picoNewtons)
#define RMS_FINAL (1.0)

/* we save the rms value from the initialization iterations in minimize() here: */
static float initial_rms;
/* and terminate minimization if rms ever gets above this: */
#define MAX_RMS (1000.0 * initial_rms)

struct xyz Center, Bbox[2];

struct A atom[NATOMS];

struct B bond[4*NATOMS];

struct Q torq[6*NATOMS];


int Iteration=0;

double RvdW, EvdW;

struct vdWbuf *Nexvanbuf, *Dynobuf;
int Dynoix;			/* start of dynamically found vdw's */

/** A space grid for locating non-bonded interactions */

struct A *Space[SPWIDTH][SPWIDTH][SPWIDTH];	/*  space buckets */

static void orion(struct xyz *position) {            /* atoms in space :-) */
    int n, i,j,k;
    struct A **pail;

    for (n=0; n<Nexatom; n++) *atom[n].bucket = NULL;
	
    for (n=0; n<Nexatom; n++) {
	i= ((int)position[n].x / 250) & SPMASK;
	j= ((int)position[n].y / 250) & SPMASK;
	k= ((int)position[n].z / 250) & SPMASK;

	pail = &Space[i][j][k];
	atom[n].next = *pail;
	*pail = atom+n;
	atom[n].bucket = pail;
    }

}


/** constraints */

int Nexcon=0;

struct AXLE Constraint[100];


/** motors: shoot for 5 nN/atom? speeds up to 10 m/s */

int Nexmot=0;

struct MOT Motor[100];




/** constants: timestep (.1 femtosecond), scale of distance (picometers) */
double Dt= 1e-16, Dx=1e-12;
double Dmass = 1e-27;           // units of mass vs. kg
double Temperature = 300.0;	/* Kelvins */
double Boltz = 1.38e-23;	/* k, in J/K */

double TotalKE = 0.0;		 /* actually double, = m_i v_i^2 */
double FoundKE = 0.0;

double Pi = 3.1415926;

/* values are for carbon and carbon-carbon bond (for testing) */

/** stiffnesses are in N/m, so forces come out in pN (i.e. Dx N) */
double Kb=28.63;		/* N/m */
double Ks=440.0;		/* N/m */
double De=0.556, Beta = 1.989e-2; /* Morse params */

//NB depends on Dx
double Tq = 1e-3;            // since torques are given in pN*nm,
     // force(pN) = Tq(Dx/nm)*torque(pN*nm)/r(Dx)

/** pN/kg => acc in pm/s^2; mult by Dt^2 (folded into massacc) */

double R0 = 152.3, R1 = 152.3, Theta0 = 1.911;

/** global properties: center of mass, momentum, moment of rotation */
double totMass=0.0;
struct xyz Cog, P, Omega;

double totClipped=0.0;  // internal thermostat for numerical stability

double Gamma = 0.01; // for Langevin thermostats
//double Gamma = 0.1; // for Langevin thermostats
// double G1=(1.01-0.27*Gamma)*1.4*sqrt(Gamma);
double G1=(1.01-0.27*0.01)*1.4*0.1;
//double G1=(1.01-0.27*0.1)*1.4*0.31623;

// definitions for command line args

int ToMinimize=0;
int IterPerFrame=10;
int NumFrames=100;
int DumpAsText=0;
int DumpIntermediateText=0;
int PrintFrameNums=1;
int OutputFormat=1;
int KeyRecordInterval=32;
char *IDKey="";

char OutFileName[1024];
char TraceFileName[1024];

// for writing the differential position and trace files
FILE *outf, *tracef;

/** kT @ 300K is 4.14 zJ -- RMS V of carbon is 1117 m/s
    or 645 m/s each dimension, or 0.645 pm/fs  */

double gavss(double v) {
    double v0,v1, rSquared;
    do {
	v0=(float)rand()/(float)(RAND_MAX/2) - 1.0;
	v1=(float)rand()/(float)(RAND_MAX/2) - 1.0;
	rSquared = v0*v0 + v1*v1;
    } while (rSquared>=1.0 || rSquared==0.0);
    return v*v0*sqrt(-2.0*log(rSquared)/rSquared);
}

struct xyz gxyz(double v) {
    struct xyz g;
    g.x=gavss(v);
    g.y=gavss(v);
    g.z=gavss(v);
    return g;
}

struct xyz sxyz(double *v) {
    struct xyz g;
    g.x=v[0];
    g.y=v[1];
    g.z=v[2];
    return g;
}

static int isbonded(int a1, int a2) {
    int j, b, ba;
	for (j=0; j<atom[a1].nbonds; j++) {
	    b=atom[a1].bonds[j];
	    ba=(a1==bond[b].an1 ? bond[b].an2 : bond[b].an1);
	    if (ba==a2) return 1;
	}
	return 0;
}
    

int Count = 0;

void findnobo(struct xyz *position, int a1) {
    int a2, ix, iy, iz, i, j, k;
    struct A *p;
    double r;

    // fprintf(stderr, "find nobo for %d\n",a1);
	
    ix= (int)position[a1].x / 250 + 4;
    iy= (int)position[a1].y / 250 + 4;
    iz= (int)position[a1].z / 250 + 4;

    for (i=ix-7; i<ix; i++)
	for (j=iy-7; j<iy; j++)
	    for (k=iz-7; k<iz; k++)
		for (p=Space[i&SPMASK][j&SPMASK][k&SPMASK]; p; p=p->next) {
		    a2 = p-atom;
		    if (a2>a1 
			// && (ToMinimize || atom[a1].part != atom[a2].part)
			&& !isbonded(a1,a2)) {
			r=vlen(vdif(position[a1],position[a2]));
			if (r<800.0) {
			    // fprintf(stderr, "  found nobo for %d<-->%d\n",a1, a2);
			    makvdw(a1, a2);
			    Count++;
			}
		    }
		}
}

// center of mass

static struct xyz CoM(struct xyz *list) {
    int i,j, k;
    double x, y, z;
    struct xyz c, rx;

    vsetc(c,0.0);
    for (j=0; j<Nexatom; j++) {
	rx=vprodc(list[j],periodicTable[atom[j].elt].mass);
	vadd(c,rx);
    }
    vmulc(c,Dmass/totMass);
    return c;
}


// total kinetic energy over k
static double totKE() {
    int i,j, k;
    double a,b,c;
    struct xyz f, v1, v2, rx;

    c=0.0;
    for (j=0; j<Nexatom; j++) {
        rx=vdif(Positions[j], OldPositions[j]);
        a=vdot(rx,rx)*Dx*Dx/(Dt*Dt);
        a *= periodicTable[atom[j].elt].mass * 1e-27/ Boltz;
        c += a;
    }
    return c;
}

/*
  inputs:
    position[*]
    bond[*].an1, .an2, .type
    torq[*].dir1, .dir2, .b1, .b2, .kb1, .kb2
    
  changes:
    finds non-bonded interacting atoms using orion()
    force[*] contains accumulated force on atom
    bond[*].r = vector from bond[*].an1 to bond[*].an2 (delta of positions)
    bond[*].invlen = 1/|r|
    bond[*].ru = unit vector along r
*/
static void calculateForces(int doOrion, struct xyz *position, struct xyz *force)
{
    int j, k;
    struct xyz f;
    double rSquared;
    double ff;
    double fac;
    struct xyz v1;
    struct xyz v2;
    double z;
    double m;
    struct xyz q1;
    struct xyz q2;
    struct vdWbuf *nvb;

    /* interpolation */
    double *t1;
    double *t2;
    double start;
    int scale;

    if (doOrion) {
        /* find the non-bonded interactions */
        orion(position);
		
        Nexvanbuf=Dynobuf;
        Nexvanbuf->fill = Dynoix;
        Count = 0;
		
        for (j=0; j<Nexatom; j++) {
            findnobo(position, j);
        }
    }		
			
    /* clear force vectors */
    for (j=0; j<Nexatom; j++) {
        vsetc(force[j],0.0);
    }
			
    /* compute stretch force for each bond, accumulating in force[atom] */
    for (j=0; j<Nexbon; j++) {
        vsub2(bond[j].r, position[bond[j].an1], position[bond[j].an2]);
        vset(f,bond[j].r);
        rSquared = vdot(f,f);
				
        /* while we're at it, set unit bond vector and clear bend force */
        ff = 1.0/sqrt(rSquared); /* XXX if atoms are on top of each other, 1/0 !! */
        bond[j].invlen = ff;
        vmul2c(bond[j].ru,f,ff); /* unit vector along r */
        //vsetc(bond[j].bff,0.0);
				
        /* table setup for stretch, to be moved out of loop */
        start=bond[j].type->table.start;
        scale=bond[j].type->table.scale;
        t1=bond[j].type->table.t1;
        t2=bond[j].type->table.t2;
				
        k=(int)(rSquared-start)/scale;
        if (k<0) {
					
            if (!ToMinimize && DEBUG(D_TABLE_BOUNDS)) { //linear
                fprintf(stderr, "stretch: low --");
                pb(stderr, j);
            }
            fac=t1[0]+rSquared*t2[0];
        }
        else if (k>=TABLEN) {
					
            // fprintf(stderr, "stretch: high --");
            // pb(stderr, j);
            if (ToMinimize)  //flat
                fac = t1[TABLEN-1]+((TABLEN-1)*scale+start)*t2[TABLEN-1];
            else fac=0.0;
        }
        else fac=t1[k]+rSquared*t2[k];
        // table lookup equivalent to: fac=lippmor(rSquared)
            
        // vmul2c(bond[j].aff,f,fac);
        vmul2c(f,f,fac);  // f = r * lippmor(rSquared)
        vadd(force[bond[j].an1],f);
        vsub(force[bond[j].an2],f);
        //fprintf(stderr, "length %f, force %f \n", vlen(bond[j].r), sqrt(vdot(f,f)));
        //fprintf(stderr, "inverse length %f \n", bond[j].invlen);
				
    }
			
    /* now the forces for each bend */
			
    for (j=0; j<Nextorq; j++) {

        // v1, v2 are the unit vectors FROM the central atom TO the neighbors
        if (torq[j].dir1) {vsetn(v1,torq[j].b1->ru);}
        else {vset(v1,torq[j].b1->ru);}
        if (torq[j].dir2) {vsetn(v2,torq[j].b2->ru);}
        else {vset(v2,torq[j].b2->ru);}

        z = vdot(v1,v2); // = cos(theta)
        m = torq[j].type->kb * (torq[j].type->cosTheta0 - z);
        vmul2c(q1, v1, z);
        vmul2c(q2, v2, z);
        vsub(q1, v2);
        vsub(q2, v1);
        vmulc(q1, m * torq[j].b1->invlen);
        vmulc(q2, m * torq[j].b2->invlen);
		    
        /*
		
        // v1, v2 are the vectors FROM the central atom TO the neighbors
        if (torq[j].dir1) {vsetn(v1,torq[j].b1->r);}
        else {vset(v1,torq[j].b1->r);}
        if (torq[j].dir2) {vsetn(v2,torq[j].b2->r);}
        else {vset(v2,torq[j].b2->r);}
				
        // z = 1.0/sqrt(vdot(v1,v1)*vdot(v2,v2));
        z = torq[j].b1->invlen * torq[j].b2->invlen;
        theta = acos(vdot(v1, v2)*z);

        v2x(foo, v1, v2);
        foo=uvec(foo);
        q1=uvec(vx(v1, foo));
        q2=uvec(vx(foo, v2));
		
        ff = (theta - torq[j].theta0) * torq[j].kb1 * torq[j].b1->invlen;
        vmulc(q1,ff);
        ff = (theta - torq[j].theta0) * torq[j].kb2 * torq[j].b2->invlen;
        vmulc(q2,ff);
        */

		
		
        vadd(force[torq[j].ac],q1);
        vsub(force[torq[j].a1],q1);
        vadd(force[torq[j].ac],q2);
        vsub(force[torq[j].a2],q2);
        /*
          fprintf(stderr, "dtheta %f, torq %f \n",theta - torq[j].theta0, 
          sqrt(vdot(q1,q1)));
        */
    }

    // fprintf(stderr, "about to do vdw loop\n");
    /* do the van der Waals/London forces */
    for (nvb=&vanderRoot; nvb; nvb=nvb->next) {
        for (j=0; j<nvb->fill; j++) {
            // fprintf(stderr, "in vdw loop\n");
            vsub2(f, position[nvb->item[j].a1], position[nvb->item[j].a2]);
            rSquared = vdot(f,f);
					
            if (rSquared>50.0*700.0*700.0 && DEBUG(D_TABLE_BOUNDS)) {
                fprintf(stderr, "hi vdw: %f\n", sqrt(rSquared));
                pvdw(stderr, nvb,j);
                pa(stderr, nvb->item[j].a1);
                pa(stderr, nvb->item[j].a2);
            }
					
            /*
              fprintf(stderr, "Processing vdW %d/%d: atoms %d-%d, r=%f\n",
              nvb-&vanderRoot, j,nvb->item[j].a1, nvb->item[j].a2,
              sqrt(rSquared));
            */
            /* table setup  */
            start=nvb->item[j].table->start;
            scale=nvb->item[j].table->scale;
            t1=nvb->item[j].table->t1;
            t2=nvb->item[j].table->t2;
					
            k=(int)(rSquared-start)/scale;
            if (k<0) {
                if (!ToMinimize && DEBUG(D_TABLE_BOUNDS)) { //linear
                    fprintf(stderr, "vdW: off table low -- r=%.2f \n",  sqrt(rSquared));
                    pvdw(stderr, nvb,j);
                }
                k=0;
                fac=t1[k]+rSquared*t2[k];
            }
            else if (k>=TABLEN) {
                /*
                  fprintf(stderr, "vdW: off table high -- %d/%d: start=%.2f, scale=%d\n",
                  k,TABLEN, start, scale);
                */
                fac = 0.0;
            }
            else fac=t1[k]+rSquared*t2[k];
            vmulc(f,fac);
            vadd(force[nvb->item[j].a1],f);
            vsub(force[nvb->item[j].a2],f);
        }
    }
}

static void
jigMotorPreforce(int j, struct xyz *position, double deltaTframe)
{
    struct MOT *mot;
    int n;
    struct xyz rx;
    int k;
    double ff;
    int a1;
    double theta;
    struct xyz f;

    mot=Constraint[j].motor;

    if (mot->speed==0.0) { // just add torque to force

        // set the center of torque each time
        n=Constraint[j].natoms;
        vsetc(rx, 0.0);
        for (k=0; k<n; k++) {
            vadd(rx,position[Constraint[j].atoms[k]]);
        }
        vmulc(rx,1.0/(double)n);
        mot->center = rx;

        ff = Tq*mot->stall/n;
        for (k=0; k<n; k++) {
            a1 = Constraint[j].atoms[k];
            rx = vdif(position[a1],mot->center);
            f  = vprodc(vx(mot->axis,uvec(rx)),ff/vlen(rx));
			    
            //fprintf(stderr, "applying torque %f to %d: other force %f\n",
            //       vlen(f), a1, vlen(Force[a1]));

            vadd(Force[a1],f);
        }
        // data for printing speed trace
        Constraint[j].temp = mot->stall; // torque

        rx=uvec(vdif(position[Constraint[j].atoms[0]],mot->center));
			
        theta = atan2(vdot(rx,mot->rotz),vdot(rx,mot->roty));
        /* update the motor's position */
        if (theta>Pi) {
            mot->theta0 = mot->theta-2.0*Pi;
            mot->theta = theta-2.0*Pi;
        }
        else {
            mot->theta0 = mot->theta;
            mot->theta = theta;
        }
        theta = mot->theta - mot->theta0;

        Constraint[j].data += theta * deltaTframe;
    }
}

static void
jigGround(int j, double deltaTframe, struct xyz *position, struct xyz *new_position)
{
    struct xyz foo, bar;
    struct xyz q1;
    int k;
    struct xyz rx;

    vsetc(foo,0.0);
    vsetc(q1,0.0);
    for (k=0; k<Constraint[j].natoms; k++) { // find center
        vadd(foo,position[Constraint[j].atoms[k]]);
    }
    vmulc(foo,1.0/Constraint[j].natoms);

    for (k=0; k<Constraint[j].natoms; k++) {
        vsub2(rx,position[Constraint[j].atoms[k]], foo);
        v2x(bar,rx,Force[Constraint[j].atoms[k]]); // bar = rx cross Force[]
        vadd(q1,bar);
    }
    vmulc(q1,deltaTframe);
    vadd(Constraint[j].xdata, q1);
    Constraint[j].data++;

    for (k=0; k<Constraint[j].natoms; k++) {
        new_position[Constraint[j].atoms[k]] = position[Constraint[j].atoms[k]];
    }
}

static void
jigMotor(int j, double deltaTframe, struct xyz *position, struct xyz *new_position)
{
    struct MOT *mot;
    double sum_torque;
    int k;
    int a1;
    struct xyz rx;
    struct xyz f;
    double ff;
    double omega;
    double motorq;
    double theta;
    double z;
    struct xyz v1, v2;

    mot=Constraint[j].motor;

    if (mot->speed != 0.0) {
        sum_torque = 0.0;
					
        /* input torque due to forces on each atom */
        for (k=0; k<Constraint[j].natoms; k++) {
            a1 = Constraint[j].atoms[k];
            rx = vdif(position[a1],mot->atocent[j]);
            f = vx(rx,Force[a1]);
            ff = vdot(f, mot->axis);
            sum_torque += ff;
        }
		    
        //fprintf(stderr, "*** input torque %f\n", sum_torque);

        omega = mot->theta - mot->theta0;
        motorq = mot->stall - omega*mot->stall/(mot->speed);
        theta = mot->theta + omega +
            mot->moment*(motorq + sum_torque);
  
        /* theta_i+1 = 2theta_i - theta_i-1 + sum_torque + motorq
           motorq = stall - omega*(stall/speed)
           omega = (theta_i+1 - theta_i-1)/ 2Dt
           solve for theta_i+1 -- preserves Verlet reversibility  */
        /*
          z = mot->moment;
          m = - z * mot->stall / (2.0 *  mot->speed);
          theta = (2.0*mot->theta - (1.0+m)*mot->theta0 +
          z*(mot->stall + sum_torque))  / (1.0 - m);
        */

        // fprintf(stderr, "***  Theta = %f, %f, %f\n",
        //          theta*1e5, mot->theta*1e5, mot->theta0*1e5);
		    
        /* put atoms in their new places */
        for (k=0; k<Constraint[j].natoms; k++) {
            a1 = Constraint[j].atoms[k];
            z = theta + mot->atang[k];
            vmul2c(v1, mot->roty, mot->radius[k] * cos(z));
            vmul2c(v2, mot->rotz, mot->radius[k] * sin(z));
            vadd2(new_position[a1], v1, v2);
            vadd(new_position[a1], mot->atocent[k]);
        }
					
        /* update the motor's position */
        if (theta>Pi) {
            mot->theta0 = mot->theta-2.0*Pi;
            mot->theta = theta-2.0*Pi;
        }
        else {
            mot->theta0 = mot->theta;
            mot->theta = theta;
        }
        // data for printing speed trace
        Constraint[j].data += omega * deltaTframe;
        Constraint[j].temp += (motorq) * deltaTframe;
    }
}

static void
jigLinearMotor(int j, struct xyz *position, double deltaTframe)
{
    struct MOT *mot;
    int i, k;
    int a1;
    struct xyz r;
    struct xyz f;
    double ff, x;

    mot=Constraint[j].motor;

    if (mot->speed == 0.0) {
	for (i=0;i<Constraint[j].natoms;i++) 
	    vadd(Force[Constraint[j].atoms[i]], mot->center);
    }
    else {
	r = vcon(0.0);
	for (i=0;i<Constraint[j].natoms;i++) 
	    /* for each atom connected to the "shaft" */
	    r=vsum(r,Positions[Constraint[j].atoms[i]]);
	
	r=vprodc(r, 1.0/Constraint[j].natoms);
    	
	// x is length of projection of r onto axis
	x=vdot(r,mot->axis);
	
	// note .speed is stiffness
	// .theta0 is projection dist of r onto axis for 0 force
	ff = mot->speed * (mot->theta0 - x) / Constraint[j].natoms;
	f = vprodc(mot->axis, ff);

	for (i=0;i<Constraint[j].natoms;i++) 
	    vadd(Force[Constraint[j].atoms[i]], f);

    }
}

static void
jigThermometer(int j, double deltaTframe, struct xyz *position, struct xyz *new_position)
{
    double z;
    double ff;
    int a1;
    struct xyz f;

    z=deltaTframe/(3*(1+Constraint[j].atoms[1]-
                      Constraint[j].atoms[0]));
    ff=0.0;
    for (a1 = Constraint[j].atoms[0];
         a1 <= Constraint[j].atoms[1];
         a1++) {
        f = vdif(position[a1],new_position[a1]);
        ff += vdot(f, f)*periodicTable[atom[a1].elt].mass;
    }
    ff *= Dx*Dx/(Dt*Dt) * 1e-27 / Boltz;
    Constraint[j].data += ff*z;
}

// Langevin thermostat
static void
jigThermostat(int j, double deltaTframe, struct xyz *position, struct xyz *new_position)
{
    double z;
    double ke;
    int a1;
    double therm;
    struct xyz v1;
    struct xyz v2;
    double ff;

    z=deltaTframe/(3*(1+Constraint[j].atoms[1]-
                      Constraint[j].atoms[0]));
    ke=0.0;

    for (a1 = Constraint[j].atoms[0];
         a1 <= Constraint[j].atoms[1];
         a1++) {
        therm = sqrt((Boltz*Constraint[j].temp)/
                     (periodicTable[atom[a1].elt].mass * 1e-27))*Dt/Dx;
        v1 = vdif(new_position[a1],position[a1]);
        ff = vdot(v1, v1)*periodicTable[atom[a1].elt].mass;
        vmulc(v1,1.0-Gamma);
        v2= gxyz(G1*therm);
        vadd(v1, v2);
        vadd2(new_position[a1],position[a1],v1);

        // add up the energy
        ke += vdot(v1, v1)*periodicTable[atom[a1].elt].mass - ff;

    }
    ke *= 0.5 * Dx*Dx/(Dt*Dt) * 1e-27 * 1e18;
    Constraint[j].data += ke;
}

static void
jigAngle(int j, struct xyz *new_position)
{
    double z;
    struct xyz v1;
    struct xyz v2;

    // better have 3 atoms exactly
    vsub2(v1,new_position[Constraint[j].atoms[0]],
          new_position[Constraint[j].atoms[1]]);
    vsub2(v2,new_position[Constraint[j].atoms[2]],
          new_position[Constraint[j].atoms[1]]);
    z=acos(vdot(v1,v2)/(vlen(v1)*vlen(v2)));

    Constraint[j].data = z;
}


static void
jigRadius(int j, struct xyz *new_position)
{
    double z;
    struct xyz v1;

    // better have 2 atoms exactly
    vsub2(v1,new_position[Constraint[j].atoms[0]],
          new_position[Constraint[j].atoms[1]]);

    Constraint[j].data = vlen(v1);
}

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
*/
static void
calcloop(int iters) {
    int j;
    int loop;
    double deltaTframe;
    double ff;
    struct xyz f;
    struct xyz *tmp;
    
    iters = max(iters,1);

    deltaTframe = 1.0/iters;
	
    for (j=0; j<Nexatom; j++) {
	vsetc(AveragePositions[j],0.0);
    }
	
    for (loop=0; loop<iters && !Interrupted; loop++) {
		
	Iteration++;

	calculateForces(loop==0, Positions, Force);

        /* first, for each atom, find non-accelerated new pos  */
        /* Atom moved from OldPositions to Positions last time,
           now we move it the same amount from Positions to NewPositions */
        for (j=0; j<Nexatom; j++) {
            vsub2(f,Positions[j],OldPositions[j]);
            vadd2(NewPositions[j],Positions[j],f);
        }
		
	// pre-force constraints
	for (j=0;j<Nexcon;j++) {	/* for each constraint */
            switch (Constraint[j].type) {
            case CODEmotor:
                jigMotorPreforce(j, Positions, deltaTframe);
                break;
	    case CODElmotor:
		jigLinearMotor(j, Positions, deltaTframe);
                break;
	    }
	}
	
	/* convert forces to accelerations, giving new positions */
	FoundKE = 0.0;		/* and add up total KE */
	for (j=0; j<Nexatom; j++) {
	    /*
	      ff=vlen(Force[j]);
	      fprintf(stderr, "--> Total force on atom %d is %.2f, displacement %f\n", j,
	      ff, ff*atom[j].massacc);
	    */
	    vmul2c(f,Force[j],atom[j].massacc); // massacc = Dt*Dt/mass
				
	    if (vlen(f)>15.0) {
		fprintf(stderr, "High force %.2f in iteration %d\n",vlen(f), Iteration);
		pa(stderr, j);
	    }
				
	    vadd(NewPositions[j],f);
	    vadd(AveragePositions[j],NewPositions[j]);
				
	    vsub2(f, NewPositions[j], Positions[j]);
	    ff = vdot(f, f);
	    FoundKE += atom[j].energ * ff;
	}

	    
	/* now the constraints */
	for (j=0;j<Nexcon;j++) {	/* for each constraint */
            switch (Constraint[j].type) {
            case CODEground:
                jigGround(j, deltaTframe, Positions, NewPositions);
                break;
            case CODEmotor:
                jigMotor(j, deltaTframe, Positions, NewPositions);
                break;
            case CODEtemp:
                jigThermometer(j, deltaTframe, Positions, NewPositions);
                break;
            case CODEstat:
                jigThermostat(j, deltaTframe, Positions, NewPositions);
                break;
            case CODEangle:
                jigAngle(j, NewPositions);
                break;
            case CODEradius:
                jigRadius(j, NewPositions);
                break;
	    }
	}
			
	tmp=OldPositions; OldPositions=Positions; Positions=NewPositions; NewPositions=tmp;
    }
	
    for (j=0; j<Nexatom; j++) {
	vmulc(AveragePositions[j],deltaTframe);
    }
}


static int groundExists = 1;

static void
groundAtoms(struct xyz *oldPosition, struct xyz *newPosition) 
{
    int j, k;
    int foundAGround = 0;

    if (groundExists) {
	for (j=0;j<Nexcon;j++) {	/* for each constraint */
	    if (Constraint[j].type == CODEground) { /* welded to space */
                foundAGround = 1;
		for (k=0; k<Constraint[j].natoms; k++) {
		    newPosition[Constraint[j].atoms[k]] = oldPosition[Constraint[j].atoms[k]];
		}
	    }
        }
        groundExists = foundAGround ;
    }
}

// one entry for each of the four *Positions pointers
// indicates which of the four segments of position_arrays each points to
static int positionPointerSegment[4];
static float best_rms = 1e16;
static float best_max_forceSquared = 1e16;

#define PTR_OLD 0
#define PTR_CUR 1
#define PTR_NEW 2
#define PTR_BST 3


static void
setupPositionsArrays()
{
    OldPositions  = position_arrays           ;
    positionPointerSegment[PTR_OLD] = 0;
    Positions     = position_arrays +   NATOMS;
    positionPointerSegment[PTR_CUR] = 1;
    NewPositions  = position_arrays + 2*NATOMS;
    positionPointerSegment[PTR_NEW] = 2;
    BestPositions = OldPositions;
    positionPointerSegment[PTR_BST] = 0;
}

/* copy data from NewPositions to Positions,
   if rms < best_rms
     a copy of the data in the segment pointed to by best_ptr
     is placed in BestPositions 

   (actually swaps array pointers around instead of copying)
*/
static void
updatePositionsArrays(float rms, float max_forceSquared, int best_ptr)
{
    int i;
    int segmentUsed[4];

    if (rms < best_rms) {
        best_rms = rms;
        best_max_forceSquared = max_forceSquared;
        positionPointerSegment[PTR_BST] = positionPointerSegment[best_ptr];
        BestPositions = position_arrays + positionPointerSegment[PTR_BST] * NATOMS;
    }
    for (i=0; i<4; i++) {
        segmentUsed[i] = 0;
    }

    Positions = NewPositions;
    positionPointerSegment[PTR_CUR] = positionPointerSegment[PTR_NEW];
    
    segmentUsed[positionPointerSegment[PTR_CUR]] = 1;
    segmentUsed[positionPointerSegment[PTR_BST]] = 1;

    for (i=0; i<4; i++) {
        if (segmentUsed[i] == 0) {
            positionPointerSegment[PTR_NEW] = i;
            NewPositions = position_arrays + positionPointerSegment[PTR_NEW] * NATOMS;
            return;
        }
    }
    fprintf(stderr, "updatePositionsArrays: couldn't find an unused segment\n");
    exit(1);
}


/* these are shared between minimizeSteepestDescent() and minimizeConjugateGradients() */
static double sum_forceSquared;
static double movcon = 4e-4;

/*
  Minimize via adaptive steepest descent.
  
  Will do a maximum of steepestDescentFrames iterations.  Returns true
  if rms_force has dropped below RMS_CUTOVER pN before the iteration limit is
  reached.
*/
static int
minimizeSteepestDescent(int steepestDescentFrames,
                        int *frameNumber)
{
    int i, j;
    int interruptionWarning;
    struct xyz f; // force
    double last_sum_forceSquared;
    double rms_force;
    double max_forceSquared;
    double forceSquared;
    double movfac = 1.5;
    double sum_force_dot_old_force;
    double xxx, yyy;
    
    // 2 fixed steps to initialize
    for (i=0; i<2; i++) {
	max_forceSquared = 0.0;
	sum_forceSquared = 0.0;
	calculateForces(1, Positions, Force);
	for (j=0; j<Nexatom; j++) {
	    f = Force[j];
	    OldForce[j] = f;
	    forceSquared = vdot(f,f);
	    sum_forceSquared += forceSquared;
	    if (forceSquared>max_forceSquared) max_forceSquared = forceSquared;
	    vmulc(f, movcon);
	    vadd2(NewPositions[j], Positions[j], f);
	}
	rms_force = sqrt(sum_forceSquared/Nexatom);
        groundAtoms(Positions, NewPositions);
        updatePositionsArrays(rms_force, max_forceSquared, PTR_CUR);
    }
    initial_rms = rms_force;
    minshot(outf, 0, Positions, rms_force, max_forceSquared, (*frameNumber)++, "1");

    // adaptive stepsize steepest descents until RMS gradient is under RMS_CUTOVER
    while (*frameNumber < steepestDescentFrames && !Interrupted) {
	last_sum_forceSquared = sum_forceSquared;
	max_forceSquared = 0.0;
	sum_forceSquared = 0.0;
	sum_force_dot_old_force=0.0;
	calculateForces(1, Positions, Force);
	for (j=0; j<Nexatom; j++) {
	    f= Force[j];
	    forceSquared = vdot(f,f);
	    if (forceSquared>max_forceSquared) max_forceSquared = forceSquared;
	    sum_forceSquared += forceSquared;
	    sum_force_dot_old_force += vdot(f,OldForce[j]);
	}
	rms_force = sqrt(sum_forceSquared/Nexatom);

	minshot(outf, 0, Positions, rms_force, max_forceSquared, (*frameNumber)++, "2");

        if ((rms_force > MAX_RMS) ||
            (rms_force <= RMS_CUTOVER && max_forceSquared <= MAX_CUTOVER_SQUARED)) {
            break;
        }
        
	xxx = sqrt(last_sum_forceSquared); // == previous rms_force * sqrt(Nexatom)
	yyy = sum_force_dot_old_force/xxx;
        DPRINT(D_MINIMIZE, "                         %f <? %f - %f (%f)\n", yyy, xxx, xxx/movfac, xxx-xxx/movfac);
	if (yyy < (xxx - xxx/(movfac))) {
            movcon *= xxx/(xxx-yyy);
            DPRINT(D_MINIMIZE, "                         movcon *= %f / %f (%f)\n", xxx, xxx-yyy, xxx/(xxx-yyy));
        } else {
            movcon *= movfac;
            DPRINT(D_MINIMIZE, "                         movcon *= movfac\n", xxx, yyy, movcon);
        }
        DPRINT(D_MINIMIZE, "                         %f\n", movcon);
        
	for (j=0; j<Nexatom; j++) {
	    f= Force[j];
	    OldForce[j] = f;
	    vmulc(f, movcon);
	    vadd2(NewPositions[j], Positions[j], f);
	}
        groundAtoms(Positions, NewPositions);
        updatePositionsArrays(rms_force, max_forceSquared, PTR_CUR);
    }
    if (rms_force <= RMS_CUTOVER && max_forceSquared <= MAX_CUTOVER_SQUARED) {
        fprintf(tracef, "# Switching to Conjugate-Gradient\n");
        return 1;
    } else {
	interruptionWarning = minshot(outf, 1, BestPositions, best_rms, best_max_forceSquared,
                                      (*frameNumber)++, "SDfinal");
        if (!interruptionWarning) {
            if (*frameNumber > steepestDescentFrames) {
                WARNING("minimization terminated after %d iterations", steepestDescentFrames);
            } else if (rms_force >= MAX_RMS) {
                WARNING("minimization terminated due to excessive force");
            } else{
                // don't think we can get here...
                WARNING("minimization terminated in Steepest Descent");
            }
        }
        return 0;
    }
}

static void
minimizeConjugateGradients(int numFrames, int *frameNumber)
{
    int i, j, k;
    int interruptionWarning;
    double forceSquared, max_forceSquared;
    double sum_old_force_squared;
    double last_sum_forceSquared;
    double sum_force_dot_old_force;
    double gamma; // = sum_forceSquared / last_sum_forceSquared
    double xxx, yyy, zzz;
    struct xyz f; // force
    double rms_force;
    double old_movcon = movcon;
    double movfac = 3.0;
    
    max_forceSquared = 0.0;
    last_sum_forceSquared = sum_forceSquared;
    sum_forceSquared = 0.0;
    calculateForces(1, Positions, Force);
    for (j=0; j<Nexatom; j++) {
	f= Force[j];
	forceSquared = vdot(f,f);
	if (forceSquared>max_forceSquared) max_forceSquared = forceSquared;
	sum_forceSquared += forceSquared;
    }
    rms_force = sqrt(sum_forceSquared/Nexatom);

    // conjugate gradients for a while
    while (rms_force>RMS_FINAL && rms_force < MAX_RMS && *frameNumber<numFrames && !Interrupted) {
	//for (i=0; i<20 ;  i++) {
	minshot(outf, 0, Positions, rms_force, max_forceSquared, (*frameNumber)++, "3");
	gamma = sum_forceSquared/last_sum_forceSquared;
	// compute the conjugate direction 
	last_sum_forceSquared=sum_forceSquared;
	sum_old_force_squared=0.0;
	sum_force_dot_old_force=0.0;
	for (j=0; j<Nexatom; j++) {
	    vmul2c(f,OldForce[j],gamma);
	    vadd(f,Force[j]);
	    OldForce[j]=f;
	    sum_old_force_squared += vdot(f,f);
	    sum_force_dot_old_force += vdot(Force[j],OldForce[j]);
	}
	xxx = sqrt(sum_old_force_squared);
	yyy = sum_force_dot_old_force/xxx;
	zzz = yyy;
        DPRINT(D_MINIMIZE, "xxx: %f yyy: %f\n", xxx, yyy);
	for (k=0; k<10 && yyy*yyy>1.0 && (DumpAsText || *frameNumber<numFrames) && !Interrupted; k++) {
	    for (j=0; j<Nexatom; j++) {
		f=OldForce[j];
		vmulc(f, movcon);
		vadd2(NewPositions[j],Positions[j], f);
	    }
            groundAtoms(Positions, NewPositions);
	    sum_forceSquared = 0.0;
	    sum_force_dot_old_force=0.0;
	    calculateForces(0, NewPositions, Force);
	    for (j=0; j<Nexatom; j++) {
		f= Force[j];
		forceSquared = vdot(f,f);
		if (forceSquared>max_forceSquared) max_forceSquared = forceSquared;
		sum_forceSquared += forceSquared;
		sum_force_dot_old_force += vdot(f,OldForce[j]);
	    }
	    rms_force = sqrt(sum_forceSquared/Nexatom);
            /*
            minshot(outf, 0, NewPositions, rms_force, max_forceSquared, (*frameNumber)++, "4"); 
            */
	    yyy = sum_force_dot_old_force/xxx;
	    if (yyy<zzz-zzz/(movfac)) movcon *= zzz/(zzz-yyy);
	    else movcon *= movfac;
            DPRINT(D_MINIMIZE, "xxx: %f yyy: %f zzz: %f movcon: %f\n", xxx, yyy, zzz, movcon);
	}
	old_movcon=movcon;
	if (yyy<xxx-xxx/(movfac+1.0)) movcon *= xxx/(xxx-yyy)-1.0;
	else movcon *= movfac;
        DPRINT(D_MINIMIZE, "xxx: %f yyy: %f movcon: %f\n", xxx, yyy, movcon);
	for (j=0; j<Nexatom; j++) {
	    f= OldForce[j];
	    vmulc(f, movcon);
	    vadd(NewPositions[j], f);
	}
        groundAtoms(Positions, NewPositions);
	if (movcon<0) movcon = old_movcon+movcon;
	max_forceSquared = 0.0;
	sum_forceSquared = 0.0;
	calculateForces(0, NewPositions, Force);
	for (j=0; j<Nexatom; j++) {
	    f= Force[j];
	    forceSquared = vdot(f,f);
	    if (forceSquared>max_forceSquared) max_forceSquared = forceSquared;
	    sum_forceSquared += forceSquared;
	}
	rms_force = sqrt(sum_forceSquared/Nexatom);
        updatePositionsArrays(rms_force, max_forceSquared, PTR_NEW);
    }
    interruptionWarning = minshot(outf, 1, BestPositions, best_rms, best_max_forceSquared,
                                  (*frameNumber)++, "final");
    if (rms_force > RMS_FINAL && !interruptionWarning) {
        if (*frameNumber > numFrames) {
            WARNING("minimization terminated after %d iterations", numFrames);
        } else if (rms_force >= MAX_RMS) {
            WARNING("minimization terminated due to excessive force");
        } else{
            // don't think we can get here...
            WARNING("minimization terminated in Conjugate-Gradient");
        }
    }
}

static void
minimize(int numFrames)
{
    int frameNumber;
    int steepestDescentFrames;
    int conjugateGradientFrames;
    
    frameNumber = 1;
    steepestDescentFrames = DumpAsText ? numFrames : numFrames / 2;
    conjugateGradientFrames = DumpAsText ? numFrames*6 : numFrames;
    
    fprintf(tracef,"\n# rms force, high force\n");

    if (minimizeSteepestDescent(steepestDescentFrames, &frameNumber)) {
        minimizeConjugateGradients(conjugateGradientFrames, &frameNumber);
    } else {
    }
    doneExit(0, tracef, "Minimization final rms: %f, highForce: %f",
             best_rms, sqrt(best_max_forceSquared));
}

static void
SIGTERMhandler(int sig) 
{
    Interrupted = 1;
}

#if 0
static void installSIGTERMhandler() 
{
    struct sigaction act;

    act.sa_handler = &SIGTERMhandler;
    sigemptyset(&act.sa_mask);
    act.sa_flags = 0;
    if (sigaction(SIGTERM, &act, NULL) < 0) {
        perror("sigaction()");
        exit(1);
    }
}
#endif

static void
usage()
{
                
    fprintf(stderr, "command line parameters:\n\
   -d<char>      -- dump, <char>= a: atoms; b: bonds; c: constraints\n\
   -n<int>       -- expect this many atoms\n\
   -m            -- minimize the structure\n\
   -i<int>       -- number of iterations per frame\n\
   -f<int>       -- number of frames\n\
   -s<float>     -- timestep\n\
   -t<float>     -- temperature\n\
   -x            -- write positions as (text) .xyz file(s)\n\
   -X            -- write intermediate minimize positions to .xyz (need -x)\n\
   -O            -- write old format .dpb files (default)\n\
   -N            -- write new format .dpb files\n\
   -I<string>    -- specify IDKey\n\
   -K<int>       -- number of delta frames between key frames\n\
   -r            -- repress frame numbers\n\
   -o<string>    -- output file name (otherwise same as input)\n\
   -q<string>    -- trace file name (otherwise trace)\n\
   -D<int>       -- turn on a debugging flag (see simulator.h)\n\
   filename      -- if no ., add .mmp to read, .dpb to write\n");
    exit(1);
}


main(int argc,char **argv)
{
    int i, j, n;
    int da=0, db=0, dc=0, dw=0;
    struct xyz p, foo;
    double therm = 0.645;
	
    char buf[1024], *filename, *ofilename, *tfilename, *c;
	
    double x,y,z, end, theta;

    if (signal(SIGTERM, &SIGTERMhandler) == SIG_ERR) {
        perror("signal(SIGTERM)");
        exit(1);
    }

    setupPositionsArrays();
	
    vsetc(Cog,0.0);
    vsetc(P,0.0);
    vsetc(Omega,0.0);
	
    filename = (char *)0;
    ofilename = (char *)0;
    tfilename = (char *)0;

    for (i=1; i<argc; i++) {

	if (argv[i][0] == '-') {
	    switch (argv[i][1]) {
	    case 'h':
                usage();
	    case 'd':
		if (argv[i][2]=='a') da = 1;
		if (argv[i][2]=='b') db = 1;
		if (argv[i][2]=='c') dc = 1;
		if (argv[i][2]=='w') dw = 1;
	    case 'n':
		n = atoi(argv[i]+2);
		if (n>NATOMS) {
		    fprintf(stderr, "n too high = %d\n",n);
		    exit(1);
		}
		break;
	    case 'm':
		ToMinimize=1;
		break;
	    case 'i':
		IterPerFrame = atoi(argv[i]+2);
		break;
	    case 'f':
		NumFrames = atoi(argv[i]+2);
		break;
	    case 's':
	        Dt = atof(argv[i]+2);
		break;
	    case 't':
		Temperature = atof(argv[i]+2);
		break;
	    case 'x':
		DumpAsText=1;
		break;
	    case 'X':
		DumpIntermediateText=1;
		break;
	    case 'O':
		OutputFormat=1;
		break;
	    case 'N':
		OutputFormat=2;
		break;
	    case 'I':
                IDKey=argv[i]+2;
		break;
	    case 'K':
                KeyRecordInterval=atoi(argv[i]+2);
		break;
	    case 'r':
		PrintFrameNums=0;
		break;
	    case 'D':
		n = atoi(argv[i]+2);
                if (n < 32 && n >= 0) {
                    debug_flags |= 1 << n;
                }
		break;
            case 'o':
		ofilename=argv[i]+2;
		break;
	    case 'q':
		tfilename=argv[i]+2;
		break;
	    default:
		fprintf(stderr, "unknown switch %s\n",argv[i]+1);
	    }
	}	
	else {
	    filename = argv[i];
	}
    }

    if (DumpAsText) {
        OutputFormat = 0;
    }

    if (!filename) {
        usage();
    }

    //if (ToMinimize) printf("Minimize\n");

    if (strchr(filename, '.')) {
        sprintf(buf, "%s", filename);
    } else {
        sprintf(buf, "%s.mmp", filename);
    }

    if (! ofilename) {
	strcpy(OutFileName,buf);
	c=strchr(OutFileName, '.');
	if (c) {
            *c='\0';
        }
    } else {
        strcpy(OutFileName,ofilename);
    }
    
    if (! strchr(OutFileName, '.')) {
	if (DumpAsText) {
            strcat(OutFileName,".xyz");
        } else {
            strcat(OutFileName,".dpb");
        }
    }

    if (! tfilename) {
	strcpy(TraceFileName,buf);
	c=strchr(TraceFileName, '.');
	if (c) {
            *c='\0';
        }
    } else {
        strcpy(TraceFileName,tfilename);
    }
    
    if (! strchr(TraceFileName, '.')) {
        strcat(TraceFileName,".trc");
    }

    if (IterPerFrame <= 0) IterPerFrame = 1;

    initializeBondTable();
    vdWsetup();
    //testInterpolateBondStretch(1, 6, 6);
    //testNewBondStretchTable();

    filred(buf);
    
    // this doesn't seem to make any difference... -emm
    //orion();

    if (da) {
	fprintf(stderr, "%d atoms:\n",Nexatom);
	for (i=0; i<Nexatom; i++) pa(stderr, i);
    }
    if (db) {
	fprintf(stderr, "%d bonds:\n",Nexbon);
	for (i=0; i<Nexbon; i++) pb(stderr, i);
	fprintf(stderr, "%d torques:\n",Nextorq);
	for (i=0; i<Nextorq; i++) pq(stderr, i);
    }
    if (dw) {
	fprintf(stderr, "%d Waals:\n",vanderRoot);
	for (i=0; i<vanderRoot.fill; i++) pvdw(stderr, &vanderRoot,i);
    }
    if (dc) {
	fprintf(stderr, "%d constraints:\n",Nexcon);
	for (i=0; i<Nexcon; i++) pcon(stderr, i);
    }
    /*
    fprintf(stderr, " center of mass velocity: %f\n", vlen(vdif(CoM(Positions),CoM(OldPositions))));
    fprintf(stderr, " center of mass: %f -- %f\n", vlen(CoM(Positions)), vlen(Cog));
    fprintf(stderr, " total momentum: %f\n",P);
    */
    tracef = fopen(TraceFileName, "w");
    if (!tracef) {
        perror(TraceFileName);
        exit(1);
    }
    printheader(tracef, filename, OutFileName, TraceFileName, 
                Nexatom, NumFrames, IterPerFrame, Temperature);

    if  (ToMinimize) {
	NumFrames = max(NumFrames,(int)sqrt((double)Nexatom));
	Temperature = 0.0;
    } else {
        headcon(tracef);
    }

    printf("iters per frame = %d\n",IterPerFrame);
    printf("number of frames = %d\n",NumFrames);
    printf("timestep = %e\n",Dt);
    printf("temp = %f\n",Temperature);
    if (DumpAsText) printf("dump as text\n");

    printf("< %s  > %s\n", buf, OutFileName);

    printf("\nTotal Ke = %e\n",TotalKE);

    outf = fopen(OutFileName, DumpAsText ? "w" : "wb");
    if (outf == NULL) {
        perror(OutFileName);
        exit(1);
    }
    writeOutputHeader(outf);

    if  (ToMinimize) {
	minimize(NumFrames);
    }
    else {
	for (i=0; i<NumFrames; i++) {
	    if (PrintFrameNums) printf(" %d", i);
	    fflush(stdout);
	    if ((i & 15) == 15)
		if (PrintFrameNums) printf("\n");
	    calcloop(IterPerFrame);
	    snapshot(outf, i);
	}

	/*  do the time-reversal (for debugging)
	tmp=Positions; Positions=NewPositions; NewPositions=tmp;

	for (i=0; i<NumFrames; i++) {
	    printf(" %d", i);
	    fflush(stdout);
	    if ((i & 15) == 15)
		printf("\n");
	    calcloop(IterPerFrame);
	    snapshot(outf, i);
	}
	 */
        writeOutputTrailer(outf, NumFrames);
    }

    doneExit(0, tracef, "");
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */

