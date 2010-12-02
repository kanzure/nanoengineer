// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
#ifndef ANILLO_H_INCLUDED
#define ANILLO_H_INCLUDED

#include <iostream>
#include <stdlib.h>

#include "pto3D.h"
#include "MoleculaT.h"
#include "String.h"

// http://groups.google.com/group/alt.sources/msg/b92b1a812b1cf4c1?dmode=source

class anillo
{
 public:
    int num;
    int *vert;
    pto3D centroide;

    anillo () {
	num = 0;
	centroide = INVALID_PTO3D;
	vert = new int[15];
    }

    void addVert (int pton);
    void setCentro (pto3D cide);
    void centracentroide (MoleculaT mol);
    void ordena (pto3D vecref, MoleculaT mol);
    void ordenaccw (int ini, MoleculaT mol);
    void ordenacw (int ini, MoleculaT mol);
    void rota (int giro);
    std::ostream& operator<< (const anillo&);
};

#endif
