/* $Id$ */

#ifndef W2_H_INCLUDED
#define W2_H_INCLUDED

#include "pto3D.h"
#include "W1.h"

#define GAP   15.0	//val absoluto de zona de deformacion
#define GMI   2.0	//val absoluto de zona de no deformacion

class W2: public W1
{
	pto3D aproxNT (pto3D pto,	//pto es el punto a aproximar
		       int atotip, int posi, int posj, pto3D origen, int i, int j,
		       pto3D orient, pto3D inicio, double coef);
	pto3D aproxNTchap (pto3D pto,	//pto es el punto a aproximar
				   int atotip, int posi, int posj, pto3D origen,
				   int i, int j, pto3D orient, pto3D inicio, double coef);
	int detectanconc (pto2D pA, pto2D pB, pto2D pC, pto2D pD);
 public:
	W2(int i1, int j1, double lent1, int i2, int j2, double lent2, int terminator);
};

#endif
