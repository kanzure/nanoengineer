// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.

#if 0
#define DBGPRINTF(x...) fprintf(stderr, ## x)
#else
#define DBGPRINTF(x...) ((void) 0)
#endif

extern int debug_flags;
#define DEBUG(flag) (debug_flags & (flag))
#define DPRINT(flag, x...) (DEBUG(flag) ? fprintf(stderr, ## x) : (void) 0)

#define D_TABLE_BOUNDS    (1<<0)
#define D_READER          (1<<1)
#define D_MINIMIZE        (1<<2)

/* should probably do varargs here so we can do printf like stuff */
extern FILE *tracef;
#define ERROR(s) (printError(tracef, s))
#define WARNING(s) (printWarning(tracef, s))

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
/** vector addition (incremental: add src to dest) */
#define vadd(dest,src) dest.x+=src.x; dest.y+=src.y; dest.z+=src.z
/** vector addition (non-incremental) */
#define vadd2(dest,src1,src2) dest.x=src1.x+src2.x; \
    dest.y=src1.y+src2.y; dest.z=src1.z+src2.z
/** vector subtraction (incremental: subtract src from dest) */
#define vsub(dest,src) dest.x-=src.x; dest.y-=src.y; dest.z-=src.z
/** vector subtraction (non-incremental) */
#define vsub2(dest,src1,src2) dest.x=src1.x-src2.x; \
    dest.y=src1.y-src2.y; dest.z=src1.z-src2.z
/** */
#define vmul(dest,src) dest.x*=src.x; dest.y*=src.y; dest.z*=src.z
/** */
#define vmul2(dest,src1,src2) dest.x=src1.x*src2.x; \
    dest.y=src1.y*src2.y; dest.z=src1.z*src2.z
/** */
#define vmul2c(dest,src1,src2) dest.x=src1.x*src2; \
    dest.y=src1.y*src2; dest.z=src1.z*src2
/** */
#define vmulc(dest,src) dest.x*=src; dest.y*=src; dest.z*=src

#define vdiv(dest,src) dest.x/=src.x; dest.y/=src.y; dest.z/=src.z
#define vdiv2(dest,src1,src2) dest.x=src1.x/src2.x; \
    dest.y=src1.y/src2.y; dest.z=src1.z/src2.z

/** */
#define vset(dest,src) dest.x=src.x; dest.y=src.y; dest.z=src.z
/** */
#define vsetc(dest,src) dest.x=src; dest.y=src; dest.z=src
/** */
#define vsetn(dest,src) dest.x= -src.x; dest.y= -src.y; dest.z= -src.z

/** */
#define vmin(dest,src) dest.x = min(dest.x,src.x); \
    dest.y = min(dest.y,src.y); dest.z = min(dest.z,src.z);
/** */
#define vmax(dest,src) dest.x = max(dest.x,src.x); \
    dest.y = max(dest.y,src.y); dest.z = max(dest.z,src.z);

/** */
#define vdot(src1,src2) (src1.x*src2.x+src1.y*src2.y+src1.z*src2.z)
// cross product
#define v2x(dest,src1,src2)  dest.x = src1.y * src2.z - src1.z * src2.y;\
	dest.y = src1.z * src2.x - src1.x * src2.z;\
	dest.z = src1.x * src2.y - src1.y * src2.x;

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

/* a 3-vector */
struct xyz {
        double x;
        double y;
        double z;
};

/** atoms.  old, new, cur, and force are parallel to atoms */
struct A {
        int elt,nbonds;
        int bonds[NBONDS];
        int part, disp;         /* which part its in, how to show */
        double massacc;         /* times force to get acceleration */
        double energ, vlim;             /* thermostat factors */
        struct A *next, **bucket;       /* sep chaining for space buckets */
        struct AXLE *constraint;        /* only one per atom */
};

/* a (stretch) bond.   */
/* r points from an2 to an1 */
struct B {
    int an1, an2, order;
    double invlen;
    struct bsdata *type;
    struct xyz r, ru;        /* bond vector, unit version threreof */
    struct xyz aff;     /* axial force */
    //struct xyz bff;     /* bending force */
};
/* note that the bending "force" is a torque pair, e.g. +bff applies
   to an1 and -bff to an2 (and aff is a linear pair likewise) */


/* a bending bond -- points to two bonds */
/* dirX is 1 if bX->an1 is the common atom */
struct Q {
    struct B *b1, *b2;
    int dir1, dir2;
    int a1, a2, ac;

    /** kb in pN/rad */
    double kb1, kb2;
    /** in radians */
    double theta0;

    struct angben *type;
};


/* indexed by element number */
struct atomtype {
        /** in 1e-27 kg */
        double mass;
        /** in Angstroms */
        double rvdw;
        /** in zJ */
        double evdw;
        /** number of bonds */
        int nbonds;
        /** element's symbol on periodic table */
        char *symbol;
};

struct dtab {                   /* two interpolation tables */
        double  t1[TABLEN], t2[TABLEN];
};

/* data for a stretch bond type */
struct bsdata {
        /** bond type, atom types & order */
        int typ, ord, a1, a2;
        /** stiffness N/m */
        double ks;
        /** base radius  pm */
        double r0;
        /** Morse/Lippincott PE parameters */
        double de,beta;
        /** interpolation table stuff */
        double start;
        struct dtab *table;
        int scale;
};

/* bond angle bending data */



struct angben {
        /** bondtypes, negative if bond's a2 is common */
        int b1typ, b2typ;
        /** kb in N/m */
        double kb;
        /** in radians */
        double theta0;
};

/*
#define benrec(a1,o1,ac,o2,a2,kb,th) {bontyp(o1,ac,a1),bontyp(o2,ac,a2),\
                                 kb*6.36e-2,  th, 0.0, NULL, NULL, 0}
*/
// convert Ktheta from zJ to yJ, see 
#define benrec(a1,ac,a2,kb,th) {bontyp(1,ac,a1),bontyp(1,ac,a2),\
                                 kb*1000.0,  th}

/* van der Waals forces */

struct vdWi {
        /** the atoms involved */
        int a1, a2;
        /** the lookup table for the fn */
        struct vdWtab *table;
        struct vdWi *next;
};

struct vdWbuf {
        struct vdWi item[VANBUFSIZ];
        int fill;
        struct vdWbuf *next;
};
struct vdWbuf vanderRoot;

struct vdWtab {
        double start;
        int scale;
        struct dtab table;
};

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


/* mol.c */
extern struct vdWbuf vanderRoot;
extern int Nexbon;
extern int Nextorq;
extern int Nexatom;
extern double uft1[200];
extern double uft2[200];
extern double uffunc(double uf);
//extern struct xyz f;
extern struct xyz force[];
extern struct xyz average_positions[];
extern struct xyz *old_positions;
extern struct xyz *new_positions;
extern struct xyz *positions;
extern struct xyz Center;
extern struct xyz Bbox[2];
extern struct xyz diam[5];
extern int PartNo;
extern int DisplayStyle;
extern struct A atom[];
extern struct B bond[];
extern struct Q torq[];
// extern char *elname[37];
extern void pbontyp(FILE *f, struct bsdata *ab);
extern int Iteration;
extern void bondump(FILE *f);
extern void pangben(FILE *f, struct angben *ab);
extern int findbond(int btyp);
extern int findtorq(int btyp1, int btyp2);
// extern struct vdWtab vanderTable[(37 * (37 +1))/2];
extern struct vdWtab vanderTable[];
extern double RvdW;
extern double EvdW;
extern struct vdWbuf *Nexvanbuf;
extern struct vdWbuf *Dynobuf;
extern int Dynoix;
extern struct A *Space[128][128][128];
extern void orion(void);
extern int Nexcon;
extern struct AXLE Constraint[100];
extern int Nexmot;
extern struct MOT Motor[100];
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
extern void speedump(FILE *f);
extern double t1[150];
extern double t2[150];
extern double start;
extern int scale;
extern void maktab(double *t1, double *t2, double func(double), double start, int length, int scale);
extern double bender(double rsq);
extern double hooke(double rsq);
extern double lippmor(double rsq);
extern double bucking(double rsq);
extern double square(double x);
extern void bondinit(void);
extern void vdWsetup(void);
extern double gavss(double v);
extern struct xyz gxyz(double v);
extern struct xyz sxyz(double *v);
extern void pv(FILE *f, struct xyz foo);
extern void pvt(FILE *f, struct xyz foo);
extern void pa(FILE *f, int i);
extern void checkatom(FILE *f, int i);
extern void pb(FILE *f, int i);
extern void printAllBonds(FILE *f);
extern void printError(FILE *f, char *s);
extern void printWarning(FILE *f, char *s);
extern void doneExit(FILE *f, char *s, int exitvalue);
extern void pq(FILE *f, int i);
extern void pvdw(FILE *f, struct vdWbuf *buf, int n);
extern void makatom(int elem, struct xyz posn);
extern void makbon0(int a, int b, int ord);
extern void makbon1(int n);
extern void maktorq(int a, int b);
extern void makvdw(int a1, int a2);
extern int Count;
extern void findnobo(int a1);
extern void makvander0(int a1, int a2);
extern void makvander1(struct vdWbuf *buf, int n);
extern int makcon(int typ, struct MOT *mot, int n, int *atnos);
extern struct MOT *makmot(double stall, double speed, struct xyz vec1, struct xyz vec2);
extern void makmot2(int i);
extern void pcon(FILE *f, int i);
extern void filred(char *filnam);
extern int ShotNo;
extern void calcloop(int iters);
extern void minimize(int NumFrames);
extern void keyboard(unsigned char key, int x, int y);
extern int main(int argc, char **argv);

/* display.c */
extern void display(void);
extern void init(void);
extern void snapshot(int n);
extern void display_init(int *argc, char *argv[]);
extern void display_mainloop(void);

/* lin-alg.c */
extern struct xyz vcon(double x);
extern struct xyz vsum(struct xyz v, struct xyz w);
extern struct xyz vdif(struct xyz v, struct xyz w);
struct xyz vprod(struct xyz v, struct xyz w);
struct xyz vprodc(struct xyz v, double w);
extern double vlen(struct xyz v);
extern struct xyz uvec(struct xyz v);
extern double vang(struct xyz v, struct xyz w);
extern struct xyz vx(struct xyz v, struct xyz w);

/* tables */
extern struct atomtype element[];
extern struct bsdata bstab[];
extern struct angben bendata[];
extern const int NUMELTS;
extern const int BSTABSIZE;
extern const int BENDATASIZE;


/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
