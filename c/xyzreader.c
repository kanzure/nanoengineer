#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "mol.h"


/** indicate next avail/total number of stretch bonds, bend bonds, and atoms */
int Nexbon=0, Nextorq=0, Nexatom=0;

/** Input xyz file */
FILE *inf;

/** positions and forces on the atoms w/pointers into pos */
struct xyz avg[NATOMS];

struct xyz Center, Bbox[2];

/** data for the 5-carbon test molecule */
struct xyz diam[5]=
	{{0.0, 0.0, 0.0},
	 {176.7, 176.7, 0.0},
	 {176.7, 0.0, 176.7},
	 {0.0, 176.7, 176.7},
	 {88.33, 88.33, 88.33}};

int PartNo=0;

/** 0 nothing, 1 ball/stick, 2 vdW surface */
int DisplayStyle=2;

struct A atom[NATOMS];


struct B bond[4*NATOMS];


struct atomtype element[NUMELTS]={
	{0.001,  1.0,  0.130, 1, {0.0, 0.0, 0.0, 1.0}, "LP"},     /*  0 Lone Pair */
	{1.674, 0.79,  0.382, 1, {0.0, 0.6, 0.6, 1.0}, "H"},      /*  1 Hydrogen */
	{6.646,  1.4,  0.666, 0, {1.0, 0.27, 0.67, 1.0}, "He"},   /*  2 Helium */
	{11.525, 4.0,  0.666, 1, {0.0, 0.5, 0.5, 1.0}, "Li"},     /*  3 Lithium */
	{14.964, 3.0,  0.666, 2, {0.98, 0.67, 1.0, 1.0}, "Be"},   /*  4 Beryllium */
	{17.949, 2.0,  0.666, 3, {0.3, 0.3, 1.0, 1.0}, "B"},      /*  5 Boron */
	{19.925, 1.84, 0.357, 4, {0.22, 0.35, 0.18, 1.0}, "C"},   /*  6 Carbon */
	{23.257, 1.55, 0.447, 5, {0.84, 0.37, 1.0, 1.0}, "N"},    /*  7 Nitrogen */
	{26.565, 1.74, 0.406, 2, {0.6, 0.2, 0.2, 1.0}, "O"},      /*  8 Oxygen */
	{31.545, 1.65, 0.634, 1, {0.0, 0.8, 0.34, 1.0}, "F"},     /*  9 Fluorine */
	{33.49,  1.82, 0.666, 0, {0.92, 0.25, 0.62, 1.0}, "Ne"},  /* 10 Neon */
	{38.173, 4.0,  1.666, 1, {0.0, 0.4, 0.4, 1.0}, "Na"},     /* 11 Sodium */
	{40.356, 3.0,  1.666, 2, {0.88, 0.6, 0.9, 1.0}, "Mg"},    /* 12 Magnesium */
	{44.800, 2.5,  1.666, 3, {0.5, 0.5, 0.9, 1.0}, "Al"},     /* 13 Aluminum */
	{46.624, 2.25, 1.137, 4, {0.37, 0.45, 0.33, 1.0}, "Si"},  /* 14 Silicon */
	{51.429, 2.11, 1.365, 5, {0.73, 0.32, 0.87, 1.0}, "P"},   /* 15 Phosphorus */
	{53.233, 2.11, 1.641, 6, {1.0, 0.65, 0.0, 1.0}, "S"},     /* 16 Sulfur */
	{58.867, 2.03, 1.950, 1, {0.34, 0.68, 0.0, 1.0}, "Cl"},   /* 17 Chlorine */
	{66.33,  1.88, 1.666, 0, {0.85, 0.24, 0.57, 1.0}, "Ar"},  /* 18 Argon */
	{64.926, 5.0,  2.666, 1, {0.0, 0.3, 0.3, 1.0}, "K"},      /* 19 Potassium */
	{66.549, 4.0,  2.666, 2, {0.79, 0.55, 0.8, 1.0}, "Ca"},   /* 20 Calcium */
	{74.646, 3.7,  2.666, 3, {0.42, 0.42, 0.51, 1.0}, "Sc"},  /* 21 Scandium */
	{79.534, 3.5,  2.666, 4, {0.42, 0.42, 0.51, 1.0}, "Ti"},  /* 22 Titanium */
	{84.584, 3.3,  2.666, 5, {0.42, 0.42, 0.51, 1.0}, "V"},   /* 23 Vanadium */
	{86.335, 3.1,  2.666, 6, {0.42, 0.42, 0.51, 1.0}, "Cr"},  /* 24 Chromium */
	{91.22,  3.0,  2.666, 7, {0.42, 0.42, 0.51, 1.0}, "Mn"},  /* 25 Manganese */
	{92.729, 3.0,  2.666, 3, {0.42, 0.42, 0.51, 1.0}, "Fe"},  /* 26 Iron */
	{97.854, 3.0,  2.666, 3, {0.42, 0.42, 0.51, 1.0}, "Co"},  /* 27 Cobalt */
	{97.483, 3.0,  2.666, 3, {0.42, 0.42, 0.51, 1.0}, "Ni"},  /* 28 Nickel */
	{105.513, 3.0, 2.666, 2, {0.42, 0.42, 0.51, 1.0}, "Cu"},  /* 29 Copper */
	{108.541, 2.9, 2.666, 2, {0.42, 0.42, 0.51, 1.0}, "Zn"},  /* 30 Zinc */
	{115.764, 2.7, 2.666, 3, {0.6, 0.6, 0.8, 1.0}, "Ga"},     /* 31 Gallium */
	{120.53,  2.5, 2.666, 4, {0.45, 0.49, 0.42, 1.0}, "Ge"},  /* 32 Germanium */
	{124.401, 2.2, 2.666, 5, {0.6, 0.26, 0.7, 1.0}, "As"},    /* 33 Arsenic */
	{131.106, 2.1, 2.666, 6, {0.9, 0.35, 0.0, 1.0}, "Se"},    /* 34 Selenium */
	{132.674, 2.0, 2.599, 1, {0.0, 0.5, 0.0, 1.0}, "Br"},     /* 35 Bromine */
	{134.429, 1.9, 2.666, 0, {0.78, 0.21, 0.53, 1.0}, "Kr"}   /* 36 Krypton */
};

#define NUM_ELEMENTS_KNOWN  (sizeof(element) / sizeof(struct atomtype))

/* NB! all the Evdw that end in .666 are unknown */

char *elname[NUMELTS]=
	{"LP","H","He","Li","Be","B","C","N","O","F","Ne",
	 "Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca",
	 "Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu",
	 "Zn","Ga","Ge","As","Se""Br","Kr"};




/* creating atoms, bonds, etc */

/** uses global Nexatom, atom, element, cur, old, Dt, Dx, Boltz, and
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
	atom[Nexatom].bucket = NULL;
	avg[Nexatom]=posn;
	Nexatom++;
	
}


/** file reading */

int done = 0;

void xyz_frame_read(void) {
	
	char buf[128];
	int i, j, n, ord;
	struct xyz vec1, vec2;

	Nexatom = 0;   // overwrite any old atoms
	fgets(buf, 127, inf);
	j = sscanf(buf, "%d", &n);   // get the number of atoms
	if (j == 0) {
		// end of file!
		done = 1;
		return;
	}
	fgets(buf, 127, inf);  // ignore next line of input
	for (i = 0; i < n; i++) {
		char element_name[4];
		float x, y, z;
		element_name[0] = '\0';
		fgets(buf, 127, inf);
		j = sscanf(buf, "%s %lf %lf %lf", element_name, &vec1.x, &vec1.y, &vec1.z);
		if (j < 4) {
			done = 1;
			return;
		}
		// look up the index for this element
		ord = 0;   // if unknown, call it a lone pair
		for (j = 0; j < NUM_ELEMENTS_KNOWN; j++) {
			if (strcmp(element_name, element[j].symbol) == 0) {
				ord = j;
				break;
			}
		}
		makatom(ord,vec1);
	}

	/* center the damn thing, and find the bounding box */
	Center.x = Center.y = Center.z = 0.0;
	for (i = 0; i < Nexatom; i++) {
		Center.x += avg[i].x;
		Center.y += avg[i].y;
		Center.z += avg[i].z;
	}
	Center.x /= Nexatom;
	Center.y /= Nexatom;
	Center.z /= Nexatom;
	for (i = 0; i < Nexatom; i++) {
		avg[i].x -= Center.x;
		avg[i].y -= Center.y;
		avg[i].z -= Center.z;
	}
	Center.x = Center.y = Center.z = 0.0;

	/* find bounding box */

	double xmin, xmax, ymin, ymax, zmin, zmax;
	xmin = xmax = avg[0].x;
	ymin = ymax = avg[0].y;
	zmin = zmax = avg[0].z;

	for (i=1; i<Nexatom; i++) {
		if (avg[i].x < xmin) xmin = avg[i].x;
		if (avg[i].x > xmax) xmax = avg[i].x;
		if (avg[i].y < ymin) ymin = avg[i].y;
		if (avg[i].y > ymax) ymax = avg[i].y;
		if (avg[i].z < zmin) zmin = avg[i].z;
		if (avg[i].z > zmax) zmax = avg[i].z;
	}
	Bbox[0].x = xmin;
	Bbox[0].y = ymin;
	Bbox[0].z = zmin;
	Bbox[1].x = xmax;
	Bbox[1].y = ymax;
	Bbox[1].z = zmax;
}





static int ShotNo=0;

void keyboard(unsigned char key, int x, int y) {
	
	if (key == '?') DBGPRINTF("\n\
q -- quit\n\
s -- snapshot\n");
	
	if (key == 'q') exit(0);
	if (key == 's') snapshot(ShotNo++);
	
	// calcloop(((key == 'z') ? 1 : 5));
	xyz_frame_read();
	if (done)
		exit(0);
	display();
}

/**
 * The main loop for the whole kittenkaboodle
 */

main(int argc,char **argv)
{
	inf = fopen("dumpstruct.xyz", "r");
	xyz_frame_read();
	display_init(&argc, argv);
	display_mainloop();
	display_fini();
	fclose(inf);
	
	return 0;
}

/*
 * Local Variables:
 * c-basic-offset: 8
 * tab-width: 8
 * End:
 */
