// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.
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
	j = fread(&n, sizeof(int), 1, inf);   // get the number of atoms
	if (j < 1) {
		done = 1;    // end of file!
		return;
	}

	Center.x = Center.y = Center.z = 0.0;
	for (i = 0; i < n; i++) {
		int elt;
		struct xyz posn;
		j = fread(&elt, sizeof(int), 1, inf);
		if (j < 1) {
			done = 1;   // end of file!
			return;
		}
		j = fread(&posn, sizeof(struct xyz), 1, inf);
		if (j < 1) {
			done = 1;   // end of file!
			return;
		}
		Center.x += posn.x;
		Center.y += posn.y;
		Center.z += posn.z;
		makatom(elt, posn);
	}

	Center.x /= Nexatom;
	Center.y /= Nexatom;
	Center.z /= Nexatom;

	double xmin, xmax, ymin, ymax, zmin, zmax;
	xmin = xmax = 0.0;
	ymin = ymax = 0.0;
	zmin = zmax = 0.0;

	for (i = 0; i < Nexatom; i++) {
		avg[i].x -= Center.x;
		avg[i].y -= Center.y;
		avg[i].z -= Center.z;
		if (avg[i].x < xmin) xmin = avg[i].x;
		if (avg[i].x > xmax) xmax = avg[i].x;
		if (avg[i].y < ymin) ymin = avg[i].y;
		if (avg[i].y > ymax) ymax = avg[i].y;
		if (avg[i].z < zmin) zmin = avg[i].z;
		if (avg[i].z > zmax) zmax = avg[i].z;
	}

	/* now everybody is centered around zero */
	Center.x = Center.y = Center.z = 0.0;

	/* set up bounding box */
	Bbox[0].x = xmin - 100.0;
	Bbox[0].y = ymin - 100.0;
	Bbox[0].z = zmin - 100.0;
	Bbox[1].x = xmax + 100.0;
	Bbox[1].y = ymax + 100.0;
	Bbox[1].z = zmax + 100.0;
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
