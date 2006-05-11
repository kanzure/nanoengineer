#ifndef MINIMOL_H_INCLUDED
#define MINIMOL_H_INCLUDED

#include "pto3D.h"
#include "String.h"
#include "Color.h"
#include "MoleculaB.h"

class Minimol
{
    String *minietiqs;
    String *miniperss;
    float *minisizes;
    Color *minicolor;
    int *miniselec;
    double xmin, xmax, ymin, ymax, zmin, zmax;

public:
    int nvert;
    pto3D *miniverts;
    int **miniconec;

    Minimol (int nv)
    {
	nvert = nv;
	miniverts = new pto3D[nvert];
	minietiqs = new String[nvert];
	miniperss = new String[nvert];
	minisizes = new float[nvert];
	minicolor = new Color[nvert];
	miniselec = new int[nvert];
	miniconec = new int*[nvert];
	for (int i = 0; i < nvert; i++) {
	    miniconec[i] = new int[10];
	}
    }


    Minimol (MoleculaB mo)
    {
	//Creacion de una minimolecula rapida para manipulacion dentro de un visor 3D
	//A partir de una molecula compleja tipo MoleculaB
	nvert = mo.susatomos.size ();
	miniverts = new pto3D[nvert];
	minietiqs = new String[nvert];
	miniperss = new String[nvert];
	minisizes = new float[nvert];
	minicolor = new Color[nvert];
	miniselec = new int[nvert];
	miniconec = new int*[nvert];
	for (int i = 0; i < nvert; i++) {
	    miniconec[i] = new int[10];
	    Atomo *at = mo.susatomos.get(i);
	    miniverts[i] = pto3D (at->vert.x, at->vert.y, at->vert.z);
	    minietiqs[i] = at->etiq;
	    miniperss[i] = at->pers;
	    minisizes[i] = (float) at->r;
	    minicolor[i] = at->color;
	    miniselec[i] = 0;
	    for (int j = 0; j < 10; j++)
		miniconec[i][j] = at->mconec[j];
	}
    }


    void vaciar ();
    void girox (double th);
    void giroy (double th);
    void giroz (double th);
    double getDim ();
    double distancia (int a, int b);
    double angulo (int a, int b, int c);	//OJO EN GRADOS;
    double dihedro (int a, int b, int c, int d);
    int selecstatus (int i);
    void selecciona (int i, int status);
    void deselecciona ();
    Minimol clona ();
    double getLejania ();
};

#endif
