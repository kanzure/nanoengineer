/*
  Name: triple.h
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
  Author: Oleksandr Shevchenko
  Description: coordinate 3D point management class 
*/

#include "triple.h"

//----------------------------------------------------------------------------
// Closest()
//
// closest point on edge
//
double Triple::Closest(
	const Triple & vertex0,
	const Triple & vertex1,
	Triple & p) const
{
	Triple edge(vertex0,vertex1);
	double t = ((*this-vertex0)%edge)/edge.Len2();
	if (t < 0.0)
	{
		p = vertex0;
		t = 0.0;
	}
	else if (t > 1.0)
	{
		p = vertex1;
		t = 1.0;
	}
	else
	{
		p = vertex0 + t*edge;
	}
	return t;
}

//----------------------------------------------------------------------------
// Greatest()
//
// calculate greatest value
//
int Triple::Greatest(
	double & value) const
{
	if (X() > Y())
	{
		if(X() > Z())
		{
	//    x is greatest
			value = X();
			return (0);
		}
		else
		{
	//    z is greatest
			value = Z();
			return (2);
		}
	}
	else
	{
		if(Y() > Z())
		{
	//    y is greatest
			value = Y();
			return (1);
		}
		else
		{
	//    z is greatest
			value = Z();
			return (2);
		}
	}
	return (2);
}

//----------------------------------------------------------------------------
// Len()
//
//  vector length
//
double Triple::Len() const
{
	return sqrt(X()*X() + Y()*Y() + Z()*Z());
}

//----------------------------------------------------------------------------
// Len2()
//
//  square of vector length
//
double Triple::Len2() const
{
	return (X()*X() + Y()*Y() + Z()*Z());
}

//----------------------------------------------------------------------------
// Normalize()
//
//  normalize vector to unit length
//
Triple & Triple::Normalize()
{
	double length= Len();
	*this /= length;
	return *this;
}

//----------------------------------------------------------------------------
// Normalize()
//
//  normalizes vector to unit length
//
Triple & Triple::Normalize(
	double &length)
{
	length = Len();
	*this /= length;
	return *this;
}

//----------------------------------------------------------------------------
// Orthogonal()
//
// get orthogonal axes
//
void Triple::Orthogonal(
	Triple & ox,
	Triple & oy) const
{
	double ix = 0.0, iy = 0.0;
	
	if( fabs(X())>fabs(Z()) && fabs(X()) > fabs(Y()) )
		iy = 1.0;
	else
		ix = 1.0;
	
	oy = Triple(iy*Z(), -ix*Z(), ix*Y()-iy*X());
	oy.Normalize();
	
	ox = oy * (*this);
	ox.Normalize();
}
