// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: csurface.h
  Author: Oleksandr Shevchenko
  Description: C helper for psurface.pyx 
*/

#if !defined(CSURFACE_INCLUDED)
#define CSURFACE_INCLUDED

#include "cppsurface.h"

void cAdd(double x, double y, double z, double r, int p)
{
	cppAdd(x,y,z,r,p);
}
void cCreateSurface()
{
	cppCreateSurface();
}
void cCollisionDetection(double delta)  
{
	cppCollisionDetection(delta);  
}
void cAllocate()
{
	cppAllocate();
}
void cFree()
{
	cppFree();
}
int cNp()
{
	return cppNp();
}
int cNt()
{
	return cppNt();
}
double cPx(int i)
{
	return cppPx(i);
}
double cPy(int i)
{
	return cppPy(i);
}
double cPz(int i)
{
	return cppPz(i);
}
double cNx(int i)
{
	return cppNx(i);
}
double cNy(int i)
{
	return cppNy(i);
}
double cNz(int i)
{
	return cppNz(i);
}
int cC(int i) 
{
	return cppC(i);
}
int cI(int i)
{
	return cppI(i);
}
void cLevel(int i)
{
	cppLevel(i);
}
int cType()
{
	return cppType();
}
void cMethod(int i)
{
	cppMethod(i);
}

#endif  								// CSURFACE_INCLUDED
