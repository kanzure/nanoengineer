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



extern int DumpAsText;
extern char OutFileName[];
extern int ToMinimize;
extern int IterPerFrame;
extern int NumFrames;

FILE *outf;
int *ixyz, *previxyz, *temp, ibuf1[NATOMS*3], ibuf2[NATOMS*3];

/**
 */
void display(void) {
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
	    ixyz[i+2] = (int(avg[j].z;
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


/**
 */
void display_init(int *argc, char *argv[]) {
    int i,j;

    if (DumpAsText) outf = fopen(OutFileName, "w");  
    // humorously homophonic with "Pout/smile game" :-) 
    else {
	ixyz=ibuf1;
	previxyz=ibuf2;
	for (i=0, j=0; i<3*Nexatom; i+=3, j++) {
	    previxyz[i+0] = (int)cur[j].x;
	    previxyz[i+1] = (int)cur[j].y;
	    previxyz[i+2] = (int)cur[j].z;

	    //printf("qq %d %d %d\n",previxyz[i+0],previxyz[i+1],previxyz[i+2]);
	}
	outf = fopen(OutFileName, "wb");  
	fwrite(&NumFrames, sizeof(int), 1, outf);
    }
}

/**
 */
void display_fini() {
    fclose(outf);
    printf("\n");
}

/**
 */
void display_mainloop() {
    int i;
    printf("running simulation\n");
    for (i=0; i<NumFrames; i++) {
	printf(" %d", i);
	fflush(stdout);
	if ((i & 15) == 15)
	    printf("\n");
	calcloop(IterPerFrame/10);
	snapshot(i);
    }
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
