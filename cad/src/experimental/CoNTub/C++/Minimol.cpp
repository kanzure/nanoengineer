// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
#include <math.h>
#include "Minimol.h"

void Minimol::vaciar ()
{
}

//void deseleccionar(){for (int i = 0; i<susatomos.size();i++) ((Atomo)susatomos.get(i)).selec=0; nselec=0;}
//HABRIA QUE PONER HERRAMIENTAS DE SELECCIONADO

void Minimol::girox (double th)
{
    for (int i = 0; i < nvert; i++) {
	float ct = (float) cos (th / 180 * M_PI);
	float st = (float) sin (th / 180 * M_PI);
	miniverts[i].rgirox (ct, st);
    }
}
void Minimol::giroy (double th)
{
    for (int i = 0; i < nvert; i++) {
	float ct = (float) cos (th / 180 * M_PI);
	float st = (float) sin (th / 180 * M_PI);
	miniverts[i].rgiroy (ct, st);
    }
}
void Minimol::giroz (double th)
{
    for (int i = 0; i < nvert; i++) {
	float ct = (float) cos (th / 180 * M_PI);
	float st = (float) sin (th / 180 * M_PI);
	miniverts[i].rgiroz (ct, st);
    }
}

double Minimol::getDim ()
{
    double Dim = 0.01;
    for (int i = 0; i < nvert; i++) {
	for (int j = i + 1; j < nvert; j++) {
	    pto3D v = miniverts[i];
	    pto3D w = miniverts[j];
	    double dist = v.dista (w);
	    if (dist > Dim)
		Dim = dist;
	}
    }
    return Dim;
}


double Minimol::distancia (int a, int b)
{
    pto3D v = miniverts[a];
    pto3D w = miniverts[b];
    return v.dista (w);
}

double Minimol::angulo (int a, int b, int c)	//OJO EN GRADOS
{
    pto3D v = miniverts[a];
    pto3D w = miniverts[b];
    pto3D u = miniverts[c];
    return u.menos (w).angulocong (v.menos (w));
}

double Minimol::dihedro (int a, int b, int c, int d)
{
    pto3D v = miniverts[a];
    pto3D w = miniverts[b];
    pto3D u = miniverts[c];
    pto3D s = miniverts[d];
    pto3D v1 = v.menos (w);
    pto3D v2 = w.menos (u);
    pto3D v3 = s.menos (u);
    return v1.dihedrog (v2, v3);
}			//OJO EN GRADOS


int Minimol::selecstatus (int i)
{
    return miniselec[i];
}
void Minimol::selecciona (int i, int status)
{
    miniselec[i] = status;
}
void Minimol::deselecciona ()
{
    for (int i = 0; i < nvert; i++)
	miniselec[i] = 0;
}

Minimol Minimol::clona ()
{
    Minimol mmn = Minimol (nvert);

    for (int i = 0; i < nvert; i++) {
	mmn.miniverts[i] = miniverts[i].clona ();
	mmn.minietiqs[i] = minietiqs[i];
	mmn.miniperss[i] = miniperss[i];
	mmn.minisizes[i] = minisizes[i];
	mmn.miniselec[i] = miniselec[i];
	for (int j = 0; j < 10; j++)
	    mmn.miniconec[i][j] = miniconec[i][j];

    }
    return mmn;
}

double Minimol::getLejania ()
{
    double lej = 0;
    if (nvert == 1)
	return 0;
    for (int i = 0; i < nvert; i++) {
	pto3D v = miniverts[i];
	pto3D c = pto3D (0, 0, 0);
	double dist = v.dista (c);
	if (dist > lej)
	    lej = dist;
    }
    return lej;
}
