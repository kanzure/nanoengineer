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

	fprintf(outf, "%d\n", Nexatom);
	fprintf(outf, "Frame %d\n", n);
	for (i=0; i<Nexatom; i++) {
		if (atom[i].disp == 0)
			continue;
		fprintf(outf, "%s ", element[atom[i].elt].symbol);
		fprintf(outf, "%g ", avg[i].x);
		fprintf(outf, "%g ", avg[i].y);
		fprintf(outf, "%g\n", avg[i].z);
	}

// For now, don't worry about bonds

//	for (j=0; j<Nexbon; j++) {
//		if (atom[bond[j].an1].disp==1 || atom[bond[j].an2].disp==1) {
//			glVertex3d(avg[bond[j].an1].x,
//				   avg[bond[j].an1].y,avg[bond[j].an1].z);
//			glVertex3d(avg[bond[j].an2].x,
//				   avg[bond[j].an2].y,avg[bond[j].an2].z);
//		}
//	}
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
	for (x=0; x<1000; x++) {
		printf(" %d", x);
		fflush(stdout);
		if ((x & 15) == 15)
			printf("\n");
		calcloop(15);
		snapshot(x);
	}
}

/*
 * Local Variables:
 * c-basic-offset: 8
 * tab-width: 8
 * End:
 */
