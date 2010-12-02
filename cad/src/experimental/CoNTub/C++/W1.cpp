// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
#include <iostream>
#include <math.h>
#include <stdlib.h>

#include "W1.h"
#include "Nanotubo.h"

/*
 * (a, b) - nanotube chirality
 * c - nanotube length in angstroms
 * terminator - an element number for terminating atoms, ignored if not HYDROGEN or NITROGEN
 */
W1::W1(int a, int b, double c, int terminator)
{
    molecule = MoleculaT ();
    molecule.vaciar ();   // vaciar --> empty/clear: remove all atoms and bonds
    Nanotubo NT = Nanotubo (a, b);

    // estimated number of atoms
    // int guess = (int) (NT.radio () * 2 * M_PI * c * 0.34);
    // In the original code, this was used as a basis to not compute structures that were
    // too big. I think the reason for not doing them was that they took too long with
    // bond enumeration as an order-N-squared operation.

    double x, xc, y, yc, z, zc;
    for (int i = 1; i * NT.deltaz () <= c; i++) {
	for (int j = 1; j <= NT.d (); j++) {
	    x = NT.deltaz () * i;
	    xc = NT.deltaz () * i + NT.deltazc ();
	    y = NT.radio () * (float) sin (NT.deltaphi () * i +
					   2 * (float) M_PI / NT.d () * j);
	    yc = NT.radio () * (float) sin (NT.deltaphi () * i +
					    NT.deltaphic () +
					    2 * (float) M_PI / NT.d () * j);
	    z = NT.radio () * (float) cos (NT.deltaphi () * i +
					   2 * (float) M_PI / NT.d () * j);
	    zc = NT.radio () * (float) cos (NT.deltaphi () * i +
					    NT.deltaphic () +
					    2 * (float) M_PI / NT.d () * j);
	    molecule.addVert (x, y, z, 6);
	    molecule.addVert (xc, yc, zc, 6);
	}
    }
    finish(terminator);
}

int main(int argc, char *argv[])
{
    int a, b, terminator, index;
    double c;
    char *p;

    if (argc < 6)
	goto bad_input;
    a = strtol(argv[1], &p, 10);
    if (*p != '\0') goto bad_input;
    b = strtol(argv[2], &p, 10);
    if (*p != '\0') goto bad_input;
    c = strtod(argv[3], &p);
    if (*p != '\0') goto bad_input;
    terminator = strtol(argv[4], &p, 10);
    if (*p != '\0') goto bad_input;
    index = strtol(argv[5], &p, 10);
    if (*p != '\0') {
    bad_input:
	std::cerr << "BAD INPUT\n";
	return -1;
    }
    W1 w1 = W1(a, b, c, terminator);
    w1.molecule.mmp(std::cout, index);
    return 0;
}
