// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: couple.cpp
  Author: Oleksandr Shevchenko
  Description: coordinate 2D point management class  
*/

#include "couple.h"

//----------------------------------------------------------------------------
// Constructor
//
//  couple from point constructor
//
Couple::Couple(
	int i,
	double x,
	double y,
	double z)
{
	switch (i)
	{
	case 0:
		mX = y;
		mY = z;
		break;
	case 1:
		mX = x;
		mY = z;
		break;
	case 2:
		mX = x;
		mY = y;
		break;
	}
}

//----------------------------------------------------------------------------
// Len()
//
//  vector length
//
double Couple::Len() const
{
	return sqrt(X()*X() + Y()*Y());
}

//----------------------------------------------------------------------------
// Len2()
//
//  square of vector length
//
double Couple::Len2() const
{
	return (X()*X() + Y()*Y());
}

//----------------------------------------------------------------------------
// Normalize()
//
//  normalize vector to unit length
//
Couple & Couple::Normalize()
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
Couple & Couple::Normalize(
	double &length)
{
	length = Len();
	*this /= length;
	return *this;
}
