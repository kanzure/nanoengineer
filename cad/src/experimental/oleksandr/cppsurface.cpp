// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: cppsurface.cpp
  Author: Oleksandr Shevchenko
  Description: CPP functions to call from C 
*/

#include "cppsurface.h"
#include "surface.h"
#include "hierarchy.h"
#include "collisiondetector.h"

Surface * s;
Surface * s0;
Surface * s1;
Hierarchy * h0;
Hierarchy * h1;

void cppAdd(double x, double y, double z, double r, int p)
{
	s->Add(x,y,z,r,p);
}
void cppCreateSurface()
{
	s->CreateSurface();
}
void cppCollisionDetection(double delta)  
{
	s0 = new Surface();
	s1 = new Surface();
	h0 = new Hierarchy();
	h1 = new Hierarchy();

	s0->Add(0,0,0,1,0);
	s0->CreateSurface();
	s1->Add(0,0,0,1,0);
	s1->CreateSurface();

	Triple t0(-delta,0,0);
	Triple t1(delta,0,0);
	RotationMatrix m0,m1;
	h0->Initialize(s0);
	h0->Behavior(&m0,&t0);
	h1->Initialize(s1);
	h1->Behavior(&m1,&t1);

	CollisionDetector cd;
	cd.CheckCollision(h0,h1);
	cd.Select(1);

	s->CreateSurface(s0,s1,delta); 

	delete h0;
	delete h1;

	delete s0;
	delete s1;
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
int cppC(int i)
{
    return s->C(i); 
}
int cppI(int i)
{
    return s->I(i);
}
void cppLevel(int i)
{
	s->Level(i);
}
int cppType()
{
	return s->Type();
}
void cppMethod(int i)
{
	s->Method(i);
}

