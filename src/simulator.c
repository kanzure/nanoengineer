// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "simulator.h"


/** indicate next avail/total number of stretch bonds, bend bonds, and atoms */
int Nexbon=0, Nextorq=0, Nexatom=0;

/* factor for a unit vector given length squared -- rtned in uf, i is temp */
/** tables and setup function for same */
double uft1[UFTLEN], uft2[UFTLEN];

double uffunc(double uf) {
    return 1.0/sqrt(uf);
}

/** positions and forces on the atoms w/pointers into pos */
struct xyz pos[3*NATOMS], f, force[NATOMS], avg[NATOMS];
struct xyz *old, *new, *cur, *tmp;

struct xyz Center, Bbox[2];

/** data for the 5-carbon test molecule */
struct xyz diam[5]=
    {{0.0, 0.0, 0.0},
     {176.7, 176.7, 0.0},
     {176.7, 0.0, 176.7},
     {0.0, 176.7, 176.7},
     {88.33, 88.33, 88.33}};

int PartNo=0, DisplayStyle=1;	/* 0 nothing, 1 ball/stick, 2 vdW surface */

struct A atom[NATOMS];

struct B bond[4*NATOMS];

struct Q torq[6*NATOMS];


int Iteration=0;


int findbond(int btyp) {
    int i;
    if (btyp < 0)
	btyp = -btyp;
    for (i=0; i < BSTABSIZE; i++)
	if (bstab[i].typ == btyp)
	    return i;
    DBGPRINTF("Bond type %d not found\n",btyp);
    return -1;
}

int findtorq(int btyp1, int btyp2) {
    int i;
    for (i=0; i < BENDATASIZE; i++) {
		
	if  (iabs(bendata[i].b1typ) == iabs(btyp1) &&
	     iabs(bendata[i].b2typ) == iabs(btyp2)) return i;
	if  (iabs(bendata[i].b1typ) == iabs(btyp2) &&
	     iabs(bendata[i].b2typ) == iabs(btyp1)) return i;
    }
    // printf("Bend type %d-%d not found\n",btyp1,btyp2);
    return 0; // the default bend type
}

/** the force between elt i and elt j (i<=j) is at
    vanderTable[i*(NUMELTS+1) - i*(i+1)/2 + j-i] */
// struct vdWtab vanderTable[(NUMELTS * (NUMELTS+1))/2];
struct vdWtab vanderTable[(50 * 51)/2];

double RvdW, EvdW;

struct vdWbuf *Nexvanbuf, *Dynobuf;
int Dynoix;			/* start of dynamically found vdw's */

/** A space grid for locating non-bonded interactions */

struct A *Space[SPWIDTH][SPWIDTH][SPWIDTH];	/*  space buckets */

void orion() {			/* atoms in space :-) */
    int n, i,j,k;
    struct A *emptybucket = NULL;
    struct A **pail = &emptybucket;
	
    for (n=0; n<Nexatom; n++) *atom[n].bucket = NULL;
	
    for (n=0; n<Nexatom; n++) {
	i= ((int)cur[n].x / 250) & SPMASK;
	j= ((int)cur[n].y / 250) & SPMASK;
	k= ((int)cur[n].z / 250) & SPMASK;
		
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

/** pN/kg => acc in pm/s^2; mult by Dt^2 for pm/fs^2 */

double R0 = 152.3, R1 = 152.3, Theta0 = 1.911;

/** global properties: center of mass, momentum, moment of rotation */
double totMass=0.0;
struct xyz Cog, P, Omega;

// definitions for command line args

int ToMinimize=0;
int IterPerFrame=10;
int NumFrames=100;
int DumpAsText=0;

char OutFileName[80];

// for writing the differential position file
FILE *outf;
int *ixyz, *previxyz, *temp, ibuf1[NATOMS*3], ibuf2[NATOMS*3];


/* for testing table routines */
double t1[TABLEN], t2[TABLEN];
double start=10000.0;
int scale=30;

/* Make a table for interpolating func(x) by doing
   i=(int)(x-start)/scale;
   value=t1[i]+x*t2[i]; */

void maktab(double *t1, double *t2, double func(double),
	    double start, int length, int scale) {
    int i;
    double v1, v2, r1, r2, q;
    double ov1, v3, r5, r15, v5, v15;
	
    r2=start;
    v2=func(r2);
	
    for (i=0; i<length; i++) {
	r1=r2;
	v1=v2;
	r2=start+(double)((i+1)*scale);
	v2=func(r2);
	/* shift points to minimize excursions above/below func */
	if (i<length-1) {
	    r5=(r1+r2)/2.0;
	    r15=r2+r2-r5;
	    v5=func(r5);
	    v15=func(r15);
	    v3=func(r2+r2-r1);
	    v2=v2 + 0.25*(v5-(func(r1)+v2)/2.0) + 0.25*(v15-(v2+v3)/2.0);
	}
		
	q=(v2-v1)/(r2-r1);
	t1[i] = v1 - q*r1;
	t2[i] = q;
    }
}

/* consider atoms a0 and a1 both bonded to atom ac.
   We are given the length of (a0-ac)+(a1-ac), squared, and
   desire to calculate a factor which multiplied by (a1-ac)
   gives the appropriate bending force for a0 */

/* uses globals R0 and R1, the lengths of (a0-ac) & (a1-ac), in pm,
   Kb, in N/m, and Theta0, the nominal angle, in radians */

double bender(double rsq) {
    double theta,f;
    theta=acos((rsq-(R0*R0+R1*R1))/(2.0*R0*R1));
	
    if (theta < Theta0)
	f= - Kb*(exp(-2.0*(theta-Theta0)) - exp(-(theta-Theta0)));
    else f=  Kb*sin(Pi * (theta - Theta0) / (Pi - Theta0))*(Pi - Theta0)/Pi;
	
	
    return R0*f / (R1 * sin(theta));
}

/** note -- uses global Ks and R0 */
double hooke(double rsq) {
	double r;
	
	r=sqrt(rsq);
	return Ks*(R0/r-1.0);
}

/* use the Morse potential inside R0, Lippincott outside */
/* numerically differentiate the resulting potential for force */
/* uses global De, Beta, Ks and R0 */
double lippmor(double rsq) {
    double r,y1,y2;
	
    r=sqrt(rsq);
    r=r+0.5;
	
    if (r>=R0)
	y2=De *(1-exp(- 1e-6 * Ks * R0 * (r - R0)* (r - R0) / (2 *De* r)));
    else
	y2=De *(1-exp(- Beta * (r - R0))) *(1-exp(- Beta * (r - R0)));
	
    r=r-1.0;
	
    if (r>=R0)
	y1=De *(1-exp(- 1e-6 * Ks * R0 * (r - R0)* (r - R0) / (2 *De* r)));
    else
	y1=De *(1-exp(- Beta * (r - R0))) *(1-exp(- Beta * (r - R0)));
	
    r=r+0.5;
	
    return 1e6*(y1-y2)/r;
}

/* the Buckingham potential for van der Waals / London force */
/* uses global EvdW, RvdW */
double bucking(double rsq) {
    double r, y;
    r=sqrt(rsq);
	
    y= -1e3 * EvdW*(2.48e5 * exp(-12.5*(r/RvdW)) *(-12.5/RvdW)
		    -1.924*pow(1.0/RvdW, -6.0)*(-6.0)*pow(r,-7.0));
	
    return y/r;
}

double square(double x) {return x*x;}

/* initialize the function tables for each bending and stretching bondtype */
/* sets global De, Beta, Ks and R0 */
void bondinit() {
    int i, j, b1,b2;
    double end, m, rxsq;
    struct dtab *tables,*t2;
	
    for (i=0; i < BSTABSIZE; i++) {
		
	R0 = bstab[i].r0;
	bstab[i].start = square(R0*0.5);
	end = square(R0*1.5);
	bstab[i].scale = (end - bstab[i].start) / TABLEN;
	Ks = bstab[i].ks;
	De = bstab[i].de;
	Beta = bstab[i].beta;
	tables = malloc(sizeof(struct dtab));
	if (ToMinimize)
	    	maktab(tables->t1, tables->t2, hooke,
		       bstab[i].start, TABLEN, bstab[i].scale);
	else maktab(tables->t1, tables->t2, lippmor,
		    bstab[i].start, TABLEN, bstab[i].scale);
	bstab[i].table = tables;
    }
	
    for (i = 0; i < BENDATASIZE; i++) {
	/* find the two bondtypes for this bendtype */
	b1=findbond(bendata[i].b1typ);
	b2=findbond(bendata[i].b2typ);
		
	/* find limits and scale for table */
	R0 = bstab[b1].r0;
	R1 = bstab[b2].r0;
	Theta0 = bendata[i].theta0;
	bendata[i].start =  R0*R0 + R1*R1 + 2.0*R0*R1*cos(Theta0+1.2*Pi/4.0);
	end =  R0*R0 + R1*R1 + 2.0*R0*R1*cos(Theta0-1.2*Pi/4.0);
	bendata[i].scale = (end - bendata[i].start) / TABLEN;
	/* for each end atom */
	Kb=bendata[i].kb;
	/* make the table */
	tables = malloc(sizeof(struct dtab));
	maktab(tables->t1, tables->t2, bender,
	       bendata[i].start, TABLEN, bendata[i].scale);
	bendata[i].tab1 = tables;
	if (bendata[i].b1typ == bendata[i].b2typ) bendata[i].tab2 = tables;
	else {
	    end=R0; R0=R1; R1=end;
	    tables = malloc(sizeof(struct dtab));
	    maktab(tables->t1, tables->t2, bender,
		   bendata[i].start, TABLEN, bendata[i].scale);
	    bendata[i].tab2 = tables;
	}
    }
}

void vdWsetup() {
    int i, j, k, nx, scale;
    double x, y, start, end;
	
    for (i=0; i<NUMELTS; i++)
	for (j=0; j<NUMELTS; j++)
	    if (i<=j) {
		RvdW = 100.0 * (element[i].rvdw + element[j].rvdw);
		EvdW = (element[i].evdw + element[j].evdw)/2.0;
				
		nx = i*(NUMELTS+1) - i*(i+1)/2 + j-i;
				
		start= square(RvdW*0.4);
		end=square(RvdW*1.5);
		scale = (int)(end - start) / TABLEN;
				
		vanderTable[nx].start = start;
		vanderTable[nx].scale = scale;
				
		maktab(vanderTable[nx].table.t1, vanderTable[nx].table.t2,
		       bucking, start, TABLEN, scale);
				
	    }
	
    Nexvanbuf = &vanderRoot;
    Nexvanbuf->fill = 0;
    Nexvanbuf->next = NULL;
	
    /* the space grid */
    for (i=0;i<SPWIDTH; i++)
	for (j=0;j<SPWIDTH; j++)
	    for (k=0;k<SPWIDTH; k++)
		Space[i][j][k] = NULL;
	
}

/** kT @ 300K is 4.14 zJ -- RMS V of carbon is 1117 m/s
    or 645 m/s each dimension, or 0.645 pm/fs  */

double gavss(double v) {
    double v0,v1, rsq;
    do {
	v0=(float)rand()/(float)(RAND_MAX/2) - 1.0;
	v1=(float)rand()/(float)(RAND_MAX/2) - 1.0;
	rsq = v0*v0 + v1*v1;
    } while (rsq>=1.0 || rsq==0.0);
    return v*v0*sqrt(-2.0*log(rsq)/rsq);
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


static int ShotNo=0;

void calcloop(int iters) {
	
    double fac, pe,ke;
    int i,j, k, loop, a1;
    double rsq, br, ff, m, theta, z, totorq;
    struct xyz f, v1, v2, rx, foo,bar, totforce;
    struct vdWbuf *nvb;
    struct MOT *mot;
	
    double *t1, *t2;
    double start;
    int scale;
    int inner = 10;
	
    for (j=0; j<Nexatom; j++) {
	vsetc(avg[j],0.0);
    }
	
    for (loop=0; loop<iters; loop++) {
		
	/* find the non-bonded interactions */
	orion();
		
	Nexvanbuf=Dynobuf;
	Nexvanbuf->fill = Dynoix;
	Count = 0;
		
	for (j=0; j<Nexatom; j++) {
	    findnobo(j);
	}
		
	for (i=inner; i; i--) {		/* do whole force calc n steps */
			
	    Iteration++;
			
	    /* new, cur, and old to avoid mixing positions while
	       calculating force
	       force calculated separately because used for other things */
			
	    /* first, for each atom, find non-accelerated new pos and clear force */
	    /* speed all up or slow down as temp is under/over desired */
	    /*
	      if (FoundKE < TotalKE)  ff=1.005;
	      else ff=0.995;
	    */
			
			
	    for (j=0; j<Nexatom; j++) {
		vsub2(f,cur[j],old[j]);
		ff = vdot(f,f);
		if (ff < atom[j].vlim) ff=1.0;
		else ff = atom[j].vlim/ff;
		vmulc(f, ff);
		vadd2(new[j],cur[j],f);
				
		vsetc(force[j],0.0);
	    }
			
	    /* compute stretch force for each bond, accumulating in force[atom] */
	    for (j=0; j<Nexbon; j++) {
		vsub2(bond[j].r, cur[bond[j].an1], cur[bond[j].an2]);
		vset(f,bond[j].r);
		rsq = vdot(f,f);
				
		/* while we're at it, set unit bond vector and clear bend force */
		ufac(ff,k,rsq);
		vmul2c(bond[j].ru,f,ff);
		vsetc(bond[j].bff,0.0);
				
		/* table setup for stretch, to be moved out of loop */
		start=bond[j].type->start;
		scale=bond[j].type->scale;
		t1=bond[j].type->table->t1;
		t2=bond[j].type->table->t2;
				
		k=(int)(rsq-start)/scale;
		if (k<0) {
					
		    DBGPRINTF("stretch: low --");
		    //pb(j);
		    fac=t1[0]+rsq*t2[0];
		}
		else if (k>=TABLEN) {
					
		    DBGPRINTF("stretch: high --");
		    //pb(j);
		    if (ToMinimize) fac = t1[0]+rsq*t2[0]; //linear
		    else fac=0.0;
		}
		else fac=t1[k]+rsq*t2[k];
				
		vmul2c(bond[j].aff,f,fac);
				
	    }
			
	    /* now the forces for each bend, accumulating ones for each pair
	       in the bond record */
	    /* v1, v2 are the vectors FROM the central atom TO the neighbors */
			
	    for (j=0; j<Nextorq; j++) {
				
		if (torq[j].dir1) {vsetn(v1,torq[j].b1->r);}
		else {vset(v1,torq[j].b1->r);}
		if (torq[j].dir2) {vsetn(v2,torq[j].b2->r);}
		else {vset(v2,torq[j].b2->r);}
				
		vadd2(rx,v1,v2);
		rsq=vdot(rx,rx);
				
		/* table setup for bend, to be moved out of loop */
		start=torq[j].type->start;
		scale=torq[j].type->scale;
		t1=torq[j].type->tab1->t1;
		t2=torq[j].type->tab1->t2;
				
		k=(int)(rsq-start)/scale;
		if (k<0 || k>=TABLEN) {
		    theta=(180.0/3.1415)*vang(v1,v2);
					
		    printf("bend: off table -- angle = %.2f\n",theta);
		    pq(j);
					
		    if (k<0) k=0;
		    else k=TABLEN-1;
		}
		ff=t1[k]+rsq*t2[k];
				
		vmulc(v2,ff);
		if (torq[j].dir1) {vsub(torq[j].b1->bff,v2);}
		else {vadd(torq[j].b1->bff,v2);}
				
		if (torq[j].type->tab1 == torq[j].type->tab2) {
		    t1=torq[j].type->tab2->t1;
		    t2=torq[j].type->tab2->t2;
					
		    ff=t1[k]+rsq*t2[k];
		}
		vmulc(v1,ff);
				
		if (torq[j].dir2) {vsub(torq[j].b2->bff,v1);}
		else {vadd(torq[j].b2->bff,v1);}
	    }
			
	    /* now loop over bonds again, orthogonalizing torques and
	       adding to force */
	    for (j=0; j<Nexbon; j++) {
		vadd(force[bond[j].an1],bond[j].aff);
		vsub(force[bond[j].an2],bond[j].aff);
		/*
		  br=sqrt(vdot(bond[j].aff,bond[j].aff));
		  DBGPRINTF("bond %d: stretch force: %f, ",j,br);
		*/
		vmul2c(f,bond[j].ru,vdot(bond[j].ru,bond[j].bff));
		vsub2(f,bond[j].bff,f);
		vadd(force[bond[j].an1],f);
		vsub(force[bond[j].an2],f);
		
	    }
			
	    /* do the van der Waals/London forces */
	    for (nvb=&vanderRoot; nvb; nvb=nvb->next)
		for (j=0; j<nvb->fill; j++) {
		    vsub2(f, cur[nvb->item[j].a1], cur[nvb->item[j].a2]);
		    rsq = vdot(f,f);
					
		    if (rsq>50.0*700.0*700.0) {
			DBGPRINTF("hi vdw: %f\n", sqrt(rsq));
			pvdw(nvb,j);
			pa(nvb->item[j].a1);
			pa(nvb->item[j].a2);
		    }
					
		    /*
		      DBGPRINTF("Processing vdW %d/%d: atoms %d-%d, r=%f\n",
		      nvb-&vanderRoot, j,nvb->item[j].a1, nvb->item[j].a2,
		      sqrt(rsq));
		    */
		    /* table setup  */
		    start=nvb->item[j].table->start;
		    scale=nvb->item[j].table->scale;
		    t1=nvb->item[j].table->table.t1;
		    t2=nvb->item[j].table->table.t2;
					
		    k=(int)(rsq-start)/scale;
		    if (k<0) {
			DBGPRINTF("vdW: off table low -- r=%.2f \n",  sqrt(rsq));
			pvdw(nvb,j);
			k=0;
			fac=t1[k]+rsq*t2[k];
		    }
		    else if (k>=TABLEN) {
			/*
			  DBGPRINTF("vdW: off table high -- %d/%d: start=%.2f, scale=%d\n",
			  k,TABLEN, start, scale);
			*/
			fac = 0.0;
		    }
		    else fac=t1[k]+rsq*t2[k];
		    vmulc(f,fac);
		    vadd(force[nvb->item[j].a1],f);
		    vsub(force[nvb->item[j].a2],f);
		}
			
	    /* convert forces to accelerations, giving new positions */
			
	    FoundKE = 0.0;		/* and add up total KE */
			
	    for (j=0; j<Nexatom; j++) {
		/*
		  ff=vlen(force[j]);
		  DBGPRINTF("--> Total force on atom %d is %.2f, displacement %f\n", j,
		  ff, ff*atom[j].massacc);
		*/
		vmul2c(f,force[j],atom[j].massacc);
				
		if (vlen(f)>15.0) {
		    DBGPRINTF("High force %.2f in iteration %d\n",vlen(f), Iteration);
		    pa(j);
		}
				
		vadd(new[j],f);
		vadd(avg[j],new[j]);
				
		vsub2(f, new[j], cur[j]);
		ff = vdot(f, f);
		FoundKE += atom[j].energ * ff;
	    }
			
	    /* now the constraints */
	    /*
	      DBGPRINTF("\njust before, cur=\n");
	      for (j=0;j<Nexatom;j++) pvt(cur[j]);
	    */
	    for (j=0;j<Nexcon;j++) {	/* for each constraint */
		if (Constraint[j].type == 0) { /* welded to space */
		    for (k=0; k<Constraint[j].natoms; k++) {
			new[Constraint[j].atoms[k]] = cur[Constraint[j].atoms[k]];
		    }
		}
		else if (Constraint[j].type == 1) { /* motor */
					
		    mot=Constraint[j].motor;
		    totorq = 0.0;
					
		    /* input torque due to forces on each atom */
		    for (k=0; k<Constraint[j].natoms; k++) {
			a1 = Constraint[j].atoms[k];
			rx = vdif(cur[a1],mot->atocent[j]);
			f = vx(rx,force[a1]);
			ff = vdot(f, mot->axis);
			totorq += ff;
		    }
		    /*
		      DBGPRINTF("*** input torque %f\n", totorq);
		    */
		    /* theta_i+1 = 2theta_i - theta_i-1 + totorq + motorq
		       motorq = stall - omega*(stall/speed)
		       omega = (theta_i+1 - theta_i-1)/ 2Dt
		       solve for theta_i+1 -- preserves Verlet reversibility  */
		    z = mot->moment;
		    m = - z * mot->stall / (2.0 *  mot->speed);
		    theta = (2.0*mot->theta - (1.0+m)*mot->theta0 +
			     z*(mot->stall + totorq))  / (1.0 - m);
		    /*
		      DBGPRINTF("***  Theta = %f, %f, %f\n",theta, mot->theta, mot->theta0);
		    */
		    /* put atoms in their new places */
		    for (k=0; k<Constraint[j].natoms; k++) {
			a1 = Constraint[j].atoms[k];
			z = theta + mot->atang[k];
			vmul2c(v1, mot->roty, mot->radius[k] * cos(z));
			vmul2c(v2, mot->rotz, mot->radius[k] * sin(z));
			vadd2(new[a1], v1, v2);
			vadd(new[a1], mot->atocent[k]);
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
		}
	    }
	    /*
	      DBGPRINTF("just after, new=\n");
	      for (j=0;j<Nexatom;j++) pvt(new[j]);
	    */
			
	    tmp=old; old=cur; cur=new; new=tmp;
			
	}} /* end of main loop */
	
    ff = 1.0/((double)inner * (double)iters);
    for (j=0; j<Nexatom; j++) {
	vmulc(avg[j],ff);
    }
	
}


/**
 */
void snapshot(int n) {
    int i,j;
    char c0, c1, c2;
    if (DumpAsText) {

        fprintf(outf, "%d\nFrame %d, Iteration: %d\n", Nexatom, n, Iteration);

        for (i=0; i<Nexatom; i++) {
            fprintf(outf, "%s %f %f %f\n", element[atom[i].elt].symbol,
                    avg[i].x, avg[i].y, avg[i].z);
        }
    }
    else {
        for (i=0, j=0; i<3*Nexatom; i+=3, j++) {
            ixyz[i+0] = (int)avg[j].x;
            ixyz[i+1] = (int)avg[j].y;
            ixyz[i+2] = (int)avg[j].z;
            c0=(char)(ixyz[i+0] - previxyz[i+0]);
            fwrite(&c0, sizeof(char), 1, outf);
            c1=(char)(ixyz[i+1] - previxyz[i+1]);
            fwrite(&c1, sizeof(char), 1, outf);
            c2=(char)(ixyz[i+2] - previxyz[i+2]);
            fwrite(&c2, sizeof(char), 1, outf);

            //printf("%d %d %d\n", (int)c0, (int)c1, (int)c2);
        }
        temp = previxyz;
        previxyz = ixyz;
        ixyz = temp;

    }
}


void minimize(int NumFrames, int IterPerFrame) {
    int i, j, saveNexcon;
    double tke, therm, mass;
    struct xyz v;
   
    /* turn off constraints --
       minimize is a one-shot run of the program */
    Nexcon=0;

    Temperature = 0.0;
	
    for (i=0; i<NumFrames; i++) {
	// stop atoms in their tracks
	for (j=0; j<Nexatom; j++) old[j] = cur[j];
	calcloop(IterPerFrame);
	snapshot(0);
	}
}


/**
   read command line parms:
   -n -- expect <number> of atoms
   -m -- minimize the structure
   -i -- number of iterations per frame 
   -f -- number of frames
   -s -- timestep\n\
   -t -- temperature
   -x -- write positions as (text) xyz file(s)
   filename -- if no ., add .mmp to read, .dpb to write
 */

main(int argc,char **argv)
{
    int i,j, n;
    struct xyz p, foo;
    double therm = 0.645;
	
    char buf[80], *filename, *ofilename, *c;
	
    double x,y,z, end, theta;

    maktab(uft1, uft2, uffunc, UFSTART, UFTLEN, UFSCALE);
	
    bondinit();
    vdWsetup();
	
    cur=pos;
    old=pos+NATOMS;
    new=pos+2*NATOMS;
	
    vsetc(Cog,0.0);
    vsetc(P,0.0);
    vsetc(Omega,0.0);
	
    filename = (char *)0;
    ofilename = (char *)0;

    for (i=1; i<argc; i++) {

	if (argv[i][0] == '-') {
	    switch (argv[i][1]) {
	    case 'h':
		printf("command line parameters:\n\
   -n -- expect <number> of atoms\n\
   -m -- minimize the structure\n\
   -i -- number of iterations per frame\n\
   -f -- number of frames\n\
   -s -- timestep\n\
   -t -- temperature\n\
   -x -- write positions as (text) .xyz file(s)\n\
   -o -- output file name (otherwise same as input)\n\
   filename -- if no ., add .mmp to read, .dpb to write\n");
		exit(0);
	    case 'n':
		n = atoi(argv[i]+2);
		if (n>NATOMS) {
		    printf("n too high = %d\n",n);
		    exit(0);
		}
		break;
	    case 'm':
		ToMinimize=1;
		NumFrames = 100;
		IterPerFrame = 30;
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
	    case 'o':
		ofilename=argv[i]+2;
		break;
	    default:
		printf("unknown switch %s\n",argv[i]+1);
	    }
	}	
	else {
	    filename = argv[i];
	}
    }

    if (ToMinimize) printf("Minimize\n");
	
    if (! filename) filename="sample";
    if (strchr(filename, '.')) sprintf(buf, "%s", filename);
    else sprintf(buf, "%s.mmp", filename);

    if (! ofilename) {
	strcpy(OutFileName,buf);
	c=strchr(OutFileName, '.');
	if (c) *c='\0';
    }
    else strcpy(OutFileName,ofilename);
    if (! strchr(OutFileName, '.')) {

	if (DumpAsText) strcat(OutFileName,".xyz");
	else strcat(OutFileName,".dpb");
    }

    IterPerFrame = IterPerFrame/10;
    if (IterPerFrame == 0) IterPerFrame = 1;

    printf("iters per frame = %d\n",IterPerFrame);
    printf("number of frames = %d\n",NumFrames);
    printf("timestep = %e\n",Dt);
    printf("temp = %f\n",Temperature);
    if (DumpAsText) printf("dump as text\n");

    printf("< %s  > %s\n", buf, OutFileName);

    filred(buf);
    
    printf("%d constraints:\n",Nexcon);
      for (i=0; i<Nexcon; i++) pcon(i);
      /*
    printf("%d atoms:\n",Nexatom);
      for (i=0; i<Nexatom; i++) pa(i);
    printf("%d bonds:\n",Nexbon);
      for (i=0; i<Nexbon; i++) pb(i);
    printf("%d torques:\n",Nextorq);
      for (i=0; i<Nextorq; i++) pq(i);
    printf("%d Waals:\n",vanderRoot);
      for (i=0; i<vanderRoot.fill; i++) pvdw(&vanderRoot,i);
      */
    orion();

    if (DumpAsText) outf = fopen(OutFileName, "w");  

    else {
	ixyz=ibuf1;
	previxyz=ibuf2;
	for (i=0, j=0; i<3*Nexatom; i+=3, j++) {
	    previxyz[i+0] = (int)cur[j].x;
	    previxyz[i+1] = (int)cur[j].y;
	    previxyz[i+2] = (int)cur[j].z;
	}
	outf = fopen(OutFileName, "wb");  
	fwrite(&NumFrames, sizeof(int), 1, outf);
    }

    if  (ToMinimize) {
	minimize(NumFrames, IterPerFrame);
    }
    else {
	for (i=0; i<NumFrames; i++) {
	    printf(" %d", i);
	    fflush(stdout);
	    if ((i & 15) == 15)
		printf("\n");
	    calcloop(IterPerFrame);
	    snapshot(i);
	}}

    fclose(outf);
    printf("\n");
	
    return 0;
	
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */

