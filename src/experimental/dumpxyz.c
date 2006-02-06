// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "mol.h"

/**
 * @file
 *
 * Instead of sending frames to an OpenGL pane, let's dump frames as a
 * sequence of XYZ snapshots. Because it's a 3D representation, the
 * display animation program can place light sources and the camera
 * wherever we want.
 *
 * Info about sequential XYZ file format:
 * http://willware.net:8080/xyz2rgb.html
 */


FILE *outf;


/**
 */
void display(void) {
}

/**
 */
void snapshot(int n) {
	int i,j;
	fwrite(&Nexatom, sizeof(int), 1, outf);
	for (i=0; i<Nexatom; i++) {
		if (atom[i].disp == 0)
			continue;
		fwrite(&atom[i].elt, sizeof(int), 1, outf);
		fwrite(&avg[i], sizeof(struct xyz), 1, outf);
	}
}


/**
 */
void display_init(int *argc, char *argv[]) {
	outf = fopen("dumpstruct.xyz", "w");  // humorously homophonic with "dumptruck"
}


/**
 */
void display_fini(void) {
	fclose(outf);
}

/**
 */
void display_mainloop() {
	int x;
	printf("making movie\n");
	for (x=0; x<100; x++) {
		printf(" %d", x);
		fflush(stdout);
		if ((x & 15) == 15)
			printf("\n");
		calcloop(15);
		snapshot(x);
	}
	printf("\n");
}

/*
 * Local Variables:
 * c-basic-offset: 8
 * tab-width: 8
 * End:
 */
