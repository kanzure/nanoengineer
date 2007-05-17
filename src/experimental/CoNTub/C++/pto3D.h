// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
#ifndef PTO3D_H_INCLUDED
#define PTO3D_H_INCLUDED

#include <iostream>
#include "String.h"

class pto2D;  // do not include pto2D.h here: circular definition

class pto3D
{
 public:
    float x, y, z;

    pto3D (void) {
	x = 0.0f;
	y = 0.0f;
	z = 0.0f;
    }
    pto3D (double X, double Y, double Z) {
	x = (float) X;
	y = (float) Y;
	z = (float) Z;
    }

    void giroxr (double theta);
    void giroxg (double thetag);
    void giroyr (double theta);
    void giroyg (double thetag);
    void girozr (double theta);
    void girozg (double thetag);
    void rgirox (float ct, float st);
    void rgiroy (float ct, float st);
    void rgiroz (float ct, float st);
    /** rotate theta degrees about the x axis */
    pto3D ngiroxr (double theta);
    pto3D ngiroxg (double thetag);
    /** rotate theta degrees about the y axis */
    pto3D ngiroyr (double theta);
    pto3D ngiroyg (double thetag);
    /** rotate theta degrees about the z axis */
    pto3D ngirozr (double theta);
    pto3D ngirozg (double thetag);
    /** rotate theta degrees about the x axis y cierto punto*/
    void giroxr (double theta, pto3D paux);
    void giroxg (double thetag, pto3D pau);
    /** rotate theta degrees about the y axis */
    void giroyr (double theta, pto3D paux);
    void giroyg (double thetag, pto3D pau);
    /** rotate theta degrees about the z axis */
    void girozr (double theta, pto3D paux);
    void girozg (double thetag, pto3D pau);
///////////////////////////////////////////////////

    pto3D ngirar (double theta, pto3D eje);
    pto3D ngirag (double thetag, pto3D pau);

/////////////////////////////////////////////////
    pto3D mas (pto3D pto2);
    pto3D menos (pto3D pto2);
    double prodesc (pto3D pto2);
    pto3D prodvect (pto3D pto2);
    double dista (pto3D pto2);
    pto3D escala (double factor);
    double anguloconr (pto3D pto2);
    double angulocong (pto3D pto2);
    double modulo ();
    pto3D proyeccplano (pto3D pto2);
    //ACLARACION dihedro positivo es cuando, mirando en el sentido marcado
    double dihedror (pto3D ptoc, pto3D pto1);
    double dihedrog (pto3D ptoc, pto3D pto1);
    pto3D aversor (void);
    void versoriza (void);
    pto3D clona (void);
    pto3D ptomediocon (pto3D v1);
    pto3D ptopondcon (pto3D v1, double param);
    pto2D a2D (void);
    /* http://gethelp.devx.com/techtips/cpp_pro/10min/10min0400.asp */
    friend std::ostream& operator<< (std::ostream& s, const pto3D& a) {
	s << "<pto3D " << a.x << " " << a.y << " " << a.z << ">";
	return s;
    }
    int valid(void) {
	return x < 0.5e20 || y < 0.5e20 || z < 0.5e20;
    }
};

static pto3D INVALID_PTO3D = pto3D(1.0e20, 1.0e20, 1.0e20);

#endif
