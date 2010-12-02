// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/* $Id$ */

#ifndef PTO2D_H_INCLUDED
#define PTO2D_H_INCLUDED
#include "pto3D.h"

class pto2D: public pto3D
{
 public:
    pto2D ();
    pto2D (float xt, float yt);
    pto2D (double xt, double yt);
    pto2D (pto3D other);
    int dentro3 (pto2D A, pto2D B, pto2D C);
    int dentro3l (pto2D A, pto2D B, pto2D C);
    int dentrocasi3 (pto2D A, pto2D B, pto2D v1, pto2D v2);
    int dentro4cv (pto2D A, pto2D B, pto2D C, pto2D D, double p);
    int dentro4 (pto2D A, pto2D B, pto2D C, pto2D D, double p);
    int dentro4 (pto2D A, pto2D B, pto2D C, pto2D D);
    double anguloccwhasta (pto2D phasta);	//EN RADIANES
    double angulocwhasta (pto2D phasta);	//EN RADIANES
    int dentro4e (pto2D A, pto2D B, pto2D C, pto2D D);
    int dentro4l (pto2D A, pto2D B, pto2D C, pto2D D);
    pto2D mas (pto2D p);
    pto2D menos (pto2D p);
};

#endif
