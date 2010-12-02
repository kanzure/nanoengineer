// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>


// Position of the eye in spherical coordinates
#define EYE_THETA  0.0
#define EYE_PHI  0.0
#define EYE_R  100.0

// Position of the eye in cartesian coordinates
#define EYE_X  (EYE_R * cos(EYE_THETA) * cos(EYE_PHI))
#define EYE_Y  (EYE_R * sin(EYE_THETA) * cos(EYE_PHI))
#define EYE_Z  (EYE_R * sin(EYE_PHI))


void
glSetup(int windowWidth, int windowHeight)
{

    //exit(1);

}


void
line(float x1, float y1, float z1,
     float x2, float y2, float z2,
     float r, float g, float b)
{

}


void
sphere(double x, double y, double z, double radius, double r, double g, double b)
{
}

