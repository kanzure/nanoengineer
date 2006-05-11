#ifndef ATOMO_H_INCLUDED
#define ATOMO_H_INCLUDED

#include "pto3D.h"
#include "TabPe.h"
#include "Color.h"

class Atomo
{
 public:
    pto3D vert;
    int *mconec;
    int selec;
    String etiq;
    String pers;
    Color color;
    double r;		//de doubles
    int tipo;
    int *mconecA;		//array de conec alternativas (para newzmat)
    tabPe TablaP;
    int index;

    Atomo () {
	vert = pto3D (0.0, 0.0, 0.0);
	tipo = 0;
	r = 0.0;
	selec = 0;
	color = BLACK;
	etiq = "  ";
	pers = "  ";
	mconec = new int[10];
	mconecA = new int[10];
	TablaP = tabPe_getInstance();
	index = -1;
    }

    Atomo (int t, int s, String e, String p, pto3D pto, Color c, double radio) {
	tipo = t;
	etiq = e;
	pers = p;
	vert = pto.clona ();
	color = c;
	r = radio;
	mconec = new int[10];
	mconecA = new int[10];
	TablaP = tabPe_getInstance();
	index = -1;
    }

    Atomo (pto3D p, int t) {
	TablaP = tabPe_getInstance();
	tipo = t;
	vert = p.clona ();
	etiq = TablaP.getSimbolo (t);
	pers = "  ";
	color = TablaP.getColor (t);
	r = TablaP.getSize (t);
	mconec = new int[10];
	mconecA = new int[10];
	index = -1;
    }

    Atomo (pto3D p, int t, Color c) {
	TablaP = tabPe_getInstance();
	tipo = t;
	vert = p.clona ();
	etiq = TablaP.getSimbolo (t);
	pers = "  ";
	color = c;
	r = TablaP.getSize (t);
	mconec = new int[10];
	mconecA = new int[10];
	index = -1;
    }
};

#endif
