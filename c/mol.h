#ifndef USING_GL
#define USING_GL 1
#endif

#if !USING_GL
typedef double GLfloat;
#else
#include <GL/glut.h>
#endif


#define SCRWID 640
#define SCRHIT 480

#define NATOMS 10000
#define NBONDS 12
/* that's bonds per atom! */

#define NUMELTS 37

#define VANBUFSIZ 10000

#define iabs(x) (x<0 ? -(x) : x)
#define min(x,y) (x<y ? x : y)
#define max(x,y) (x>y ? x : y)

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

/** table length for bond stretch/bending functions */
#define TABLEN 150

/** factor for a unit vector given length squared -- rtned in uf, i is temp */
#define UFTLEN 200
/** */
#define UFSTART 10000.0
/** */
#define UFSCALE 300
/** */
#define ufac(uf,i,rsq) {uf=rsq; i=(int)(uf-UFSTART)/UFSCALE; \
                        if (i<0 || i>UFTLEN) uf=1.0/sqrt(uf);\
                        else uf=uft1[i]+uf*uft2[i];}

/* bond type is a number that encodes the atom types and order
   maintained in numerical order in the following table */
#define bontyp(ord,a1,a2) (a1<=a2 ? ord*10000 + a1*100 + a2 : \
                                   -(ord*10000 + a2*100 + a1))
#define bondrec(ord,a1,a2,ks,len,de,beta) {bontyp(ord,a1,a2),\
          ord,a1,a2,ks,len,de,beta*1e-2, 0.0, NULL, 0}

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
	int part, disp;		/* which part its in, how to show */
	double massacc;     	/* times force to get acceleration */
	double energ, vlim;	        /* thermostat factors */
	struct A *next, **bucket;	/* sep chaining for space buckets */
	struct AXLE *constraint;	/* only one per atom */
};

/* a (stretch) bond.   */
/* r points from an2 to an1 */
struct B {
	int an1, an2, order;
	struct bsdata *type;
	struct xyz r, ru;        /* bond vector, unit version threreof */
	struct xyz aff, bff;     /* axial force,  bending force */
};
/* note that the bending "force" is a torque pair, e.g. +bff applies
   to an1 and -bff to an2 (and aff is a linear pair likewise) */

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
	/** for display */
	GLfloat color[4];
};

struct dtab {			/* two interpolation tables */
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
	/** interpolation table stuff */
	double start;
	struct dtab *tab1, *tab2;
	int scale;
};

#define benrec(a1,o1,ac,o2,a2,kb,th) {bontyp(o1,ac,a1),bontyp(o2,ac,a2),\
                                 kb*6.36e-2,  th, 0.0, NULL, NULL, 0}

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

#define MAX_ATOMS_PER_AXLE 25

/**
 * External rotational constraint, either an anchor or a motor
 */
struct AXLE {
	/** 0= fixed, 1=motor */
	int type;
	/** motor if there is one */
	struct MOT *motor;
	int natoms;
	/** atoms connected to the shaft */
	int atoms[MAX_ATOMS_PER_AXLE];
};

/**
 * A motor
 */
struct MOT {
	/** point about which motor turns */
	struct xyz center;
	/** centers of rotation and radii */
	struct xyz atocent[MAX_ATOMS_PER_AXLE], ator[MAX_ATOMS_PER_AXLE];
	/** axis & frame of rotation, unit vectors */
	struct xyz axis, roty, rotz;
	/** atom positions about centers, */
	double radius[MAX_ATOMS_PER_AXLE];
	/** in polar coords */
	double atang[MAX_ATOMS_PER_AXLE];
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
extern struct xyz pos[3*10000];
extern struct xyz f;
extern struct xyz force[10000];
extern struct xyz avg[10000];
extern struct xyz *old;
extern struct xyz *new;
extern struct xyz *cur;
extern struct xyz *tmp;
extern struct xyz Center;
extern struct xyz Bbox[2];
extern struct xyz diam[5];
extern int PartNo;
extern int DisplayStyle;
extern struct A atom[10000];
extern struct B bond[4*10000];
extern struct Q torq[6*10000];
extern struct atomtype element[37];
extern char *elname[37];
extern struct bsdata bstab[];
extern void pbontyp(struct bsdata *ab);
extern int Iteration;
extern void bondump(void);
extern struct angben bendata[];
extern void pangben(struct angben *ab);
extern int findbond(int btyp);
extern int findtorq(int btyp1, int btyp2);
extern struct vdWtab vanderTable[(37 * (37 +1))/2];
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
extern double Beta;
extern double R0;
extern double R1;
extern double Theta0;
extern double totMass;
extern struct xyz Cog;
extern struct xyz P;
extern struct xyz Omega;
extern void speedump(void);
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
extern void pv(struct xyz foo);
extern void pvt(struct xyz foo);
extern void pa(int i);
extern void checkatom(int i);
extern void pb(int i);
extern void pq(int i);
extern void pvdw(struct vdWbuf *buf, int n);
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
extern void pcon(int i);
extern void filred(char *filnam);
extern int ShotNo;
extern void calcloop(int iters);
extern void minimize(void);
extern void keyboard(unsigned char key, int x, int y);
extern int main(int argc, char **argv);

/* display.c */
extern void display(void);
extern void init(void);
extern void snapshot(void);
extern void display_init(int *argc, char *argv[]);
extern void display_mainloop(void);

/* lin-alg.c */
extern struct xyz vcon(double x);
extern struct xyz vsum(struct xyz v, struct xyz w);
extern struct xyz vdif(struct xyz v, struct xyz w);
extern double vlen(struct xyz v);
extern struct xyz uvec(struct xyz v);
extern double vang(struct xyz v, struct xyz w);
extern struct xyz vx(struct xyz v, struct xyz w);

/*
 * Local Variables:
 * c-basic-offset: 8
 * tab-width: 8
 * End:
 */
