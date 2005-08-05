// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <signal.h>
#include <time.h>
#include <stdarg.h>
#include <errno.h>
#include <string.h>

#include "lin-alg.h"
#include "allocate.h"
#include "hashtable.h"

#include "readers.h"

/* begin tables.h */
extern struct atomtype element[];
extern struct bsdata bstab[];
extern struct angben bendata[];
extern const int NUMELTS;
extern const int BSTABSIZE;
extern const int BENDATASIZE;
/* end tables.h */

#define NATOMS 100000
#define NBONDS 12
/* that's bonds per atom! */

#define VANBUFSIZ 10000

#define iabs(x) (x<0 ? -(x) : x)
#define min(x,y) (x<y ? x : y)
#define max(x,y) (x>y ? x : y)

#define PICOSEC (1e-12)

/** A space grid for locating non-bonded interactions */
#define SPWIDTH 128
#define SPMASK 127

/** table length for bond stretch/bending functions */
#define TABLEN 150

/** factor for a unit vector given length squared -- rtned in uf, i is temp */
#define UFTLEN 200
/** */
#define UFSTART 10000.0
/** */
#define UFSCALE 300
/*
#define ufac(uf,i,rsq) {uf=rsq; i=(int)(uf-UFSTART)/UFSCALE; \
                        if (i<0 || i>UFTLEN) uf=1.0/sqrt(uf);\
                        else uf=uft1[i]+uf*uft2[i];}
*/
#define ufac(uf,i,rsq) (uf=1.0/sqrt(uf))

/* bond type is a number that encodes the atom types and order
   maintained in numerical order in the following table */
#define bontyp(ord,a1,a2) (a1<=a2 ? ord*10000 + a1*100 + a2 : \
                                  -(ord*10000 + a2*100 + a1))
//#define bondrec(ord,a1,a2,ks,len,de,beta) {bontyp(ord,a1,a2),\
    //          ord,a1,a2,ks,len,de,beta*1e-2, 0.0, NULL, 0}
#define bondrec(a1,a2,ks,len,de,beta) {bontyp(1,a1,a2),\
          1,a1,a2,ks,len,de,beta*1e-2, 0.0, NULL, 0}

/** atoms.  old, new, cur, and force are parallel to atoms */
struct A {
    int elt,nbonds;
    int bonds[NBONDS]; // index into bond[]
    //int part, disp;         /* which part its in, how to show */
    double massacc;         /* times force to get acceleration */
    double energ, vlim;             /* thermostat factors */
    struct A *next, **bucket;       /* sep chaining for space buckets */
    struct AXLE *constraint;        /* only one per atom */
};

/* a (stretch) bond.   */
/* r points from an2 to an1 */
struct B {
    int an1, an2; // index into atom[]
    char order;
    double invlen;
    struct bondStretch *type;
    struct xyz r, ru;        /* bond vector, unit version threreof */
    struct xyz aff;     /* axial force */
    //struct xyz bff;     /* bending force */
};
/* note that the bending "force" is a torque pair, e.g. +bff applies
   to an1 and -bff to an2 (and aff is a linear pair likewise) */


/* a bending bond -- points to two bonds */
/* dirX is 1 if bX->an1 is the common atom */
struct Q {
    struct B *b1, *b2; // this torque is made up from two entries in bond[]
    int dir1, dir2;
    int a1, a2, ac; // index into atom[]

    /** kb in pN/rad */
    //double kb1, kb2; // should be in type, right?
    /** in radians */
    //double theta0; // should be in type, right?

    struct bendData *type;
};

/* van der Waals forces */

struct vdWi {
        /** the atoms involved */
        int a1, a2;
        /** the lookup table for the fn */
        struct interpolationTable *table;
        struct vdWi *next;
};

struct vdWbuf {
        struct vdWi item[VANBUFSIZ];
        int fill;
        struct vdWbuf *next;
};
struct vdWbuf vanderRoot;

struct interpolationTable {
    double start;
    int scale;
    double t1[TABLEN];
    double t2[TABLEN];
};

#include "printers.h"
#include "newtables.h"

// number of atoms a jig can hold
#define NJATOMS 30

#define CODEground 0
#define CODEtemp 1
#define CODEstat 2
#define CODEmotor 3
#define CODEbearing 4
#define CODElmotor 5
#define CODEspring 6
#define CODEslider 7
#define CODEangle 8
#define CODEradius 9


/**
 * a "jig", motor, constraint, or instrument
 */
struct AXLE {
        /** see CODEs above  */
        int type;
        /** motor if there is one */
        struct MOT *motor;
        int natoms;
        /** atoms connected to the shaft */
        int atoms[NJATOMS];
    // string from file
    char *name;
    // a pun
    double temp, gamma;
    // whatever
    double data;
    struct xyz xdata;
};

/**
 * A motor
 */
struct MOT {
        /** point about which motor turns */
        struct xyz center;
        /** centers of rotation and radii */
        struct xyz atocent[NJATOMS], ator[NJATOMS];
        /** axis & frame of rotation, unit vectors */
        struct xyz axis, roty, rotz;
        /** atom positions about centers, */
        double radius[NJATOMS];
        /** in polar coords */
        double atang[NJATOMS];
        /** torque at zero speed, Dx^2 N * m */
        double stall;
        /** speed at zero torque, rad/Dt */
        double speed;
        /** previous angular position in radians */
        double theta0;
        /** current angular position in radians */
        double theta;
        /** angular inertia factor in Dt^2 / kg Dx */
        double moment;
};


/* set to 1 when a SIGTERM is caught */
extern int Interrupted;
extern int Nexbon;
extern int Nextorq;
extern int Nexatom;
extern struct xyz Force[];
extern struct xyz OldForce[];
extern struct xyz AveragePositions[];
extern struct xyz *OldPositions;
extern struct xyz *NewPositions;
extern struct xyz *Positions;
extern struct xyz *BestPositions;
extern struct xyz *BasePositions;
extern struct xyz *InitialPositions;
extern struct xyz Center;
extern struct xyz Bbox[2];
extern struct A atom[];
extern struct B bond[];
extern struct Q torq[];
extern int Iteration;
extern double RvdW;
extern double EvdW;
extern struct vdWbuf *Nexvanbuf;
extern struct vdWbuf *Dynobuf;
extern int Dynoix;
extern struct A *Space[SPWIDTH][SPWIDTH][SPWIDTH];
extern int Nexcon;
extern struct AXLE Constraint[];
extern int Nexmot;
extern struct MOT Motor[];
extern double Dt;
extern double Dx;
extern double Temperature;
extern double Boltz;
extern double TotalKE;
extern double FoundKE;
extern double Pi;
extern double Kb;
extern double Ks;
extern double De;
extern double Tq;
extern double Beta;
extern double R0;
extern double R1;
extern double Theta0;
extern double totMass;
extern struct xyz Cog;
extern struct xyz P;
extern struct xyz Omega;


/* command line options */

extern int ToMinimize;
extern int IterPerFrame;
extern int NumFrames;
extern int DumpAsText;
extern int DumpIntermediateText;
extern int PrintFrameNums;
extern int OutputFormat;
extern int KeyRecordInterval;
extern char *IDKey;

extern char OutFileName[];
extern char TraceFileName[];

extern FILE *outf;
extern FILE *tracef;

/* XXX are these really needed? */
extern int PartNo;
extern int DisplayStyle;


extern double gavss(double v);
extern struct xyz gxyz(double v);
extern struct xyz sxyz(double *v);

extern int Count;
extern void findnobo(struct xyz *position, int a1);


/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
