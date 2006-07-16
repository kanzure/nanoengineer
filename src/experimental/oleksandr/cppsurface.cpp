/*
  Name: cppsurface.cpp
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
  Author: Oleksandr Shevchenko
  Description: CPP functions to call from C 
*/

#include "cppsurface.h"
#include "surface.h"

Surface * s;

void cppAdd(double x, double y, double z, double r)
{
	s->Add(x,y,z,r);
}
void cppCreateSurface()
{
	s->CreateSurface();
}
void cppAllocate()
{
	s = new Surface();
}
void cppFree()
{
	delete s;
}
int cppNp()
{
    return s->Np();
}
int cppNt()
{
    return s->Nt();
}
double cppPx(int i)
{
    return s->Px(i);
}
double cppPy(int i)
{
    return s->Py(i);
}
double cppPz(int i)
{
    return s->Pz(i);
}
double cppNx(int i)
{
    return s->Nx(i);
}
double cppNy(int i)
{
    return s->Ny(i);
}
double cppNz(int i)
{
    return s->Nz(i);
}
int cppI(int i)
{
    return s->I(i);
}
void cppLevel(int i)
{
	s->Level(i);
}

