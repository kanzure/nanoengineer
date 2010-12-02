// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/* $Id$ */

#include <math.h>

#include "Nanotubo.h"

int primos[] = { 1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
		 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 1 };

Nanotubo::Nanotubo (int I, int J)
{
    i1 = I;
    i2 = J;
    ordenmin = 1;  // orden --> order
    _d = 1;
    A = 2.46;

    int nn = i1, mm = i2;
    altura = new double[100];
    phi = new double[100];

    // find common factors between nn and mm, move them to d
    for (int i = 1; i <= 25; i++) {
	for (int j = 1; ((nn % primos[i]) == 0)
		 && ((mm % primos[i]) == 0); j++) {
	    nn = nn / primos[i];
	    mm = mm / primos[i];
	    _d = _d * primos[i];
	}}

    deltaz1 = A * sin (M_PI / 3 - quiral ());
    deltaz2 = A * sin (quiral ());	//esto, al estar bajo Q, es positivo cuando deberia ser negativo! OJO a esto!
    // this, when being under Q, is positive when it would have to be negative! WATCH this!
    deltaphi1 = A / radio () * cos (M_PI / 3 - quiral ());
    deltaphi2 = A / radio () * cos (quiral ());

    altura[1] = deltaz1;
    phi[1] = deltaphi1;

    for (int i = 2; i <= (i1 + i2) / _d; i++) {
	if (altura[i - 1] < 0) {
	    altura[i] = altura[i - 1] + deltaz1;
	    phi[i] = phi[i - 1] + deltaphi1;
	} else {
	    altura[i] = altura[i - 1] - deltaz2;
	    phi[i] = phi[i - 1] + deltaphi2;
	}

	if ((altura[i] < altura[ordenmin]) == (altura[i] > 0.0001))
	    ordenmin = i;
    }
}
Nanotubo::Nanotubo (int I, int J, double aalt)
{

    A = aalt;
    i1 = I;
    i2 = J;
    ordenmin = 1;
    _d = 1;
    A = 2.46;

    int nn = i1, mm = i2;
    altura = new double[100];
    phi = new double[100];

    for (int i = 1; i <= 25; i++) {
	for (int j = 1; ((nn % primos[i]) == 0)
		 && ((mm % primos[i]) == 0); j++) {
	    nn = nn / primos[i];
	    mm = mm / primos[i];
	    _d = _d * primos[i];
	}}

    deltaz1 = A * sin (M_PI / 3 - quiral ());
    deltaz2 = A * sin (quiral ());
    deltaphi1 = A / radio () * cos (M_PI / 3 - quiral ());
    deltaphi2 = A / radio () * cos (quiral ());

    altura[1] = deltaz1;
    phi[1] = deltaphi1;

    for (int i = 2; i <= (i1 + i2) / _d; i++) {
	if (altura[i - 1] < 0) {
	    altura[i] = altura[i - 1] + deltaz1;
	    phi[i] = phi[i - 1] + deltaphi1;
	} else {
	    altura[i] = altura[i - 1] - deltaz2;
	    phi[i] = phi[i - 1] + deltaphi2;
	}

	if ((altura[i] < altura[ordenmin]) == (altura[i] > 0.0001))
	    ordenmin = i;
    }
}

double Nanotubo::deltaz ()
{
    return altura[ordenmin];
}
double Nanotubo::deltaphi ()
{
    return phi[ordenmin];
}
double Nanotubo::radio ()
{
    return A * sqrt (i1 * i1 + i2 * i2 + i2 * i1) / (2 * M_PI);
}
double Nanotubo::quiral ()
{
    double ang = atan (sqrt (3) * i2 / (2 * i1 + i2));
    if (2 * i1 + i2 < 0)
	ang += (M_PI);
    return ang;
}
double Nanotubo::quiralg ()
{
    return quiral () * (180.0 / M_PI);
}
double Nanotubo::deltazc ()
{
    return A / sqrt (3) * cos (quiral ());
}
double Nanotubo::deltaphic ()
{
    return A / sqrt (3) / radio () * sin (quiral ());
}
int Nanotubo::d ()
{
    return _d;
}

double Nanotubo::energia (double momm, double momz)
{
    double numfase = sin (momz * deltaz1 + momm * deltaphi1) +
	sin (momz * (deltaz1 + deltaz2) + momm * (deltaphi1 - deltaphi2));
    double denfase = 1 + cos (momz * deltaz1 + momm * deltaphi1) +
	cos (momz * (deltaz1 + deltaz2) + momm * (deltaphi1 - deltaphi2));
    double energ = sqrt (numfase * numfase + denfase * denfase);
    return energ;
}
