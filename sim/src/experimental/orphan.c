
// Copyright 2005 Nanorex, Inc.  See LICENSE file for details. 
/* factor for a unit vector given length squared -- rtned in uf, i is temp */
/** tables and setup function for same */
double uft1[UFTLEN], uft2[UFTLEN];

double uffunc(double uf) {
    return 1.0/sqrt(uf);
}

from main() before setupPositionsArrays:
    maktab(uft1, uft2, uffunc, UFSTART, UFTLEN, UFSCALE);

/** data for the 5-carbon test molecule */
struct xyz diam[5]=
    {{0.0, 0.0, 0.0},
     {176.7, 176.7, 0.0},
     {176.7, 0.0, 176.7},
     {0.0, 176.7, 176.7},
     {88.33, 88.33, 88.33}};

int PartNo=0, DisplayStyle=1;	/* 0 nothing, 1 ball/stick, 2 vdW surface */

int findbond(int btyp) {
    int i;
    if (btyp < 0)
	btyp = -btyp;
    for (i=0; i < BSTABSIZE; i++)
	if (bstab[i].typ == btyp)
	    return i;
    // fprintf(stderr, "Bond type %d not found\n",btyp);
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
    // fprintf(stderr, "Bend type %d-%d not found\n",btyp1,btyp2);
    return 0; // the default bend type
}

// printers.c

// unused
static void pbontyp(FILE *f, struct bsdata *ab) {
    fprintf(f, "Bond between %d / %d of order %d: type %d, length %f, stiffness %f\n table %d, start %f, scale %d\n",
	      ab->a1,ab->a2,ab->ord,ab->typ,ab->r0,ab->ks,
	      ab->table,ab->start,ab->scale);
	
}

//unused
static void bondump(FILE *f) {		/* gather bond statistics */
    int histo[50][23], totno[50], btyp, i, j, k, n;
    double r, perc, means[50];
    struct bondStretch *bt;
	
    for (i=0; i<50; i++) {
	totno[i] = 0;
	means[i] = 0.0;
	for (j=0; j<23; j++)
	    histo[i][j]=0;
    }
	
    for (i=0; i<Nexbon; i++) {
	bt=bond[i].type;
	// XXX btyp = bt-bstab;
	totno[btyp]++;
	r=vlen(vdif(Positions[bond[i].an1], Positions[bond[i].an2]));
	means[btyp] += r;
	perc = (r/bt->r0)*20.0 - 8.5;
	k=(int)perc;
	if (k<0) k=0;
	if (k>22) k=22;
	histo[btyp][k]++;
    }
	
    for (i=0; i<BSTABSIZE; i++) if (totno[i]) {
	fprintf(f, "Bond type %s-%s, %d occurences, mean %.2f pm:\n",
		  periodicTable[bstab[i].a1].symbol, periodicTable[bstab[i].a2].symbol, totno[i],
		  means[i]/(double)totno[i]);
	for (j=0; j<23; j++) {
	    if ((j-1)%10) fprintf(f, " |");
	    else fprintf(f, "-+");
	    n=(80*histo[i][j])/totno[i];
	    if (histo[i][j] && n==0) fprintf(f, ".");
	    for (k=0; k<n; k++) fprintf(f, "M");
	    fprintf(f, "\n");
	}}
    fprintf(f, "Iteration %d\n",Iteration);
}

// unused
static void pangben(FILE *f, struct angben *ab) {
    fprintf(f, "Bend between %d / %d: kb=%.2f, th0=%.2f\n",
	   ab->b1typ,ab->b2typ,ab->kb,ab->theta0);

}

// unused
static void speedump(FILE *f) {		/* gather bond statistics */
    int histo[20], iv, i, j, k, n;
    double v, eng, toteng=0.0;
	
    for (i=0; i<21; i++) {
	histo[i]=0;
    }
	
    for (i=0; i<Nexatom; i++) {
	v=vlen(vdif(OldPositions[i],Positions[i]));
	eng= atom[i].energ*v*v;
	toteng += eng;
	iv=(int)(eng*1e21);
	if (iv>20) iv=20;
	histo[iv]++;
    }
	
    fprintf(f, "Kinetic energies:\n");
    for (j=0; j<21; j++) {
	if (j%5) fprintf(f, " |");
	else fprintf(f, "-+");
	n=(70*histo[j])/Nexatom;
	if (histo[j] && n==0) fprintf(f, ".");
	for (k=0; k<n; k++) fprintf(f, "M");
	fprintf(f, "\n");
    }
    fprintf(f, "Iteration %d, KE %e --> %e\n",Iteration,TotalKE,FoundKE);
}

// simulator.h

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
        /** covalent radius */
        double rcovalent;
        /** element's symbol on periodic table */
        char *symbol;
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

struct dtab {                   /* two interpolation tables */
        double  t1[TABLEN], t2[TABLEN];
};


/* mol.c */
extern struct vdWbuf vanderRoot;
extern double uft1[200];
extern double uft2[200];
extern double uffunc(double uf);
//extern struct xyz f;
extern struct xyz diam[5];
// extern char *elname[37];
#if 0
extern int findbond(int btyp);
extern int findtorq(int btyp1, int btyp2);
#endif
extern void makbon0(int a, int b, int ord);
extern void makbon1(int n);
extern void makvander0(int a1, int a2);
extern void makvander1(struct vdWbuf *buf, int n);
extern void calcloop(int iters);
extern void minimize(int NumFrames);
extern void keyboard(unsigned char key, int x, int y);
extern int main(int argc, char **argv);

/* display.c */
extern void display(void);
extern void init(void);
extern void display_init(int *argc, char *argv[]);
extern void display_mainloop(void);

// interpolate.c

void testInterpolateBondStretch(int ord, int a1, int a2)
{
    int i;
    double start;
    double scale;
    double *t1, *t2;
    double rSquared;
    double lowR, highR;
    double lowRSquare;
    double highRSquare;
    double epsilon;
    int steps;
    int k;
    double fac;
    double func;
    
    i = findbond(bontyp(ord, a1, a2));

    R0 = bstab[i].r0;
    Ks = bstab[i].ks;
    De = bstab[i].de;
    Beta = bstab[i].beta;
    printf("# R0: %e Ks: %e De: %e Beta: %e\n", R0, Ks, De, Beta);
    
    /* table setup for stretch, to be moved out of loop */
    start=bstab[i].start;
    scale=bstab[i].scale;
    t1=bstab[i].table->t1;
    t2=bstab[i].table->t2;

    printf("# start: %e scale: %e\n", start, scale);

    lowR = R0 * 0.496;
    highR = R0 * 1.5;
    steps = 10000;
    lowRSquare = lowR * lowR;
    highRSquare = highR * highR;
    //highRSquare = TABLEN * scale * 1.5 + start;
    epsilon = (highRSquare - lowRSquare) / steps ;

    for (rSquared=lowRSquare; rSquared<highRSquare; rSquared += epsilon) {
        k=(int)(rSquared-start)/scale;
        if (k<0) {
            fac=t1[0]+rSquared*t2[0];
        } else if (k>=TABLEN) {
            fac = t1[TABLEN-1]+((TABLEN-1)*scale+start)*t2[TABLEN-1];
        } else {
            fac=t1[k]+rSquared*t2[k];
        }
        // table lookup equivalent to: fac=lippmor(rSquared)
        func = lippmor(rSquared);
        printf("%e %e %e\n", sqrt(rSquared), fac, func);
    }
    exit(0);
}
