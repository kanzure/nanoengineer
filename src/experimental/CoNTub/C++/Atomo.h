#ifndef ATOMO_H_INCLUDED
#define ATOMO_H_INCLUDED

#include "pto3D.h"
#include "TabPe.h"

class Color;

class Atomo
{
    int tipo;
    int selec;
    char * etiq;
    char * pers;
    Color *color;
    double r;		//de doubles
    int *mconec;
    int *mconecA;		//array de conec alternativas (para newzmat)
    tabPe *TablaP;
    int index;

 public:
    pto3D *vert;

    Atomo () {
	vert = new pto3D (0.0, 0.0, 0.0);
	tipo = 0;
	r = 0.0;
	selec = 0;
	color = NULL; //Color.black;
	etiq = "  ";
	pers = "  ";
	mconec = new int[10];
	mconecA = new int[10];
	TablaP = tabPe_getInstance();
    }

    Atomo (int t, int s, char * e, char * p, pto3D *pto, Color *c, double radio) {
	tipo = t;
	etiq = e;
	pers = p;
	vert = pto->clona ();
	color = c;
	r = radio;
	mconec = new int[10];
	mconecA = new int[10];
	TablaP = tabPe_getInstance();
    }

    Atomo (pto3D *p, int t) {
	TablaP = tabPe_getInstance();
	tipo = t;
	vert = p->clona ();
	etiq = TablaP->getSimbolo (t);
	pers = "  ";
	color = TablaP->getColor (t);
	r = TablaP->getSize (t);
	mconec = new int[10];
	mconecA = new int[10];
    }

    Atomo (pto3D *p, int t, Color *c) {
	TablaP = tabPe_getInstance();
	tipo = t;
	vert = p->clona ();
	etiq = TablaP->getSimbolo (t);
	pers = "  ";
	color = c;
	r = TablaP->getSize (t);
	mconec = new int[10];
	mconecA = new int[10];
    }
};

#endif
