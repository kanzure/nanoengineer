#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <GL/glut.h>


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

#define vadd(dest,src) dest.x+=src.x; dest.y+=src.y; dest.z+=src.z
#define vadd2(dest,src1,src2) dest.x=src1.x+src2.x; \
    dest.y=src1.y+src2.y; dest.z=src1.z+src2.z
#define vsub(dest,src) dest.x-=src.x; dest.y-=src.y; dest.z-=src.z
#define vsub2(dest,src1,src2) dest.x=src1.x-src2.x; \
    dest.y=src1.y-src2.y; dest.z=src1.z-src2.z
#define vmul(dest,src) dest.x*=src.x; dest.y*=src.y; dest.z*=src.z
#define vmul2(dest,src1,src2) dest.x=src1.x*src2.x; \
    dest.y=src1.y*src2.y; dest.z=src1.z*src2.z
#define vmul2c(dest,src1,src2) dest.x=src1.x*src2; \
    dest.y=src1.y*src2; dest.z=src1.z*src2
#define vmulc(dest,src) dest.x*=src; dest.y*=src; dest.z*=src

#define vset(dest,src) dest.x=src.x; dest.y=src.y; dest.z=src.z
#define vsetc(dest,src) dest.x=src; dest.y=src; dest.z=src
#define vsetn(dest,src) dest.x= -src.x; dest.y= -src.y; dest.z= -src.z

#define vmin(dest,src) dest.x = min(dest.x,src.x); \
    dest.y = min(dest.y,src.y); dest.z = min(dest.z,src.z);
#define vmax(dest,src) dest.x = max(dest.x,src.x); \
    dest.y = max(dest.y,src.y); dest.z = max(dest.z,src.z);

#define vdot(src1,src2) (src1.x*src2.x+src1.y*src2.y+src1.z*src2.z)

/* table length for bond stretch/bending functions */
#define TABLEN 150

/* factor for a unit vector given length squared -- rtned in uf, i is temp */
#define UFTLEN 200
#define UFSTART 10000.0
#define UFSCALE 300
#define ufac(uf,i,rsq) {uf=rsq; i=(int)(uf-UFSTART)/UFSCALE; \
                        if (i<0 || i>UFTLEN) uf=1.0/sqrt(uf);\
                        else uf=uft1[i]+uf*uft2[i];}

/* tables and setup function for same */
double uft1[UFTLEN], uft2[UFTLEN];
  
double uffunc(double uf) {
  return 1.0/sqrt(uf);
}

/* indicate next avail/total number of stretch bonds, bend bonds, and atoms */
int Nexbon=0, Nextorq=0, Nexatom=0;

/* a 3-vector */
struct xyz {
  double x,y,z;};
/* positions and forces on the atoms w/pointers into pos */
struct xyz pos[3*NATOMS], f, force[NATOMS], avg[NATOMS];
struct xyz *old, *new, *cur, *tmp;

struct xyz Center, Bbox[2];
  
/* data for the 5-carbon test molecule */
struct xyz diam[5]={{0.0, 0.0, 0.0},
		    {176.7, 176.7, 0.0},
		    {176.7, 0.0, 176.7},
		    {0.0, 176.7, 176.7},
		    {88.33, 88.33, 88.33}};

/* some linear-algebra functions */


struct xyz vcon(double x) {
  struct xyz u;
  vsetc(u,x);
  return u;
}


struct xyz vsum(struct xyz v, struct xyz w) {
  struct xyz u;
  vadd2(u,v,w);
  return u;
}

struct xyz vdif(struct xyz v, struct xyz w) {
  struct xyz u;
  vsub2(u,v,w);
  return u;
}

double vlen(struct xyz v) {	/* length of a vector */
  return sqrt(vdot(v,v));
}

struct xyz uvec(struct xyz v) {	/* unit vector in given direction */
  struct xyz w;
  double rlen;
  rlen=1.0/vlen(v);
  vmul2c(w,v,rlen);
  return w;
}

double vang(struct xyz v, struct xyz w) {
  struct xyz u1, u2;
  u1=uvec(v);
  u2=uvec(w);
  return acos(vdot(u1,u2));
}

struct xyz vx(struct xyz v, struct xyz w) {
  struct xyz u;
  u.x = v.y * w.z - v.z * w.y;
  u.y = v.z * w.x - v.x * w.z;
  u.z = v.x * w.y - v.y * w.x;
  return u;
}

int PartNo=0, DisplayStyle=1;	/* 0 nothing, 1 ball/stick, 2 vdW surface */

/* atoms.  old, new, cur, and force are parallel to atoms */
  struct A {
    int elt,nbonds;
    int bonds[NBONDS];
    int part, disp;		/* which part its in, how to show */
    double massacc;     	/* times force to get acceleration */
    double energ, vlim;	        /* thermostat factors */
    struct A *next, **bucket;	/* sep chaining for space buckets */
    struct XTR *constraint;	/* only one per atom */
  };
  struct A atom[NATOMS];

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

  struct B bond[4*NATOMS];

/* a bending bond -- points to two bonds */
/* dirX is 1 if bX->an1 is the common atom */ 
  struct Q {
    struct B *b1, *b2;
    int dir1, dir2;
    int a1, a2, ac;
    struct angben *type;
  };
  struct Q torq[6*NATOMS];

/* indexed by element number */
struct atomtype {
  double mass; 			/* in 1e-27 kg */
  double rvdw;			/* in Angstroms */
  double evdw;			/* in zJ */
  int nbonds;			/* number of bonds */
  GLfloat color[4];		/* for display */
};
struct atomtype element[NUMELTS]={
  {0.001,  1.0,  0.130, 1, {0.0, 0.0, 0.0, 1.0}},     /*  0 Lone Pair */
  {1.674, 0.79,  0.382, 1, {0.0, 0.6, 0.6, 1.0}},     /*  1 Hydrogen */
  {6.646,  1.4,  0.666, 0, {1.0, 0.27, 0.67, 1.0}},   /*  2 Helium */
  {11.525, 4.0,  0.666, 1, {0.0, 0.5, 0.5, 1.0}},     /*  3 Lithium */
  {14.964, 3.0,  0.666, 2, {0.98, 0.67, 1.0, 1.0}},   /*  4 Beryllium */
  {17.949, 2.0,  0.666, 3, {0.3, 0.3, 1.0, 1.0}},     /*  5 Boron */
  {19.925, 1.84, 0.357, 4, {0.22, 0.35, 0.18, 1.0}},  /*  6 Carbon */
  {23.257, 1.55, 0.447, 5, {0.84, 0.37, 1.0, 1.0}},   /*  7 Nitrogen */
  {26.565, 1.74, 0.406, 2, {0.6, 0.2, 0.2, 1.0}},     /*  8 Oxygen */
  {31.545, 1.65, 0.634, 1, {0.0, 0.8, 0.34, 1.0}},    /*  9 Fluorine */
  {33.49,  1.82, 0.666, 0, {0.92, 0.25, 0.62, 1.0}},  /* 10 Neon */
  {38.173, 4.0,  1.666, 1, {0.0, 0.4, 0.4, 1.0}},     /* 11 Sodium */
  {40.356, 3.0,  1.666, 2, {0.88, 0.6, 0.9, 1.0}},    /* 12 Magnesium */
  {44.800, 2.5,  1.666, 3, {0.5, 0.5, 0.9, 1.0}},     /* 13 Aluminum */
  {46.624, 2.25, 1.137, 4, {0.37, 0.45, 0.33, 1.0}},  /* 14 Silicon */
  {51.429, 2.11, 1.365, 5, {0.73, 0.32, 0.87, 1.0}},  /* 15 Phosphorus */
  {53.233, 2.11, 1.641, 6, {1.0, 0.65, 0.0, 1.0}},    /* 16 Sulfur */
  {58.867, 2.03, 1.950, 1, {0.34, 0.68, 0.0, 1.0}},   /* 17 Chlorine */
  {66.33,  1.88, 1.666, 0, {0.85, 0.24, 0.57, 1.0}},  /* 18 Argon */
  {64.926, 5.0,  2.666, 1, {0.0, 0.3, 0.3, 1.0}},     /* 19 Potassium */
  {66.549, 4.0,  2.666, 2, {0.79, 0.55, 0.8, 1.0}},   /* 20 Calcium */
  {74.646, 3.7,  2.666, 3, {0.42, 0.42, 0.51, 1.0}},  /* 21 Scandium */
  {79.534, 3.5,  2.666, 4, {0.42, 0.42, 0.51, 1.0}},  /* 22 Titanium */
  {84.584, 3.3,  2.666, 5, {0.42, 0.42, 0.51, 1.0}},  /* 23 Vanadium */
  {86.335, 3.1,  2.666, 6, {0.42, 0.42, 0.51, 1.0}},  /* 24 Chromium */
  {91.22,  3.0,  2.666, 7, {0.42, 0.42, 0.51, 1.0}},  /* 25 Manganese */
  {92.729, 3.0,  2.666, 3, {0.42, 0.42, 0.51, 1.0}},  /* 26 Iron */
  {97.854, 3.0,  2.666, 3, {0.42, 0.42, 0.51, 1.0}},  /* 27 Cobalt */
  {97.483, 3.0,  2.666, 3, {0.42, 0.42, 0.51, 1.0}},  /* 28 Nickel */
  {105.513, 3.0, 2.666, 2, {0.42, 0.42, 0.51, 1.0}},  /* 29 Copper */
  {108.541, 2.9, 2.666, 2, {0.42, 0.42, 0.51, 1.0}},  /* 30 Zinc */
  {115.764, 2.7, 2.666, 3, {0.6, 0.6, 0.8, 1.0}},     /* 31 Gallium */
  {120.53,  2.5, 2.666, 4, {0.45, 0.49, 0.42, 1.0}},  /* 32 Germanium */
  {124.401, 2.2, 2.666, 5, {0.6, 0.26, 0.7, 1.0}},    /* 33 Arsenic */
  {131.106, 2.1, 2.666, 6, {0.9, 0.35, 0.0, 1.0}},    /* 34 Selenium */
  {132.674, 2.0, 2.599, 1, {0.0, 0.5, 0.0, 1.0}},     /* 35 Bromine */
  {134.429, 1.9, 2.666, 0, {0.78, 0.21, 0.53, 1.0}}   /* 36 Krypton */
};

/* NB! all the Evdw that end in .666 are unknown */

char *elname[NUMELTS]={"LP","H","He","Li","Be","B","C","N","O","F","Ne",
		       "Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca",
		       "Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu",
		       "Zn","Ga","Ge","As","Se""Br","Kr"};

struct dtab {			/* two interpolation tables */
  double  t1[TABLEN], t2[TABLEN];
};

/* data for a stretch bond type */
struct bsdata {
  int typ, ord, a1, a2;		/* bond type, atom types & order */
  double ks;			/* stiffness N/m */
  double r0;			/* base radius  pm */
  double de,beta;		/* Morse/Lippincott PE parameters */
  double start;	                /* interpolation table stuff */
  struct dtab *table;
  int scale;
};

/* bond type is a number that encodes the atom types and order
   maintained in numerical order in the following table */
#define bontyp(ord,a1,a2) (a1<=a2 ? ord*10000 + a1*100 + a2 : \
                                   -(ord*10000 + a2*100 + a1))
#define bondrec(ord,a1,a2,ks,len,de,beta) {bontyp(ord,a1,a2),\
          ord,a1,a2,ks,len,de,beta*1e-2, 0.0, NULL, 0}

struct bsdata bstab[]={
  bondrec(1,1,6,  460.0, 111.3, 0.671, 1.851),	/* H-C */
  bondrec(1,1,7,  460.0, 102.3, 0.721, 1.851),	/* H-N XXX */
  bondrec(1,1,8,  460.0,  94.2, 0.753, 1.747),	/* H-O */
  bondrec(1,1,14, 360.0, 125.6, 0.753, 1.747),	/* H-Si XXX */
  bondrec(1,1,16, 360.0, 125.2, 0.753, 1.747),	/* H-S XXX */
  bondrec(1,6,6,  440.0, 152.3, 0.556, 1.989),	/* C-C */
  bondrec(1,6,7,  510.0, 143.8, 0.509, 2.238),	/* C-N */
  bondrec(1,6,8,  536.0, 140.2, 0.575, 2.159),	/* C-O */
  bondrec(1,6,9,  510.0, 139.2, 0.887, 1.695),	/* C-F */
  bondrec(1,6,14, 297.0, 188.0, 0.624, 1.543),	/* C-Si */
  bondrec(1,6,15, 291.0, 185.6, 0.624, 1.543),	/* C-P XXX */
  bondrec(1,6,16, 321.3, 181.5, 0.539, 1.726),	/* C-S */
  bondrec(1,6,17, 323.0, 179.5, 0.591, 1.653),	/* C-Cl */
  bondrec(1,6,35, 230.0, 194.9, 0.488, 1.536),	/* C-Br */
  bondrec(1,7,7,  560.0, 138.1, 0.417, 2.592),	/* N-N */
  bondrec(1,7,8,  670.0, 142.0, 0.350, 3.200),	/* N-O XXX */
  bondrec(1,8,8,  781.0, 147.0, 0.272, 3.789),	/* O-O */
  bondrec(1,14,14,185.0, 233.2, 0.559, 1.286),	/* Si-Si */
  bondrec(1,14,16,185.0, 233.2, 0.559, 1.286),	/* Si-S  XXX */
  /* double bonds */
  bondrec(2,6,6,  960.0, 133.7, 1.207, 1.994),	/* C=C */
  bondrec(2,6,8, 1080.0, 120.8, 1.300, 2.160),	/* C=O XXX */
  bondrec(2,6,16, 321.3, 171.5, 1.150, 1.750),	/* C=S */
  /* triple bonds */
  bondrec(3,6,6, 1560.0, 121.2, 1.614, 2.198),	/* C~C */
  /* aromatic bonds */
  bondrec(4,1,6,  465.0, 108.3, 0.700, 1.850),	/* H-C XXX */
  bondrec(4,6,6,  660.0, 142.1, 0.800, 2.000),	/* C-C XXX */
  bondrec(4,6,7,  515.0, 135.2, 0.530, 2.250),	/* C-N XXX */
  bondrec(4,6,8,  536.0, 136.2, 0.900, 2.160),	/* C-O XXX */
  bondrec(4,6,9,  510.0, 139.2, 0.900, 1.700),	/* C-F XXX */
  bondrec(4,6,16, 321.3, 173.5, 0.800, 1.750),	/* C-S XXX */

  bondrec(10,0,0, 0.0, 0.0, 0.0, 0.0)		/* end record */
};
/* NB -- XXX means De and beta are guesses */


void pbontyp(struct bsdata *ab) {
  printf("Bond between %d / %d of order %d: type %d, length %f, stiffness %f\n table %d, start %f, scale %d\n",
	 ab->a1,ab->a2,ab->ord,ab->typ,ab->r0,ab->ks,
	 ab->table,ab->start,ab->scale);
  
}

int Iteration=0;
  

void bondump() {		/* gather bond statistics */
  int histo[50][23], totno[50], btyp, i, j, k, n;
  double r, perc, means[50];
  struct bsdata *bt;

  for (i=0; i<50; i++) {
    totno[i] = 0;
    means[i] = 0.0;
    for (j=0; j<23; j++)
      histo[i][j]=0;
  }
  
  for (i=0; i<Nexbon; i++) {
    bt=bond[i].type;
    btyp = bt-bstab;
    totno[btyp]++;
    r=vlen(vdif(cur[bond[i].an1], cur[bond[i].an2]));
    means[btyp] += r;
    perc = (r/bt->r0)*20.0 - 8.5;
    k=(int)perc;
    if (k<0) k=0;
    if (k>22) k=22;
    histo[btyp][k]++;
  }
  
  for (i=0; i<50; i++) if (totno[i]) {
    printf("Bond type %s-%s, %d occurences, mean %.2f pm:\n",
	   elname[bstab[i].a1], elname[bstab[i].a2], totno[i],
	   means[i]/(double)totno[i]);
    for (j=0; j<23; j++) {
      if ((j-1)%10) printf(" |");
      else printf("-+");
      n=(80*histo[i][j])/totno[i];
      if (histo[i][j] && n==0) printf(".");
      for (k=0; k<n; k++) printf("M");
      printf("\n");
    }}
  printf("Iteration %d\n",Iteration);
}


/* bond angle bending data */

struct angben {
  int b1typ, b2typ;	      /* bondtypes, negative if bond's a2 is common */
  double kb;	        	/* kb in N/m */
  double theta0;		/* in radians */
  double start;	                /* interpolation table stuff */
  struct dtab *tab1, *tab2;
  int scale;
};

#define benrec(a1,o1,ac,o2,a2,kb,th) {bontyp(o1,ac,a1),bontyp(o2,ac,a2),\
                                 kb*6.36e-2,  th, 0.0, NULL, NULL, 0}
struct angben bendata[]={
  benrec(6,1,6,1,6, 450, 1.911),	/* C-C-C */
  benrec(6,1,6,1,1, 360, 1.909),	/* C-C-H */
  benrec(1,1,6,1,1, 320, 1.909),	/* H-C-H */
  benrec(6,1,6,1,9, 650, 1.911),	/* C-C-F */
  benrec(9,1,6,1,9, 1070, 1.869),	/* F-C-F */
  benrec(6,4,6,4,6, 450, 2.046),	/* C-Csp2-C */
  benrec(6,1,6,2,6, 550, 2.119),	/* C-C=C */
  benrec(1,1,6,2,6, 360, 2.094),	/* C=C-H */
  benrec(6,1,6,3,6, 200, 3.142),	/* C-C-=C */
  benrec(6,1,6,2,8, 460, 2.138),	/* C-C=O */
  benrec(6,1,8,1,1, 770, 1.864),	/* C-O-H */
  benrec(6,1,8,1,6, 770, 1.864),	/* C-O-C */
  benrec(6,1,8,1,8, 770, 1.864),	/* C-O-O XXX */
  benrec(6,1,8,1,7, 770, 1.864),	/* C-O-N XXX */
  benrec(7,1,8,1,7, 770, 1.864),	/* N-O-N XXX */
  benrec(7,1,8,1,8, 770, 1.864),	/* N-O-O XXX */
  benrec(8,1,8,1,8, 770, 1.864),	/* O-O-O XXX */
  benrec(6,1,7,1,6, 630, 1.880),	/* C-N-C */
  benrec(6,1,7,1,7, 630, 1.880),	/* C-N-N XXX */
  benrec(6,1,7,1,8, 630, 1.880),	/* C-N-O XXX */
  benrec(7,1,7,1,7, 630, 1.880),	/* N-N-N XXX */
  benrec(6,1,6,1,8, 700, 1.876),	/* C-C-O */
  benrec(7,1,6,1,8, 630, 1.900),	/* N-C-O */
  benrec(7,1,7,1,8, 630, 1.900),	/* N-N-O XXX */
  benrec(8,1,7,1,8, 630, 1.900),	/* O-N-O XXX */
  benrec(7,1,6,1,16, 630, 1.900),	/* N-C-S XXX */
  benrec(6,1,6,1,7, 570, 1.911),	/* C-C-N */
  benrec(1,1,6,1,8, 600, 1.876),	/* H-C-O XXX */
  benrec(1,1,6,1,7, 470, 1.911),	/* H-C-N XXX */
  benrec(1,1,7,1,8, 600, 1.876),	/* H-N-O XXX */
  benrec(1,1,7,1,6, 470, 1.911),	/* H-N-C XXX */
  benrec(1,1,7,1,7, 470, 1.911),	/* H-N-N XXX */
  benrec(14,1,14,1,14, 350, 1.943),	/* Si-Si-Si */
  benrec(1,1,14,1,14, 350, 1.943),	/* H-Si-Si XXX */
  benrec(1,1,14,1,16, 350, 1.943),	/* H-Si-S XXX */
  benrec(16,1,14,1,16, 350, 1.943),	/* S-Si-S XXX */
  benrec(16,1,14,1,14, 350, 1.943),	/* S-Si-Si XXX */
  benrec(14,1,6,1,14, 400, 2.016),	/* Si-C-Si */
  benrec(6,1,14,1,6, 480, 1.934),	/* C-Si-C */
  benrec(17,1,6,1,17, 1080, 1.950),	/* Cl-C-Cl */
  benrec(6,1,6,1,16, 550, 1.902),	/* C-C-S */
  benrec(6,1,16,1,6, 720, 1.902),	/* C-S-C */
  benrec(14,1,16,1,14, 720, 1.902),	/* Si-S-Si XXX */

  benrec(10,10,10,10,10, 0, 0.0)        /* end record */
};

void pangben(struct angben *ab) {
  printf("Bend between %d / %d: kb=%.2f, th0=%.2f\n\
 --Table[%d]: %.0f by %d:  -->%.2f/%.4f,  -->%.2f/%.4f\n",
	 ab->b1typ,ab->b2typ,ab->kb,ab->theta0,
	 TABLEN,ab->start,ab->scale,
	 ab->tab1->t1[0],ab->tab1->t2[0],
	 ab->tab2->t1[0],ab->tab2->t2[0]);
}

int findbond(int btyp) {
  int i;
  if (btyp<0) btyp = - btyp;
  for (i=0; bstab[i].typ<btyp; i++);
  if (bstab[i].typ == btyp) return i;
  printf("Bond type %d not found\n",btyp);
  return -1;
}

int findtorq(int btyp1, int btyp2) {
  int i;
  for (i=0; bendata[i].b1typ<100000; i++) {

    if  (iabs(bendata[i].b1typ) == iabs(btyp1) &&
	 iabs(bendata[i].b2typ) == iabs(btyp2)) return i;
    if  (iabs(bendata[i].b1typ) == iabs(btyp2) &&
	 iabs(bendata[i].b2typ) == iabs(btyp1)) return i;
  }
  printf("Bend type %d-%d not found\n",btyp1,btyp2);
  return -1;
}

/* van der Waals forces */

struct vdWi {
  int a1, a2;			/* the atoms involved */
  struct vdWtab *table;		/* the lookup table for the fn */
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

/* the force between elt i and elt j (i<=j) is at
  vanderTable[i*(NUMELTS+1) - i*(i+1)/2 + j-i] */
struct vdWtab vanderTable[(NUMELTS * (NUMELTS+1))/2];

double RvdW, EvdW;

struct vdWbuf *Nexvanbuf, *Dynobuf;
int Dynoix;			/* start of dynamically found vdw's */

/* A space grid for locating non-bonded interactions */

#define SPWIDTH 128
#define SPMASK 127
struct A *Space[SPWIDTH][SPWIDTH][SPWIDTH];	/*  space buckets */

void orion() {			/* atoms in space :-) */
  int n, i,j,k;
  struct A **pail;


  for (n=0; n<Nexatom; n++) *atom[n].bucket = NULL;

  for (n=0; n<Nexatom; n++) {
    i= ((int)cur[n].x / 250) & SPMASK;
    j= ((int)cur[n].y / 250) & SPMASK;
    k= ((int)cur[n].z / 250) & SPMASK;
    pail = &Space[i][j][k];
    atom[n].next = *pail;
    *pail = atom+n;
    atom[n].bucket = pail;
  }

}


/* constraints */

int Nexcon=0;

struct XTR {
  int type;			/* 0= fixed, 1=motor */
  struct MOT *motor;		/* motor if there is one */
  int natoms;
  int atoms[25];		/* atoms connected to the shaft */
};
struct XTR Constraint[100];


/* motors: shoot for 5 nN/atom? speeds up to 10 m/s */

int Nexmot=0;

struct MOT {
  struct xyz center;		/* point about which motor turns */
  struct xyz atocent[25], ator[25]; /* centers of rotation and radii */
  struct xyz axis, roty, rotz;	/* axis & frame of rotation, unit vectors */
  double radius[25];		/* atom positions about centers, */
  double atang[25];	 	 /* in polar coords */
  double stall;			/* torque at zero speed, Dx^2 N * m */
  double speed;			/* speed at zero torque, rad/Dt */
  double theta0;		/* previous angular position in radians */
  double theta;			/* current angular position in radians */
  double moment;		/* angular inertia factor in Dt^2 / kg Dx */
};
struct MOT Motor[100];




/* constants: timestep (femtosecond), scale of distance (picometers) */
double Dt= 1e-16, Dx=1e-12;
double Temperature = 300.0;	/* Kelvins */
double Boltz = 1.38e-23;	/* k, in J/K */

double TotalKE = 0.0;		 /* actually double, = m_i v_i^2 */
double FoundKE = 0.0;

double Pi = 3.1415926;

/* values are for carbon and carbon-carbon bond (for testing) */

/* stiffnesses are in N/m, so forces come out in pN (i.e. Dx N) */
double Kb=28.63;		/* N/m */
double Ks=440.0;		/* N/m */
double De=0.556, Beta = 1.989e-2; /* Morse params */

/* pN/kg => acc in pm/s^2; mult by Dt^2 for pm/fs^2 */

double R0 = 152.3, R1 = 152.3, Theta0 = 1.911;

/* global properties: center of mass, momentum, moment of rotation */
double totMass=0.0;
struct xyz Cog, P, Omega;


void speedump() {		/* gather bond statistics */
  int histo[20], iv, i, j, k, n;
  double v, eng, toteng=0.0;

  for (i=0; i<21; i++) {
    histo[i]=0;
  }
  
  for (i=0; i<Nexatom; i++) {
    v=vlen(vdif(old[i],cur[i]));
    eng= atom[i].energ*v*v;
    toteng += eng;
    iv=(int)(eng*1e21);
    if (iv>20) iv=20;
    histo[iv]++;
  }
  
  printf("Kinetic energies:\n");
  for (j=0; j<21; j++) {
    if (j%5) printf(" |");
      else printf("-+");
      n=(70*histo[j])/Nexatom;
      if (histo[j] && n==0) printf(".");
      for (k=0; k<n; k++) printf("M");
      printf("\n");
  }
  printf("Iteration %d, KE %e --> %e\n",Iteration,TotalKE,FoundKE);
}


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

/* note -- uses global Ks and R0 */
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

  for (i=0; bstab[i].ord<10; i++) {

    R0 = bstab[i].r0;
    bstab[i].start = square(R0*0.5);
    end = square(R0*1.5);
    bstab[i].scale = (end - bstab[i].start) / TABLEN;
    Ks = bstab[i].ks;
    De = bstab[i].de;
    Beta = bstab[i].beta;
    tables = malloc(sizeof(struct dtab));
    maktab(tables->t1, tables->t2, lippmor,
	   bstab[i].start, TABLEN, bstab[i].scale);
    bstab[i].table = tables;
  }

  for (i=0;bendata[i].b1typ<100000;i++) {
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

  /* kT @ 300K is 4.14 zJ -- RMS V of carbon is 1117 m/s
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

void pv(struct xyz foo) {
  printf("(%.2f, %.2f, %.2f)",foo.x, foo.y, foo.z);
}
void pvt(struct xyz foo) {
  printf("(%.2f, %.2f, %.2f)\n",foo.x, foo.y, foo.z);
}

void pa(int i) {
  int j, b, ba;
  double v;

  if (i<0 || i>=Nexatom) printf("bad atom number %d\n",i);
  else {
    printf("atom %s%d (%d bonds): ", elname[atom[i].elt], i, atom[i].nbonds);
    for (j=0; j<atom[i].nbonds; j++) {
      b=atom[i].bonds[j];
      ba=(i==bond[b].an1 ? bond[b].an2 : bond[b].an1);
      printf("[%d/%d]: %s%d, ", b, bond[b].order,
	     elname[atom[ba].elt], ba);
    }
    v=vlen(vdif(cur[i],old[i]));
    printf("\n   V=%.2f, mV^2=%.6f, pos=", v,1e-4*v*v/atom[i].massacc);
    pv(cur[i]); pvt(old[i]);
    printf("   massacc=%e\n",atom[i].massacc);
  }
}

void checkatom(int i) {
  int j, b, ba;
  double v;

  if (i<0 || i>=Nexatom) printf("bad atom number %d\n",i);
  else if (atom[i].elt < 0 || atom[i].elt >= NUMELTS)
    printf("bad element in atom %d: %d\n", i, atom[i].elt);
  else if (atom[i].nbonds <0 || atom[i].nbonds >NBONDS)
    printf("bad nbonds in atom %d: %d\n", i, atom[i].nbonds);
  else if (atom[i].elt < 0 || atom[i].elt >= NUMELTS)
    printf("bad element in atom %d: %d\n", i, atom[i].elt);
  else for (j=0; j<atom[i].nbonds; j++) {
      b=atom[i].bonds[j];
      if (b < 0 || b >= Nexbon) 
	printf("bad bonds number in atom %d: %d\n", i, b);
      else if (i != bond[b].an1 && i != bond[b].an2) {
	printf("bond %d of atom %d [%d] doesn't point back\n", j, i, b);
	exit(0);
      }
  }
}

void pb(int i) {
  double len;
  struct bsdata *bt;
  int index;

  if (i<0 || i>=Nexbon) printf("bad bond number %d\n",i);
  else {
    bt = bond[i].type;
    len = vlen(vdif(cur[bond[i].an1],cur[bond[i].an2])); 
    printf("bond %d[%d] [%s%d(%d)-%s%d(%d)]: length %.1f\n", 
	   i, bond[i].order, 
	   elname[atom[bond[i].an1].elt], bond[i].an1, atom[bond[i].an1].elt,
	   elname[atom[bond[i].an1].elt], bond[i].an2, atom[bond[i].an2].elt,
	   len);
    index=(int)((len*len)-bt->start)/bt->scale;
    if (index<0 || index>=TABLEN) 
      printf("r0=%.1f, index=%d of %d, off table\n",  bt->r0, index, TABLEN);
    else printf("r0=%.1f, index=%d of %d, value %f\n", bt->r0, index, TABLEN,
		bt->table->t1[index] + len*len*bt->table->t2[index]);
  }
}

void pq(int i) {
  struct xyz r1, r2;
  if (i<0 || i>=Nextorq) printf("bad torq number %d\n",i);
  else {
      printf("torq %s%d-%s%d-%s%d, that's %d-%d=%d-%d\n",
	     elname[atom[torq[i].a1].elt], torq[i].a1,
	     elname[atom[torq[i].ac].elt], torq[i].ac,
	     elname[atom[torq[i].a2].elt], torq[i].a2,
	   (torq[i].dir1 ? torq[i].b1->an2 :  torq[i].b1->an1),
	   (torq[i].dir1 ? torq[i].b1->an1 :  torq[i].b1->an2),
	   (torq[i].dir2 ? torq[i].b2->an1 :  torq[i].b2->an2),
	   (torq[i].dir2 ? torq[i].b2->an2 :  torq[i].b2->an1));

      r1=vdif(cur[torq[i].a1],cur[torq[i].ac]);
      r2=vdif(cur[torq[i].a2],cur[torq[i].ac]);
      printf("r1= %.1f, r2= %.1f, theta=%.2f (%.0f)\n",
	     vlen(r1), vlen(r2), vang(r1, r2), 
	     (180.0/3.1415)*vang(r1, r2));      
  }
}

void pvdw(struct vdWbuf *buf, int n) {
  printf("vdW %s%d-%s%d: vanderTable[%d]\n",
	 elname[atom[buf->item[n].a1].elt], buf->item[n].a1,
	 elname[atom[buf->item[n].a2].elt], buf->item[n].a2,
	 buf->item[n].table - vanderTable);
  printf("start; %f, scale %d, b=%f, m=%f\n",
	 sqrt(buf->item[n].table->start), buf->item[n].table->scale,
	 buf->item[n].table->table.t1[0],
	 buf->item[n].table->table.t2[0]);

}

/* creating atoms, bonds, etc */

/* uses global Nexatom, atom, element, cur, old, Dt, Dx, Boltz, and 
    Temperature */
void makatom(int elem, struct xyz posn) {
  struct xyz foo, v, p;
  double mass, therm;

  /* create the data structures */
  atom[Nexatom].elt=elem;
  atom[Nexatom].nbonds=0;
  atom[Nexatom].part = PartNo;
  atom[Nexatom].disp = DisplayStyle;
  atom[Nexatom].next = NULL;
  atom[Nexatom].bucket = &Space[0][0][0];

  mass=element[elem].mass * 1e-27;
  atom[Nexatom].massacc= Dt*Dt / mass;

  /* set position and initialize thermal velocity */
  cur[Nexatom]=posn;
  old[Nexatom]=posn;
  avg[Nexatom]=posn;
  therm = sqrt((2.0*Boltz*Temperature)/mass)*Dt/Dx;
  v=gxyz(therm);
  vsub(old[Nexatom],v);

  /* thermostat trigger stays high, since slower motions shouldn't
     reach the unstable simulation regions of phase space
  */
  therm = sqrt((2.0*Boltz*300.0)/mass)*Dt/Dx;
  atom[Nexatom].vlim=(3*therm)*(3*therm);

  TotalKE += 2.0*Boltz*Temperature;
  atom[Nexatom].energ = (0.5*mass*Dx*Dx)/(Dt*Dt);

  /* add contribution to overall mass center, momentum */
  totMass += mass;

  vmul2c(foo,posn,mass);
  vadd(Cog,foo);

  vmul2c(p,v,mass);
  vadd(P,p);

  /* 
    v=vlen(vdif(cur[Nexatom],old[Nexatom]));
    printf("makatom(%d)  V=%.2f ", Nexatom, v);
    pv(cur[Nexatom]); pvt(old[Nexatom]);
  */          
  Nexatom++;

  }



/* an actual bond is ordered so it has a positive type,
    e.g. atom[a].elt <= atom[b].elt */
/* 2 phases -- in first, we don't know if both atoms are there yet */
void makbon0(int a, int b, int ord) {
  int t, typ, ta, tb;
  double bl, sbl;

  bond[Nexbon].an1=a;
  bond[Nexbon].an2=b;
  bond[Nexbon].order=ord;

  Nexbon++;
}

void makbon1(int n) {
  int a, b, t, typ, ta, tb;
  double bl, sbl;

  a=bond[n].an1;
  b=bond[n].an2;

  ta=atom[a].elt;
  tb=atom[b].elt;
  if (tb<ta) {t=a; a=b; b=t; t=ta; ta=tb; tb=t;}

  typ=bontyp(bond[n].order,ta,tb);
  bond[n].an1=a;
  bond[n].an2=b;

  bond[n].type=bstab+findbond(typ);

  bl = vlen(vdif(cur[a], cur[b]));
  sbl = bond[n].type->r0;
  if (bl> 1.11*sbl || bl<0.89*sbl)
    printf("Strained bond: %2f vs %2f  (%s%d-%s%d)\n",bl,sbl,
	   elname[atom[a].elt], a, elname[atom[b].elt], b);
}

/* torqs are ordered so the bonds match those in bendata */
void maktorq(int a, int b) {
  int t, tq;
  double theta, th0;

  tq = findtorq(bond[a].type->typ,bond[b].type->typ);
  if (bendata[tq].b2typ == bond[a].type->typ
      || bendata[tq].b2typ == -bond[a].type->typ) {t=a; a=b; b=t;}
  
  torq[Nextorq].b1=bond+a;
  torq[Nextorq].b2=bond+b;
  torq[Nextorq].type = bendata+tq;

  if (bond[a].an1==bond[b].an1) {
    torq[Nextorq].dir1=1;
    torq[Nextorq].dir2=1;
    torq[Nextorq].a1=bond[a].an2;
    torq[Nextorq].a2=bond[b].an2;
    torq[Nextorq].ac=bond[a].an1;
  }
  else if (bond[a].an2==bond[b].an1) {
    torq[Nextorq].dir1=0;
    torq[Nextorq].dir2=1;
    torq[Nextorq].a1=bond[a].an1;
    torq[Nextorq].a2=bond[b].an2;
    torq[Nextorq].ac=bond[a].an2;
  }
  else if (bond[a].an1==bond[b].an2) {
    torq[Nextorq].dir1=1;
    torq[Nextorq].dir2=0;
    torq[Nextorq].a1=bond[a].an2;
    torq[Nextorq].a2=bond[b].an1;
    torq[Nextorq].ac=bond[a].an1;
  }
  else {
    torq[Nextorq].dir1=0;
    torq[Nextorq].dir2=0;
    torq[Nextorq].a1=bond[a].an1;
    torq[Nextorq].a2=bond[b].an1;
    torq[Nextorq].ac=bond[a].an2;
  }
  
  theta = vang(vdif(cur[torq[Nextorq].a1],cur[torq[Nextorq].ac]),
	       vdif(cur[torq[Nextorq].a2],cur[torq[Nextorq].ac]));
  th0=torq[Nextorq].type->theta0;
  
  if (theta> 1.25*th0 || theta<0.75*th0)
    printf("Strained torq: %.0f vs %.0f  (%s%d-%s%d-%s%d)\n",
	   (180.0/3.1415)*theta, (180.0/3.1415)*th0,
	   elname[atom[torq[Nextorq].a1].elt], torq[Nextorq].a1,
	   elname[atom[torq[Nextorq].ac].elt], torq[Nextorq].ac,
	   elname[atom[torq[Nextorq].a2].elt], torq[Nextorq].a2);
    


  Nextorq++;
}

/* make a vdw in one go, in calc loop */
void makvdw(int a1, int a2) {
  struct vdWbuf *newbuf;
  int nx, i, j;

  if (Nexvanbuf->fill >= VANBUFSIZ) {
    if (Nexvanbuf->next) {
      Nexvanbuf = Nexvanbuf->next;
      Nexvanbuf->fill = 0;
    }
    else {
      newbuf=malloc(sizeof(struct vdWbuf));
      Nexvanbuf->next = newbuf;
      Nexvanbuf = newbuf;
      Nexvanbuf->fill = 0;
      Nexvanbuf->next = NULL;
    }
  }

  Nexvanbuf->item[Nexvanbuf->fill].a1 = a1;
  Nexvanbuf->item[Nexvanbuf->fill].a2 = a2;

  i = min(atom[a1].elt,atom[a2].elt);
  j = max(atom[a2].elt,atom[a2].elt);
  nx = i*(NUMELTS+1) - i*(i+1)/2 + j-i;
  Nexvanbuf->item[Nexvanbuf->fill].table = vanderTable+nx;
 
  Nexvanbuf->fill++;
}

int Count = 0;

void findnobo(int a1) {
  int a2, ix, iy, iz, i, j, k;
  struct A *p;
  double r;

  ix= (int)cur[a1].x / 250 + 4;
  iy= (int)cur[a1].y / 250 + 4;
  iz= (int)cur[a1].z / 250 + 4;

  for (i=ix-7; i<ix; i++)
    for (j=iy-7; j<iy; j++)
      for (k=iz-7; k<iz; k++)
	for (p=Space[i&SPMASK][j&SPMASK][k&SPMASK]; p; p=p->next) {
	  a2 = p-atom;
	  if (a2>a1 && atom[a1].part != atom[a2].part) {
	    r=vlen(vdif(cur[a1],cur[a2]));
	    if (r<800.0) {
	      makvdw(a1, a2);
	      Count++;
	    }
	  }
	}
}

/* same as stretch bonds, 2 phases */
void makvander0(int a1, int a2) {
  struct vdWbuf *newbuf;
  int nx, i, j;

  if (Nexvanbuf->fill >= VANBUFSIZ) {
    if (Nexvanbuf->next) {
      Nexvanbuf = Nexvanbuf->next;
      Nexvanbuf->fill = 0;
    }
    else {
      newbuf=malloc(sizeof(struct vdWbuf));
      Nexvanbuf->next = newbuf;
      Nexvanbuf = newbuf;
      Nexvanbuf->fill = 0;
      Nexvanbuf->next = NULL;
    }
  }

  Nexvanbuf->item[Nexvanbuf->fill].a1 = a1;
  Nexvanbuf->item[Nexvanbuf->fill].a2 = a2;

  /* 
	printf("making(0) vdW %d/%d: atoms %d-%d\n",
	       Nexvanbuf-&vanderRoot, Nexvanbuf->fill, a1, a2);
  */
 
  Nexvanbuf->fill++;
}

void makvander1(struct vdWbuf *buf, int n) {

  int nx, i, j, a1, a2;

  
  a1=buf->item[n].a1;
  a2=buf->item[n].a2;

  i = min(atom[a1].elt,atom[a2].elt);
  j = max(atom[a2].elt,atom[a2].elt);
  nx = i*(NUMELTS+1) - i*(i+1)/2 + j-i;
  buf->item[n].table = vanderTable+nx;

  /* 
	printf("making(1) vdW %d/%d: atoms %d-%d\n",
	       buf-&vanderRoot, n, buf->item[n].a1, buf->item[n].a2);
  */
}

int makcon(int typ, struct MOT *mot, int n, int *atnos) {
  int i;
  
  Constraint[Nexcon].type = typ;
  Constraint[Nexcon].natoms=n;
  Constraint[Nexcon].motor=mot;
  for (i=0; i<n; i++) Constraint[Nexcon].atoms[i]=atnos[i];
  return Nexcon++;
}

    /* input torque in nN*nm,  speed in gigahertz
       store in pN*pm, rad/Dt 
    */

struct MOT * makmot(double stall, double speed, 
		    struct xyz vec1,  struct xyz vec2) {
  int i;

  Motor[Nexmot].center=vec1;
  Motor[Nexmot].axis=uvec(vec2);
  Motor[Nexmot].stall=stall*(1e-9/Dx)*(1e-9/Dx);
  Motor[Nexmot].speed=speed*1e9*2.0*Pi* Dt;
  
  return Motor+Nexmot++;
}

void makmot2(int i) {
  struct MOT *mot;
  struct xyz r, q, vrmax;
  int j, *atlis;
  double x, mass, rmax=0.0, mominert=0.0;

  if (Constraint[i].type != 1) return;

  atlis = Constraint[i].atoms;
  mot = Constraint[i].motor;
  mot->axis = uvec(mot->axis);

  for (j=0;j<Constraint[i].natoms;j++) {
    /* for each atom connected to the "shaft" */
    mass = element[atom[atlis[j]].elt].mass * 1e-27;

    /* find its projection onto the rotation vector */
    r=vdif(cur[atlis[j]],mot->center);
    x=vdot(r,mot->axis);
    vmul2c(q,mot->axis,x);
    vadd2(mot->atocent[j],q,mot->center);

    /* and orthogonal distance */
    r=vdif(cur[atlis[j]],mot->atocent[j]);
    mot->ator[j] = r;
    mot->radius[j]=vlen(r);
    if (mot->radius[j] > rmax) vrmax=r;

    mominert += mot->radius[j]*mass;
  }
  mot->moment = (Dt*Dt)/mominert;
  mot->theta = 0.0;
  mot->theta0 = 0.0;

  /* set up coordinate system for rotations */
  mot->roty = uvec(vrmax);
  mot->rotz = vx(mot->axis, mot->roty);
  /* the idea is that an atom at (radius, atang) can be rotated theta
     by putting it at radius*(roty*cos(nt)+rotz*sin(nt))
     where nt is theta + atang
  */
  for (j=0;j<Constraint[i].natoms;j++) { /* now find the angles */
    r=uvec(mot->ator[j]);
    mot->atang[j] = atan2(vdot(r,mot->rotz),vdot(r,mot->roty));
  }
}

void pcon(int i) {
  struct MOT *mot;
  int j;

  if (i<0 || i>=Nexcon) {
    printf("Bad constraint number %d\n",i);
    return;
  }
  printf("Constraint %d: ",i);
  if (Constraint[i].type == 0) {
    printf("Space weld\n atoms ");
    for (j=0;j<Constraint[i].natoms;j++) 
      printf("%d ",Constraint[i].atoms[j]);
    printf("\n");
  }
  else if (Constraint[i].type == 1) {
    mot = Constraint[i].motor;
    printf("motor; stall torque %.2e, unloaded speed %.2e\n center ",
	   mot->stall, mot->speed);
    pv(mot->center);
    printf(" axis ");
    pvt(mot->axis);

    printf(" rot basis ");
    pv(mot->roty); pv(mot->rotz);
    printf(" angles %.0f, %.0f, %.0f\n",
	   180.0*vang(mot->axis,mot->roty)/Pi,
	   180.0*vang(mot->rotz,mot->roty)/Pi,
	   180.0*vang(mot->axis,mot->rotz)/Pi);

    for (j=0;j<Constraint[i].natoms;j++) {
      printf(" atom %d radius %.1f angle %.2f\n   center ",
	     Constraint[i].atoms[j], mot->radius[j], mot->atang[j]);
      pv(mot->atocent[j]);
      printf(" posn "); pvt(mot->ator[j]);
    }
    printf(" Theta=%.2f, theta0=%.2f, moment factor =%e\n",
	   mot->theta, mot->theta0, mot->moment);
  }
}
    
/* file reading */

void filred(char *filnam) {
  
  FILE *file;
  char buf[128];
  int i, j, n, m, b, c, ord, lastatom;
  double stall, speed;
  struct xyz vec1,vec2;
  int a1, a2, ie, ix, iy, iz, ix1, iy1, iz1, iv[25];
  int firstatom=1, offset;
  int atnum, atnotab[2*NATOMS];
  struct vdWbuf *nvb;

  file=fopen(filnam,"r");
  
  
  while (fgets(buf,127,file)) {
    /* atom number (element) (posx, posy, posz) */
    /* position vectors are integral 0.1pm */
    if (0==strncasecmp("atom",buf,4)) {
      sscanf(buf+4, "%d (%d) (%d,%d,%d", &atnum, &ie, &ix, &iy, &iz);
      /*
      printf("in filred: %s %d (%d) (%d,%d,%d) \n","atom", 
	     lastatom,ie, ix, iy, iz );
      */

      atnotab[atnum]=Nexatom;
      lastatom = Nexatom;

      vec1.x=(double)ix *0.1;
      vec1.y=(double)iy *0.1;
      vec1.z=(double)iz *0.1;
      makatom(ie,vec1);

      
    }
    /* bondO atno atno atno ... (where O is order) */
    else if (0==strncasecmp("bond",buf,4)) {

      j=sscanf(buf+4, "%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d",
	       &ord, iv, iv+1, iv+2, iv+3, iv+4, iv+5, iv+6, iv+7, iv+8, iv+9,
	       iv+10, iv+11, iv+12, iv+13, iv+14, iv+15, iv+16, iv+17, 
	       iv+18, iv+19, iv+20, iv+21, iv+22, iv+23, iv+24);

      for (i=0; i<j-1; i++) makbon0(lastatom, atnotab[iv[i]], ord);
    }

    /* [vander]Waals atno atno atno ... (for atoms on same part) */
    else if (0==strncasecmp("waals",buf,5)) {

      j=sscanf(buf+5, "%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d",
	       iv, iv+1, iv+2, iv+3, iv+4, iv+5, iv+6, iv+7, iv+8, iv+9,
	       iv+10, iv+11, iv+12, iv+13, iv+14, iv+15, iv+16, iv+17, 
	       iv+18, iv+19, iv+20, iv+21, iv+22, iv+23, iv+24);

      for (i=0; i<j; i++) makvander0(lastatom,atnotab[iv[i]]);
    }

    /* constraints */
    /* welded to space: */
    else if (0==strncasecmp("ground",buf,6)) {
      j=sscanf(buf+6, "%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d",
	       iv, iv+1, iv+2, iv+3, iv+4, iv+5, iv+6, iv+7, iv+8, iv+9,
		 iv+10, iv+11, iv+12, iv+13, iv+14, iv+15, iv+16, iv+17, 
		 iv+18, iv+19, iv+20, iv+21, iv+22, iv+23, iv+24);
      for (i=0; i<j; i++) atnotab[iv[i]];
      makcon(0, NULL, j, iv);
    }

    /* motor <torque>, <speed>, (<center>) (<axis>) */
    /* torque in nN*nm  speed in gigahertz */
    else if (0==strncasecmp("motor",buf,5)) {
      sscanf(buf+5, "%lf, %lf, (%d, %d, %d) (%d, %d, %d",
	     &stall, &speed, &ix, &iy, &iz, &ix1, &iy1, &iz1);

      vec1.x=(double)ix *0.1;
      vec1.y=(double)iy *0.1;
      vec1.z=(double)iz *0.1;
      vec2.x=(double)ix1 *0.1;
      vec2.y=(double)iy1 *0.1;
      vec2.z=(double)iz1 *0.1;
      fgets(buf,127,file);
      if (strncasecmp("shaft",buf,5)) printf("motor needs a shaft\n");
      else {
	j=sscanf(buf+5, "%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d",
		 iv, iv+1, iv+2, iv+3, iv+4, iv+5, iv+6, iv+7, iv+8, iv+9,
		 iv+10, iv+11, iv+12, iv+13, iv+14, iv+15, iv+16, iv+17, 
		 iv+18, iv+19, iv+20, iv+21, iv+22, iv+23, iv+24);
	for (i=0; i<j; i++) atnotab[iv[i]];
	i=makcon(1, makmot(stall, speed, vec1, vec2), j, iv);
      }
    }

    /* part [nil|bns|vdw] */
    else if (0==strncasecmp("part",buf,4)) {
      PartNo++;
      if (0==strncasecmp("nil",buf+5,3)) DisplayStyle=0;
      else if (0==strncasecmp("bns",buf+5,3)) DisplayStyle=1;
      else if (0==strncasecmp("vdw",buf+5,3)) DisplayStyle=2;
      else DisplayStyle=1;
    }

    /* show [nil|bns|vdw] */
    else if (0==strncasecmp("show",buf,4)) {
      if (0==strncasecmp("nil",buf+5,3)) DisplayStyle=0;
      else if (0==strncasecmp("bns",buf+5,3)) DisplayStyle=1;
      else if (0==strncasecmp("vdw",buf+5,3)) DisplayStyle=2;
      else DisplayStyle=1;
    }

    else if (0==strncasecmp("kelvin",buf,6)) {
      sscanf(buf+6, "%d", &ix);
      Temperature = (double)ix;
      printf("Temperature set to %f\n",Temperature);
    }

    else if (0==strncasecmp("end",buf,3)) break;
    
    else printf("??? %s\n", buf);

  }
  fclose(file);


  /* fill in new atoms, fixup backward bonds */

  for (i=0; i<Nexbon; i++) {
    makbon1(i);
    a1=bond[i].an1;
    atom[a1].bonds[atom[a1].nbonds++]=i;
    a2=bond[i].an2;
    atom[a2].bonds[atom[a2].nbonds++]=i;
  }

  /* got all the static vdW bonds we'll see */
  Dynobuf = Nexvanbuf;
  Dynoix = Nexvanbuf->fill;

  /* fill in new atoms for vanderwaals pointers */
  for (nvb=&vanderRoot; nvb; nvb=nvb->next) 
    for (j=0; j<nvb->fill; j++) makvander1(nvb, j);

  /* 
  for (i=0; i<Nexatom; i++) pa(i);
  for (i=0; i<Nexbon; i++) pb(i);
  */

  /* create bending bonds */
  for (i=0; i<Nexatom; i++) {
    for (m=0; m<atom[i].nbonds-1; m++) {
      for (n=m+1; n<atom[i].nbonds; n++) {
	checkatom(i);
	maktorq(atom[i].bonds[m], atom[i].bonds[n]);
      }
    }
  }

  for (i=0; i<Nexcon; i++) makmot2(i); /* fixup motors */
  
  /* find bounding box */

  vset(vec1, cur[0]);
  vset(vec2, cur[0]);
  
  for (i=1; i<Nexatom; i++) {
    vmin(vec1,cur[i]);
    vmax(vec2,cur[i]);
  }
  vadd2(Center, vec1, vec2);
  vmulc(Center, 0.5);

  vset(Bbox[0], vsum(vec1, vcon(-100.0)));
  vset(Bbox[1], vsum(vec2, vcon(100.0)));

}

/* display stuff */


GLfloat light_diffuse[] = {1.0, 1.0, 1.0, 1.0};  /* White diffuse light. */
GLfloat color_black[] = {0.0, 0.0, 0.0, 1.0};  /* Black. */
GLfloat color_red[] = {1.0, 0.0, 0.0, 1.0};  /* Red. */
GLfloat light_position[] = {1.0, 1.0, 1.0, 0.0};  /* Infinite light location. */
void display(void) {
  int i,j;
  struct vdWbuf *nvb;
  GLfloat r;

  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  for (i=0; i<Nexatom; i++) {
    if (atom[i].disp==0) continue;
    glPushMatrix();
    glColor3fv(element[atom[i].elt].color);
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, element[atom[i].elt].color);
    glMaterialfv(GL_FRONT, GL_SPECULAR, light_diffuse);
    glMaterialf(GL_FRONT, GL_SHININESS, 25.0);

    glTranslatef(avg[i].x, avg[i].y, avg[i].z);
    r=(atom[i].disp==2 ? 100.0 : 10.0) * element[atom[i].elt].rvdw;
    glutSolidSphere(r, 40,20);
    glPopMatrix();
   }

  glDisable(GL_LIGHTING);
  glColor3fv(color_black);
  
  glBegin(GL_LINES);
  for (j=0; j<Nexbon; j++) {
    if (atom[bond[j].an1].disp==1 || atom[bond[j].an2].disp==1) {
      glVertex3d(avg[bond[j].an1].x,
		 avg[bond[j].an1].y,avg[bond[j].an1].z);
      glVertex3d(avg[bond[j].an2].x,
		 avg[bond[j].an2].y,avg[bond[j].an2].z);
    }
  }

  /* show vander waals interactions */
  /* 
  glColor3fv(color_red);
  for (nvb=&vanderRoot; nvb; nvb=nvb->next) 
    for (j=0; j<nvb->fill; j++) {
      if (atom[nvb->item[j].a1].disp==1 || atom[nvb->item[j].a2].disp==1) {
	if (vlen(vdif(avg[nvb->item[j].a1],avg[nvb->item[j].a2])) < 400.0){
       glVertex3d(avg[nvb->item[j].a1].x,
		  avg[nvb->item[j].a1].y,
		  avg[nvb->item[j].a1].z);
       glVertex3d(avg[nvb->item[j].a2].x,
		  avg[nvb->item[j].a2].y,
		  avg[nvb->item[j].a2].z);
	}}
    }	
   */
  glEnd();
  glEnable(GL_LIGHTING);
  
  glutSwapBuffers();
}

void init(void) {
  double dist;

  glClearColor(0.4, 0.9, 0.2, 1.0);

  /* Enable a single OpenGL light. */
  glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse);
  glLightfv(GL_LIGHT0, GL_POSITION, light_position);
  glEnable(GL_LIGHT0);
  glEnable(GL_LIGHTING);

  /* Use depth buffering for hidden surface elimination. */
  glEnable(GL_DEPTH_TEST);

  /* Setup the view of the molecule. */
  dist = 1.5 * vlen(vdif(Bbox[1],Bbox[0]));
  
  glMatrixMode(GL_PROJECTION);
  gluPerspective( /* field of view in degree */ 30.0,
    /* aspect ratio */ 1.33333,
    /* Z near */ dist*0.6, /* Z far */ dist*1.5);
  glMatrixMode(GL_MODELVIEW);
  gluLookAt(Center.x, Center.y-dist, Center.z-dist/3.0,  /* eye is at  */
    Center.x, Center.y, Center.z,      /* center is at  */
    1.0, 0.0, 0.);      /* up is in positive Y direction */

}

int ShotNo=0;

void snapshot() {
  char fnam[25];
  FILE *file;
  unsigned char buf[3*SCRWID*SCRHIT], buf2[3*SCRWID*SCRHIT];
  int i, j, w=SCRWID, h=SCRHIT;

  
  glFlush();
  glReadPixels(0,0, w,h, GL_RGB, GL_UNSIGNED_BYTE, buf);
  /* OpenGL returns the image upside down... */
  for (i=0; i<h; i++)
    for (j=0;j<3*w; j++) 
      buf2[i*3*w + j]=buf[(h-i-1)*3*w + j];

  sprintf(fnam,"mol%04d.ppm",ShotNo++);

  file = fopen(fnam,"w"); 
  fprintf(file, "P6\n%d %d\n%d\n", w, h, 255);
  fwrite(buf2, 1, 3*w*h, file);
  fclose(file);
}


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
	
	printf("stretch: low --");
	pb(j);
	fac=t1[0]+rsq*t2[0]; 
      }
      else if (k>=TABLEN) {
	
	printf("stretch: high --");
	pb(j);
	fac=0.0;
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
      printf("bond %d: stretch force: %f, ",j,br);
       */
      vmul2c(f,bond[j].ru,vdot(bond[j].ru,bond[j].bff));
      vsub2(f,bond[j].bff,f);
      vadd(force[bond[j].an1],f);
      vsub(force[bond[j].an2],f);
      /* 
      printf("bending %f\n", sqrt(vdot(f,f)));
       */
    }

    /* do the van der Waals/London forces */
    for (nvb=&vanderRoot; nvb; nvb=nvb->next) 
      for (j=0; j<nvb->fill; j++) {
	vsub2(f, cur[nvb->item[j].a1], cur[nvb->item[j].a2]);
	rsq = vdot(f,f);

	if (rsq>50.0*700.0*700.0) {
	  printf("hi vdw: %f\n", sqrt(rsq));
	  pvdw(nvb,j);
	  pa(nvb->item[j].a1);
	  pa(nvb->item[j].a2);
	}

	/* 
	printf("Processing vdW %d/%d: atoms %d-%d, r=%f\n",
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
	  printf("vdW: off table low -- r=%.2f \n",  sqrt(rsq));
	  pvdw(nvb,j);
	  k=0;
	  fac=t1[k]+rsq*t2[k]; 
	}
	else if (k>=TABLEN) {
	  /* 
	  printf("vdW: off table high -- %d/%d: start=%.2f, scale=%d\n",
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
      printf("--> Total force on atom %d is %.2f, displacement %f\n", j,
	     ff, ff*atom[j].massacc);
	      */
      vmul2c(f,force[j],atom[j].massacc);

      if (vlen(f)>15.0) {
	printf("High force %.2f in iteration %d\n",vlen(f), Iteration);
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
    printf("\njust before, cur=\n");
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
	printf("*** input torque %f\n", totorq);
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
	printf("***  Theta = %f, %f, %f\n",theta, mot->theta, mot->theta0);
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
    printf("just after, new=\n");
    for (j=0;j<Nexatom;j++) pvt(new[j]);
    */

    tmp=old; old=cur; cur=new; new=tmp;

  }} /* end of main loop */
  
  ff = 1.0/((double)inner * (double)iters);
  for (j=0; j<Nexatom; j++) {
    vmulc(avg[j],ff);
  }
  
}

void minimize() {
  int i, j, saveNexcon;
  double tke, therm, mass;
  struct xyz v;

  /* turn off constraints while minimizing */
  saveNexcon=Nexcon;
  Nexcon=0;

  for (i=0; i<10; i++) {
    for (j=0; j<Nexatom; j++) old[j] = cur[j];
    calcloop(10);
    tke=0.0;
    for (j=0; j<Nexatom; j++) {
      v= vdif(cur[j], old[j]);
      tke += vdot(v,v);
    }
    printf("total Ke = %.2f\n",tke);
    display();
  }

  Nexcon=saveNexcon;

  printf("reinitializing constraints\n");
  for (i=0; i<Nexcon; i++) makmot2(i); /* regen constraints */
  for (i=0; i<Nexcon; i++) pcon(i);

  for (j=0; j<Nexatom; j++) {
    mass = element[atom[j].elt].mass * 1e-27;
    therm = sqrt((2.0*Boltz*Temperature)/mass)*Dt/Dx;
    v=gxyz(therm);
    vsub2(old[j],cur[j],v);
  }
  printf("reinitializing Temperature to %.0fK\n",Temperature);
}
  


void keyboard(unsigned char key, int x, int y) {

  if (key == '?') printf("\n\
q -- quit\n\
s -- snapshot\n\
b -- bond info\n\
p -- produce a movie\n\
m -- minimize energy of molecule\n\
v -- velocity info\n\
r -- reverse atoms in their tracks\n\
f -- iterate forever\n");

  if (key == 'q') exit(0);
  if (key == 's') snapshot();
  if (key == 'b') bondump();
  if (key == 'm') minimize();
  if (key == 'v') speedump();
  if (key == 'r') {tmp=old; old=cur; cur=tmp;}
  if (key == 'f') while (1) {calcloop(1); display();speedump();}
  if (key == 'p') {
    printf("making movie\n");
    for (x=0; x<1000; x++) {
      calcloop(15);
      display();
      snapshot();
    }
    exit(0);
  }


  calcloop(((key == 'z') ? 1 : 5));

  display();
  /* 
  snapshot();
 */
}

/* MMMM   MMMM      AAAAA     IIIIIIIIIII   NNNNN   NNN */
/* MMMM   MMMM     AAAAAAA    IIIIIIIIIII   NNNNNN  NNN */
/* MMMMM MMMMM    AAAA AAAA       IIII      NNNNNNN NNN */
/* MMMMMMMMMMM   AAAA   AAAA      IIII      NNNNNNNNNNN */
/* MMMMMMMMMMM   AAAAAAAAAAA      IIII      NNN NNNNNNN */
/* MMMMMMMMMMM   AAAAAAAAAAA      IIII      NNN  NNNNNN */
/* MMM MMM MMM   AAA     AAA  IIIIIIIIIII   NNN   NNNNN */
/* MMM     MMM   AAA     AAA  IIIIIIIIIII   NNN    NNNN */

main(int argc,char **argv)
{ 
  int i,j;
  struct xyz p, foo;
  double therm = 0.645;

  char buf[80];

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


  if (argc<2) exit(0);

  if (strchr(argv[1], '.')) sprintf(buf, "%s", argv[1]);
  else sprintf(buf, "%s.amsf", argv[1]);

  filred(buf);

  for (i=0; i<Nexcon; i++) pcon(i);
  /* 
  for (i=0; i<Nexatom; i++) pa(i);
  for (i=0; i<Nexbon; i++) pb(i);
  for (i=0; i<Nextorq; i++) pq(i);
  for (i=0; i<vanderRoot.fill; i++) pvdw(&vanderRoot,i);
   */
    
  orion();

  glutInit(&argc, argv);
  glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
  glutCreateWindow("Molecule!");
  glutReshapeWindow(SCRWID,SCRHIT);  
  glutDisplayFunc(display);
  glutKeyboardFunc(keyboard);
  init();

  

  glutMainLoop();
  return 0;  

}

/* 

  for (i=0; i<5; i++)  {
    makatom(6,diam[i]);
  }

  vadd2(old[Nexatom-1],cur[Nexatom-1],P);

  for (i=0; i<4; i++) makbon(i,4,1);

  for (i=0; i<3; i++) for (j=i+1; j<4; j++) maktorq(i,j);
 */
  /*  for testing the table

  start = 20586.734698;
  end = 0;
  scale = 206;
  printf("%f by %d steps %d to %f\n", start,scale,TABLEN,end);
  maktab(t1,t2,bender,start,TABLEN,scale);
  
  for (i=0; i<10; i++) {
    x=150.534+10.845*(double)i;
    x=x*x;
    y=bender(x);
    
    j=(int)(x-start)/scale;
    printf("%d\n",j);
    z=t1[j]+x*t2[j]; 
    printf("direct %f, table %f, ratio %f\n",y,z,y/z);
  }
  exit(0);

  start = square(R0*0.666);
  end = square(R0*1.333);
  scale = (end - start) / TABLEN;
  printf("%f by %d steps %d to %f\n", start,scale,TABLEN,end);
  maktab(t1,t2,hooke,start,TABLEN,scale);
  for (i=0; i<100; i++) {
    x=110.534+0.845*(double)i;
    x=x*x;
    y=hooke(x);

    j=(int)(x-start)/scale;
    z=t1[j]+x*t2[j]; 
    printf("direct %f, table %f, ratio %f\n",y,z,y/z);
  }
  exit(0);

  maktab(t1,t2,hooke,start,TABLEN,30);
  for (i=0; i<100; i++) {
    x=110.534+0.845*(double)i;
    x=x*x;
    y=hooke(x);

    j=(int)(x-start)/scale;
    z=t1[j]+x*t2[j]; 
    printf("direct %f, table %f, ratio %f\n",y,z,y/z);
  }
  */
  /*
    start =  R0*R0 + R1*R1 + 2.0*R0*R1*cos(Theta0-Pi/6.0);
    end =  R0*R0 + R1*R1 + 2.0*R0*R1*cos(Theta0+Pi/6.0);
    scale = (end - start) / TABLEN;
    printf("start=%f, scale=%d\n",start, scale);

  maktab(t1,t2,bender,start,TABLEN,scale);
  theta=Pi/2.0;

  for (i=0; i<50; i++) {
    theta=theta+(Pi/200.0);
    x=square(152.3)*(square(1.0+cos(theta))+square(sin(theta)));
    y=bender(x);


    
    j=(int)(x-start)/scale;
    z=t1[j]+x*t2[j]; 
    printf("theta %.3f, x %.1f, direct %.2f, table[%d] %.2f\n",theta,x,y,j,z);
    
  }
  exit(0);
  */
