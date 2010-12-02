// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: couple.h
  Author: Oleksandr Shevchenko
  Description: coordinate 2D point management class  
*/

#if !defined(COUPLE_INCLUDED)
#define COUPLE_INCLUDED

#include <math.h>
#include "triple.h"

class Couple
{

  public:

	//------------------------------------------------------------------------
	// Constructor
	//
	//  empty Couple
	//
	inline Couple();

	//------------------------------------------------------------------------
	// Constructor
	//
	//  Couple (x,y) constructor
	//
	inline Couple(
		double ax,
		double ay);

	//------------------------------------------------------------------------
	// Constructor
	//
	//  Couple (x,y) constructor
	//
	inline Couple(
		double coords[2]);

	//------------------------------------------------------------------------
	// Constructor
	//
	// vector a->b constructor
	//
	inline Couple(
		const Couple &a,
		const Couple &b);

	//------------------------------------------------------------------------
	// Constructor
	//
	//  Couple from point constructor
	//
	Couple(
		int i,
		double x,
		double y,
		double z);

	//------------------------------------------------------------------------
	// Len()
	//
	//  vector length
	//
	double Len() const;

	//------------------------------------------------------------------------
	// Len2()
	//
	//  square of vector length
	//
	double Len2() const;

	//------------------------------------------------------------------------
	// Normalize()
	//
	//  normalize vector to unit length
	//
	Couple & Normalize();

	//------------------------------------------------------------------------
	// Normalize()
	//
	//  normalizes vector to unit length
	//
	Couple & Normalize(
		double &length);

	//------------------------------------------------------------------------
	// operator -()
	//
	//  overloaded negation operator
	//
	inline Couple operator -() const;

	//------------------------------------------------------------------------
	// operator *=()
	//
	//  overloaded operator *= gives multiplication to of Couple to number
	//
	inline Couple & operator *=(
		double s);

	//------------------------------------------------------------------------
	// operator /=()
	//
	//  overloaded /=(double) operator
	//
	inline Couple & operator /=(
		double s);

	//------------------------------------------------------------------------
	// operator +=()
	//
	//  overloaded += operator
	//
	inline Couple & operator +=(
		const Couple &a);

	//------------------------------------------------------------------------
	// operator -=()
	//
	//  overloaded -= operator
	//
	inline Couple & operator -=(
		const Couple &a);

	//------------------------------------------------------------------------
	// U()
	//
	//  get x coordinate
	//
	inline double U() const;

	//------------------------------------------------------------------------
	// U()
	//
	//  set x coordinate
	//
	inline double & U();

	//------------------------------------------------------------------------
	// V()
	//
	//  get y coordinate
	//
	inline double V() const;

	//------------------------------------------------------------------------
	// V()
	//
	//  set y coordinate
	//
	inline double & V();

	//------------------------------------------------------------------------
	// X()
	//
	//  get x coordinate
	//
	inline double X() const;

	//------------------------------------------------------------------------
	// X()
	//
	//  set x coordinate
	//
	inline double & X();

	//------------------------------------------------------------------------
	// Y()
	//
	//  get y coordinate
	//
	inline double Y() const;

	//------------------------------------------------------------------------
	// Y()
	//
	//  set y coordinate
	//
	inline double & Y();

  private:

	//------------------------------------------------------------------------
	// mX

	double mX;							// coordinate x

	//------------------------------------------------------------------------
	// mY

	double mY;							// coordinate y
};

//----------------------------------------------------------------------------
// operator -()
//
//  overloaded binary minus
//
inline Couple operator -(
	const Couple &a,
	const Couple &b);

//----------------------------------------------------------------------------
// operator %()
//
//  dot product of two vectors C = (A*B)
//
inline double operator %(
	const Couple &a,
	const Couple &b);

//----------------------------------------------------------------------------
// operator *()
//
//  vector*number product
//
inline Couple operator *(
	const Couple &a,
	double s);

//----------------------------------------------------------------------------
// operator *()
//
//  number*vector product
//
inline Couple operator *(
	double s,
	const Couple &b);

//----------------------------------------------------------------------------
// operator /()
//
//  overloaded operator / (double)
//
inline Couple operator /(
	const Couple &a,
	double s);

//----------------------------------------------------------------------------
// operator +()
//
//  overloaded binary plus
//
inline Couple operator +(
	const Couple &a,
	const Couple &b);

//----------------------------------------------------------------------------
// operator -()

inline Couple operator -(
	const Couple &a,
	const Couple &b)
{
	return Couple(a.X()-b.X(),a.Y()-b.Y());
}

//----------------------------------------------------------------------------
// operator %()

inline double operator %(
	const Couple &a,
	const Couple &b)
{
	return (a.X()*b.X() + a.Y()*b.Y());
}

//----------------------------------------------------------------------------
// operator *()

inline Couple operator *(
	const Couple &a,
	double s)
{
	return (Couple(a.X()*s,a.Y()*s));
}

//----------------------------------------------------------------------------
// operator *()

inline Couple operator *(
	double s,
	const Couple &b)
{
	return (Couple(s*b.X(),s*b.Y()));
}

//----------------------------------------------------------------------------
// operator /()

inline Couple operator /(
	const Couple &a,
	double s)
{
	return (Couple(a.X()/s,a.Y()/s));
}

//----------------------------------------------------------------------------
// operator +()

inline Couple operator +(
	const Couple &a,
	const Couple &b)
{
	return (Couple(a.X()+b.X(),a.Y()+b.Y()));
}

//----------------------------------------------------------------------------
// Constructor

inline Couple::Couple():

	// Private data initialization
	mX(									// coordinate x
		0.0),
	mY(									// coordinate y
		0.0)
{

}

//----------------------------------------------------------------------------
// Constructor

inline Couple::Couple(
	double ax,
	double ay):

	// Private data initialization
	mX(									// coordinate x
		ax),
	mY(									// coordinate y
		ay)
{

}

//----------------------------------------------------------------------------
// Constructor

inline Couple::Couple(
	double coords[2])
{
	X() = coords[0];
	Y() = coords[1];
}

//----------------------------------------------------------------------------
// Constructor

inline Couple::Couple(
	const Couple &a,
	const Couple &b)
{
	X() = b.X() - a.X();
	Y() = b.Y() - a.Y();
}

//----------------------------------------------------------------------------
// operator -()

inline Couple Couple::operator -() const
{
	return Couple(-X(),-Y());
}

//----------------------------------------------------------------------------
// operator *=()

inline Couple & Couple::operator *=(
	double s)
{
	X() *= s;
	Y() *= s;
	return *this;
}

//----------------------------------------------------------------------------
// operator /=()

inline Couple & Couple::operator /=(
	double s)
{
	X() /= s;
	Y() /= s;
	return *this;
}

//----------------------------------------------------------------------------
// operator +=()

inline Couple & Couple::operator +=(
	const Couple &a)
{
	X() += a.X();
	Y() += a.Y();
	return *this;
}

//----------------------------------------------------------------------------
// operator -=()

inline Couple & Couple::operator -=(
	const Couple &a)
{
	X() -= a.X();
	Y() -= a.Y();
	return *this;
}

//----------------------------------------------------------------------------
// U()

inline double Couple::U() const
{
	return mX;
}

//----------------------------------------------------------------------------
// U()

inline double & Couple::U()
{
	return mX;
}

//----------------------------------------------------------------------------
// V()

inline double Couple::V() const
{
	return mY;
}

//----------------------------------------------------------------------------
// V()

inline double & Couple::V()
{
	return mY;
}

//----------------------------------------------------------------------------
// X()

inline double Couple::X() const
{
	return mX;
}

//----------------------------------------------------------------------------
// X()

inline double & Couple::X()
{
	return mX;
}

//----------------------------------------------------------------------------
// Y()

inline double Couple::Y() const
{
	return mY;
}

//----------------------------------------------------------------------------
// Y()

inline double & Couple::Y()
{
	return mY;
}
#endif  								// COUPLE_INCLUDED

