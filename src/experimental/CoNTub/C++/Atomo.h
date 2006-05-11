#ifndef ATOMO_H_INCLUDED
#define ATOMO_H_INCLUDED

#include "pto3D.h"
#include "TabPe.h"

class Atomo
{
 public:
    pto3D vert;
    int *mconec;
    int selec;
    String etiq;
    String pers;
    double r;		//de doubles
    int tipo;
    int *mconecA;		//array de conec alternativas (para newzmat)
    int index;

    Atomo () {
	vert = pto3D (0.0, 0.0, 0.0);
	tipo = 0;
	r = 0.0;
	selec = 0;
	etiq = "  ";
	pers = "  ";
	mconec = new int[10];
	mconecA = new int[10];
	index = -1;
    }

    Atomo (pto3D p, int t) {
	tipo = t;
	vert = p.clona ();
	etiq = periodicTable()->getSimbolo (t);
	pers = "  ";
	r = periodicTable()->getSize (t);
	mconec = new int[10];
	mconecA = new int[10];
	index = -1;
    }

    friend std::ostream& operator<< (std::ostream& s, const Atomo& a) {
	s << "<Atom " << a.index << " " <<
	    a.vert.x << " " << a.vert.y << " " << a.vert.z << ">";
	return s;
    }
};

#endif
