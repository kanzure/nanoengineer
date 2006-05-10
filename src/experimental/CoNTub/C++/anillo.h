#ifndef ANILLO_H_INCLUDED
#define ANILLO_H_INCLUDED

#include <stdlib.h>

#include "pto3D.h"
#include "MoleculaT.h"
#include "String.h"

// http://groups.google.com/group/alt.sources/msg/b92b1a812b1cf4c1?dmode=source

class anillo
{
    int num;
    pto3D *centroide;
    int *vert;

 public:
    anillo () {
	num = 0;
	centroide = NULL;
	vert = new int[15];
    }

    void addVert (int pton);
    void setCentro (pto3D *cide);
    String *poncentroide (MoleculaT *mol);
    void centracentroide (MoleculaT *mol);
    void ordena (pto3D *vecref, MoleculaT *mol);
    void ordenaccw (int ini, MoleculaT *mol);
    void ordenacw (int ini, MoleculaT *mol);
    void rota (int giro);
    String *aCadena ();
};

#endif
