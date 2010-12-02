// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/* $Id$ */

#include <math.h>
#include "pto3D.h"
#include "pto2D.h"

void pto3D::giroxr (double theta)
{
    double ct = cos (theta);
    double st = sin (theta);
    float Ny = (float) (y * ct + z * st);
    float Nz = (float) (-y * st + z * ct);
    y = Ny;
    z = Nz;
}
void pto3D::giroxg (double thetag)
{
    giroxr (thetag * (M_PI / 180));
}			//GRADOS

/** rotate theta degrees about the y axis */
void pto3D::giroyr (double theta)
{
    double ct = cos (theta);
    double st = sin (theta);
    float Nx = (float) (x * ct + z * st);
    float Nz = (float) (-x * st + z * ct);
    x = Nx;
    z = Nz;
}
void pto3D::giroyg (double thetag)
{
    giroyr (thetag * (M_PI / 180));
}			//GRADOS

/** rotate theta degrees about the z axis */
void pto3D::girozr (double theta)
{
    double ct = cos (theta);
    double st = sin (theta);
    float Nx = (float) (x * ct + y * st);
    float Ny = (float) (-x * st + y * ct);
    x = Nx;
    y = Ny;
}
void pto3D::girozg (double thetag)
{
    girozr (thetag * (M_PI / 180));
}			//GRADOS

//METODOS RAPIDOS para los giros del visualizador, con cosenos y senos directore

void pto3D::rgirox (float ct, float st)
{
    float Ny = y * ct + z * st;
    float Nz = -y * st + z * ct;
    y = Ny;
    z = Nz;
}
void pto3D::rgiroy (float ct, float st)
{
    float Nx = x * ct + z * st;
    float Nz = -x * st + z * ct;
    x = Nx;
    z = Nz;
}
void pto3D::rgiroz (float ct, float st)
{
    float Nx = x * ct + y * st;
    float Ny = -x * st + y * ct;
    x = Nx;
    y = Ny;
}

/** rotate theta degrees about the x axis */
pto3D pto3D::ngiroxr (double theta)
{
    double ct = cos (theta);
    double st = sin (theta);
    float Ny = (float) (y * ct + z * st);
    float Nz = (float) (-y * st + z * ct);
    pto3D sal = pto3D (x, Ny, Nz);
    return sal;
}
pto3D pto3D::ngiroxg (double thetag)
{
    return ngiroxr (thetag * (M_PI / 180));
}			//GRADOS


/** rotate theta degrees about the y axis */
pto3D pto3D::ngiroyr (double theta)
{
    double ct = cos (theta);
    double st = sin (theta);
    float Nx = (float) (x * ct + z * st);
    float Nz = (float) (-x * st + z * ct);
    pto3D sal = pto3D (Nx, y, Nz);
    return sal;
}
pto3D pto3D::ngiroyg (double thetag)
{
    return ngiroyr (thetag * (M_PI / 180));
}			//GRADOS

/** rotate theta degrees about the z axis */
pto3D pto3D::ngirozr (double theta)
{
    double ct = cos (theta);
    double st = sin (theta);
    float Nx = (float) (x * ct + y * st);
    float Ny = (float) (-x * st + y * ct);
    pto3D sal = pto3D (Nx, Ny, z);
    return sal;
}
pto3D pto3D::ngirozg (double thetag)
{
    return ngirozr (thetag * (M_PI / 180));
}			//GRADOS

/** rotate theta degrees about the x axis y cierto punto*/
void pto3D::giroxr (double theta, pto3D paux)
{
    double ct = cos (theta);
    double st = sin (theta);
    x = x - paux.x;
    y = y - paux.y;
    z = z - paux.z;
    float Ny = (float) (y * ct + z * st);
    float Nz = (float) (-y * st + z * ct);
    y = Ny;
    z = Nz;
    x = x + paux.x;
    y = y + paux.y;
    z = z + paux.z;
}
void pto3D::giroxg (double thetag, pto3D pau)
{
    giroxr (thetag * (M_PI / 180), pau);
}			//GRADOS


/** rotate theta degrees about the y axis */
void pto3D::giroyr (double theta, pto3D paux)
{
    double ct = cos (theta);
    double st = sin (theta);
    x = x - paux.x;
    y = y - paux.y;
    z = z - paux.z;
    float Nx = (float) (x * ct + z * st);
    float Nz = (float) (-x * st + z * ct);
    x = Nx;
    z = Nz;
    x = x + paux.x;
    y = y + paux.y;
    z = z + paux.z;
}
void pto3D::giroyg (double thetag, pto3D pau)
{
    giroyr (thetag * (M_PI / 180), pau);
}			//GRADOS

/** rotate theta degrees about the z axis */
void pto3D::girozr (double theta, pto3D paux)
{
    double ct = cos (theta);
    double st = sin (theta);
    x = x - paux.x;
    y = y - paux.y;
    z = z - paux.z;
    float Nx = (float) (x * ct + y * st);
    float Ny = (float) (-x * st + y * ct);
    x = Nx;
    y = Ny;
    x = x + paux.x;
    y = y + paux.y;
    z = z + paux.z;
}
void pto3D::girozg (double thetag, pto3D pau)
{
    girozr (thetag * (M_PI / 180), pau);
}			//GRADOS

///////////////////////////////////////////////////

pto3D pto3D::ngirar (double theta, pto3D eje)
{
    pto3D pplano = proyeccplano (eje);
    pto3D pparal = menos (pplano);
    double radio = pplano.modulo ();
    pto3D ejsecundario = eje.prodvect (pplano);
    pto3D ejx = pplano.aversor ();
    pto3D ejy = ejsecundario.aversor ();
    pto3D vgirado = ejx.escala (radio * cos (theta)).mas (ejy.escala (radio * sin (theta)));

    pto3D ptogirado = pparal.mas (vgirado.escala (radio));

    return ptogirado;
}
pto3D pto3D::ngirag (double thetag, pto3D pau)
{
    return ngirar (thetag * (M_PI / 180), pau);
}			//GRADOS

/////////////////////////////////////////////////
pto3D pto3D::mas (pto3D pto2)
{
    pto3D suma = pto3D ();
    suma.x = x + pto2.x;
    suma.y = y + pto2.y;
    suma.z = z + pto2.z;
    return suma;
}

pto3D pto3D::menos (pto3D pto2)
{
    pto3D resta = pto3D ();
    resta.x = x - pto2.x;
    resta.y = y - pto2.y;
    resta.z = z - pto2.z;
    return resta;
}

double pto3D::prodesc (pto3D pto2)
{
    double prodesc;
    prodesc = x * pto2.x + y * pto2.y + z * pto2.z;
    return prodesc;
}


pto3D pto3D::prodvect (pto3D pto2)
{
    pto3D pv = pto3D ();
    pv.x = y * pto2.z - z * pto2.y;
    pv.y = z * pto2.x - x * pto2.z;
    pv.z = x * pto2.y - y * pto2.x;
    return pv;
}

double pto3D::dista (pto3D pto2)
{
    double dist;
    pto3D vec, pto1;
    vec = menos (pto2);
    double prod = vec.prodesc (vec);
    dist = sqrt (prod);
    return dist;
}

pto3D pto3D::escala (double factor)
{
    pto3D res = pto3D (x * factor, y * factor,
			   z * factor);
    return res;
}

double pto3D::anguloconr (pto3D pto2)
{
    double mod1 = modulo ();
    double mod2 = pto2.modulo ();
    double pe = prodesc (pto2) / mod1 / mod2;
    if (pe < -1.)
	pe = -1.;
    if (pe > 1.)
	pe = 1.;
    double sal = acos (pe);
    return sal;
}
double pto3D::angulocong (pto3D pto2)
{
    return anguloconr (pto2) * 180.0 / M_PI;
}

double pto3D::modulo ()
{
    double mod2 = prodesc (*this);
    return sqrt (mod2);
}


pto3D pto3D::proyeccplano (pto3D pto2)
{
    double mo = pto2.modulo ();	//versor pto2
    pto3D vers2 = pto2.escala (1 / mo);
    double mod2 = prodesc (vers2);	//proyeccion escalar
    pto3D ptoplo = vers2.escala (mod2);
    pto3D proy = menos (ptoplo);
    return proy;

}

double pto3D::dihedror (pto3D ptoc, pto3D pto1)
{			//ACLARACION dihedro positivo es cuando, mirando en el sentido marcado
    pto3D p2 = proyeccplano (ptoc);	//por el vector (ptoc), el vector (pto1) esta a la derecha de (this)
    pto3D p1 = pto1.proyeccplano (ptoc);
    double res = p1.anguloconr (p2);
    pto3D pp = ptoc.prodvect (p1);
    pto3D ppc = pp.escala (-1);
    if (p2.dista (pp) > p2.dista (ppc))
	res = res * -1;
    return res;
}

double pto3D::dihedrog (pto3D ptoc, pto3D pto1)
{
    return dihedror (ptoc, pto1) * 180.0 / M_PI;
}

pto3D pto3D::aversor ()
{
    pto3D p = pto3D (x, y, z);
    p.versoriza ();
    return p;
}

void pto3D::versoriza ()
{
    double mod = modulo ();
    pto3D pc = escala (1 / mod);
    x = pc.x;
    y = pc.y;
    z = pc.z;
}

pto3D pto3D::clona ()
{
    pto3D sal = pto3D (x, y, z);
    return sal;
}

pto3D pto3D::ptomediocon (pto3D v1)
{
    return ptopondcon (v1, 0.5);
}


pto3D pto3D::ptopondcon (pto3D v1, double param)
{			//ESTABAMOS CREANDO UN VERSOR MEDIO PONDERADO DE 0 A 1
    //SI 0, se parece a this, si 1, a v1!
    pto3D salida;
    if (param < 0)
	salida = clona ();
    else if (param > 1)
	salida = v1.clona ();
    else {
	pto3D cone = v1.menos (*this);
	salida = mas (cone.escala (param));
    }
    return salida;
}

pto2D pto3D::a2D (void)
{
    return pto2D (x, y);
}

#if 0
/* http://gethelp.devx.com/techtips/cpp_pro/10min/10min0400.asp */
std::ostream& operator<< (std::ostream& s, pto3D& a) {
    s << "<pto3D " << a.x << " " << a.y << " " << a.z << ">";
    return s;
}
#endif
