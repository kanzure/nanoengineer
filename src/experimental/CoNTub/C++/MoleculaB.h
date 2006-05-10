#ifndef MOLECULAB_H_INCLUDED
#define MOLECULAB_H_INCLUDED

#include "String.h"
#include "TabPe.h"
#include "ArrayList.h"
#include "Color.h"
#include "HashMap.h"

#define MOLDEBUG  0

class MoleculaB
{
    int nselec;
    String info;		//pequeña cadena informativa para pasar un mini titulo
    // small informative string to pass a short title
    double xmin, xmax, ymin, ymax, zmin, zmax;
    tabPe TablaP;   // periodic table - this could be a singlet

    ArrayList getBucket(HashMap buckets, pto3D v);
    ArrayList getNeighborhood(HashMap buckets, pto3D v);

 public:
    ArrayList susatomos;	//de ATOMOS, literally, "his atoms"

    MoleculaB () {
	TablaP = tabPe_getInstance();
	nselec = 0;
	info = String("");
    }

    void addVert (pto3D punto, int ti, Color c);
    void addVert (pto3D punto, int ti);
    void addVert (double x, double y, double z, int ti);
    void addVert (double x, double y, double z, int ti, String e);
    void addVert (pto3D p, int ti, String e);
    double getDim ();
    double getLejania ();
    void vaciar ();
    void deseleccionar ();
    void centrar ();
    void giroxr (double th);
    void giroyr (double th);
    void girozr (double th);
    void giroxg (double th);
    void giroyg (double th);
    void girozg (double th);
    MoleculaB clona ();
    void rm (int n);
    void rmlast (int n);
    void rmlast ();
    int ocupa1 (pto3D pto1);
    int ocupa (pto3D pto1, double limite);
    int ocupa2 (pto3D pto1);
    int atomoqueocupa1 (pto3D pto);
    int atomoqueocupa (pto3D pto, double limite);
    int atomoqueocupa2 (pto3D pto);
    void mueve (int num, double x, double y, double z);
    void mueve (int s, pto3D pto);
    void sustituye (int num, int ti, pto3D pto);
    void ponconec ();
    void ponconec (double param);
    void ponconecsafe ();
    void reconec ();
    void reconec (double param);
    void reconecsafe ();

    //metodo paraeliminar conectividades redundantes, angulos demasiado pequeños (<60, en principio)
    int depuraconec ();

    //metodo paraeliminar conectividades redundantes, angulos demasiado pequeños (<60, en principio);
    void centraentorno (int num);
    void centraentorno ();
    void conecta (int i, int j);
    void conectaA (int i, int j);
    void desconecta (int i, int j);
    double distancia (int a, int b);
    double angulo (int a, int b, int c);
    double dihedro (int a, int b, int c, int d);
    int nvec (int i);
    int nvert ();
    pto3D vert (int i);
    int tipo (int i);
    String etiq (int i);
    String pers (int i);
    Color color (int i);
    double r (int i);
    int selecstatus (int i);
    void selecciona (int i, int status);
    void setInfo (String in);
    String getInfo ();
    void marcaborra (int aborrar);
    void borramarcados ();
};

#endif
