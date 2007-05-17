// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/* $Id$ */

#include <iostream>
#include <math.h>
#include <stdlib.h>

#include "W15.h"
#include "Nanotubo.h"

W15::W15(int a, int b, double c, int nshells, double sshell, int terminator)
{
    Nanotubo NT = Nanotubo (a, b);
    molecule = MoleculaT ();
    String s = String("Multi-walled nanotube with inner indices (");
    s += a;
    s += ",";
    molecule.setInfo (String("Multi-walled nanotube with inner indices (") +
		      a + "," + b + ")" + " and " + nshells + " shells");

    double x, xc, y, yc, z, zc;
    for (int i = 1; i * NT.deltaz () <= c; i++) {
	for (int j = 1; j <= NT.d (); j++) {
	    x = NT.deltaz () * i;
	    xc = NT.deltaz () * i + NT.deltazc ();
	    y = NT.radio () * (float) sin (NT.deltaphi () * i + 2 * (float) M_PI / NT.d () * j);
	    yc = NT.radio () * (float) sin (NT.deltaphi () * i + NT.deltaphic () + 2 * (float) M_PI / NT.d () * j);
	    z = NT.radio () * (float) cos (NT.deltaphi () * i + 2 * (float) M_PI / NT.d () * j);
	    zc = NT.radio () * (float) cos (NT.deltaphi () * i + NT.deltaphic () + 2 * (float) M_PI / NT.d () * j);
	    molecule.addVert (x, y, z, 6);
	    molecule.addVert (xc, yc, zc, 6);

	}
    }

    //GENERAMOS EL RESTO DE CAPAS
    double A = 2.46;
    double dz1 = A * sin (M_PI / 3 - NT.quiral ());
    double dz2 = A * sin (NT.quiral ());
    double dx1 = A * cos (M_PI / 3 - NT.quiral ());
    double dx2 = A * cos (NT.quiral ());
    int ni = a;
    int nj = b;
    double zeta = 0;

    double cshell = NT.radio () * 2 * M_PI;	//circungitud primera capa
    double radpaso = NT.radio () * 2 * M_PI;	//que a su vez es inicio


    for (int j = 1; j <= nshells - 1; j++) {
	cshell = cshell + sshell * 2 * M_PI;	//Objetivo

	for (int k = 0; radpaso < cshell; k++) {	//radpaso busca al objetivo
	    if (zeta < 0) {
		nj++;
		zeta = zeta + dz2;
		radpaso = radpaso + dx2;
	    } else {
		ni++;
		zeta = zeta - dz1;
		radpaso = radpaso + dx1;
	    }
	}

	Nanotubo NTC = Nanotubo (ni, nj);

	for (int i = 1; i * NTC.deltaz () <= c; i++) {
	    for (int k = 1; k <= NTC.d (); k++) {
		x = NTC.deltaz () * i;
		xc = NTC.deltaz () * i + NTC.deltazc ();
		y = NTC.radio () * (float) sin (NTC.deltaphi ()
						* i + 2 * (float)
						M_PI / NTC.d () * k);
		yc = NTC.radio () * (float) sin (NTC.deltaphi ()
						 * i + NTC.deltaphic ()
						 + 2 * (float)
						 M_PI / NTC.d () * k);
		z = NTC.radio () * (float) cos (NTC.deltaphi ()
						* i + 2 * (float)
						M_PI / NTC.d () * k);
		zc = NTC.radio () * (float) cos (NTC.deltaphi ()
						 * i + NTC.deltaphic ()
						 + 2 * (float)
						 M_PI / NTC.d () * k);
		molecule.addVert (x, y, z, 6);
		molecule.addVert (xc, yc, zc, 6);
	    }
	}
    }
    finish(terminator);
}

int main(int argc, char *argv[]) {
    int a, b, nshell, terminator, index;
    double c, sshell;
    char *p, *outputfile;

    if (argc < 9)
	goto bad_input;
    a = strtol(argv[1], &p, 10);
    if (*p != '\0') goto bad_input;
    b = strtol(argv[2], &p, 10);
    if (*p != '\0') goto bad_input;
    c = strtod(argv[3], &p);
    if (*p != '\0') goto bad_input;
    nshell = strtol(argv[4], &p, 10);
    if (*p != '\0') goto bad_input;
    sshell = strtod(argv[5], &p);
    if (*p != '\0') goto bad_input;
    terminator = strtol(argv[6], &p, 10);
    if (*p != '\0') goto bad_input;
    index = strtol(argv[7], &p, 10);
    if (*p != '\0') {
    bad_input:
	std::cerr << "BAD INPUT\n";
	return -1;
    }
    outputfile = argv[8];
    W15 w15 = W15(a, b, c, nshell, sshell, terminator);
    w15.molecule.mmp(outputfile, index);
    return 0;
}
