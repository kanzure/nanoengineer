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

void W1::finish(int terminator)
{
    molecule.centrar ();
    molecule.ponconec ();
    if (terminator == HYDROGEN) {
	molecule.cierraH ();
	molecule.ponconec ();
    } else if (terminator == NITROGEN) {
	molecule.cierraN ();
	molecule.ponconec ();
    }
}

std::ostream& W1::mmp(std::ostream& s)
{
    return molecule.mmp(s);
}

int main(int argc, char *argv[])
{
    int a, b, terminator;
    double c;
    a = atoi(argv[1]);
    b = atoi(argv[2]);
    c = atof(argv[3]);
    terminator = atoi(argv[4]);
    W1 w1 = W1(a, b, c, terminator);
    w1.mmp(std::cout);
}
