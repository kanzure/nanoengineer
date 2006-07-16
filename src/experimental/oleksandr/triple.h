/*
  Name: triple.h
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
  Author: Oleksandr Shevchenko
  Description: coordinate 3D point management class 
*/

#if !defined(TRIPLE_INCLUDED)
#define TRIPLE_INCLUDED

#include <math.h>

class Triple
{

  public:

	//------------------------------------------------------------------------
	// Constructor
	//
	//  empty Triple
	//
	inline Triple();

	//------------------------------------------------------------------------
	// Constructor
	//
	//  Triple (X,Y,Z) constructor
	//
	inline Triple(
		double ax,
		double ay,
		double az);

	//------------------------------------------------------------------------
	// Constructor
	//
	//  Triple (X,Y,Z) constructor
	//
	inline Triple(
		double coords[3]);

	//------------------------------------------------------------------------
	// Constructor
	//
	// vector a->b constructor
	//
	inline Triple(
		const Triple &a,
		const Triple &b);

	//------------------------------------------------------------------------
	// Closest()
	//
	// closest point on edge
	//
	double Closest(
		const Triple & vertex0,
		const Triple & vertex1,
		Triple & p) const;

	//------------------------------------------------------------------------
	// Get()

	inline double Get(
		int i) const;

	//------------------------------------------------------------------------
	// Greatest()
	//
	// calculate greatest value
	//
	int Greatest(
		double & value) const;

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
	Triple & Normalize();

	//------------------------------------------------------------------------
	// Normalize()
	//
	//  normalizes vector to unit length
	//
	Triple & Normalize(
		double &length);

	//------------------------------------------------------------------------
	// operator -()
	//
	//  overloaded negation operator
	//
	inline Triple operator -() const;

	//------------------------------------------------------------------------
	// operator *=()
	//
	//  overloaded operator *= (Triple)
	//
	inline Triple & operator *=(
		const Triple &b);

	//------------------------------------------------------------------------
	// operator *=()
	//
	//  overloaded operator *= gives multiplication to of Triple to number
	//
	inline Triple & operator *=(
		double s);

	//------------------------------------------------------------------------
	// operator /=()
	//
	//  overloaded /=(double) operator
	//
	inline Triple & operator /=(
		double s);

	//------------------------------------------------------------------------
	// operator +=()
	//
	//  overloaded += operator
	//
	inline Triple & operator +=(
		const Triple &a);

	//------------------------------------------------------------------------
	// operator -=()
	//
	//  overloaded -= operator
	//
	inline Triple & operator -=(
		const Triple &a);

	//------------------------------------------------------------------------
	// Orthogonal()
	//
	// get orthogonal axes
	//
	void Orthogonal(
		Triple & ox,
		Triple & oy) const;

	//------------------------------------------------------------------------
	// X()
	//
	//  get X coordinate
	//
	inline double X() const;

	//------------------------------------------------------------------------
	// X()
	//
	//  set X coordinate
	//
	inline double & X();

	//------------------------------------------------------------------------
	// Y()
	//
	//  get Y coordinate
	//
	inline double Y() const;

	//------------------------------------------------------------------------
	// Y()
	//
	//  set Y coordinate
	//
	inline double & Y();

	//------------------------------------------------------------------------
	// Z()
	//
	//  get Z coordinate
	//
	inline double Z() const;

	//------------------------------------------------------------------------
	// Z()
	//
	//  set Z coordinate
	//
	inline double & Z();

  private:

	//------------------------------------------------------------------------
	// mX

	double mX;							// coordinate X

	//------------------------------------------------------------------------
	// mY

	double mY;							// coordinate Y

	//------------------------------------------------------------------------
	// mZ

	double mZ;							// coordinate Z
};

//----------------------------------------------------------------------------
// operator -()
//
//  overloaded binary minus
//
inline Triple operator -(
	const Triple &a,
	const Triple &b);

//----------------------------------------------------------------------------
// operator %()
//
//  dot product of two vectors C = (A*B)
//
inline double operator %(
	const Triple &a,
	const Triple &b);

//----------------------------------------------------------------------------
// operator *()
//
//  cross product of two vectors C = AxB
//
inline Triple operator *(
	const Triple &a,
	const Triple &b);

//----------------------------------------------------------------------------
// operator *()
//
//  vector*number product
//
inline Triple operator *(
	const Triple &a,
	double s);

//----------------------------------------------------------------------------
// operator *()
//
//  number*vector product
//
inline Triple operator *(
	double s,
	const Triple &b);

//----------------------------------------------------------------------------
// operator /()
//
//  overloaded operator / (double)
//
inline Triple operator /(
	const Triple &a,
	double s);

//----------------------------------------------------------------------------
// operator +()
//
//  overloaded binary plus
//
inline Triple operator +(
	const Triple &a,
	const Triple &b);

//----------------------------------------------------------------------------
// operator -()

inline Triple operator -(
	const Triple &a,
	const Triple &b)
{
	return Triple(a.X()-b.X(),a.Y()-b.Y(),a.Z()-b.Z());
}

//----------------------------------------------------------------------------
// operator %()

inline double operator %(
	const Triple &a,
	const Triple &b)
{
	return (a.X()*b.X() + a.Y()*b.Y() + a.Z()*b.Z());
}

//----------------------------------------------------------------------------
// operator *()

inline Triple operator *(
	const Triple &a,
	const Triple &b)
{
	return (Triple(
		a.Y()*b.Z() - a.Z()*b.Y(),
		a.Z()*b.X() - a.X()*b.Z(),
		a.X()*b.Y() - a.Y()*b.X())
		);
}

//----------------------------------------------------------------------------
// operator *()

inline Triple operator *(
	const Triple &a,
	double s)
{
	return (Triple(a.X()*s,a.Y()*s,a.Z()*s));
}

//----------------------------------------------------------------------------
// operator *()

inline Triple operator *(
	double s,
	const Triple &b)
{
	return (Triple(s*b.X(),s*b.Y(),s*b.Z()));
}

//----------------------------------------------------------------------------
// operator /()

inline Triple operator /(
	const Triple &a,
	double s)
{
	return (Triple(a.X()/s,a.Y()/s,a.Z()/s));
}

//----------------------------------------------------------------------------
// operator +()

inline Triple operator +(
	const Triple &a,
	const Triple &b)
{
	return (Triple(a.X()+b.X(),a.Y()+b.Y(),a.Z()+b.Z()));
}

//----------------------------------------------------------------------------
// Constructor

inline Triple::Triple():

	// Private data initialization
	mX(									// coordinate X
		0.0),
	mY(									// coordinate Y
		0.0),
	mZ(									// coordinate Z
		0.0)
{

}

//----------------------------------------------------------------------------
// Constructor

inline Triple::Triple(
	double ax,
	double ay,
	double az):

	// Private data initialization
	mX(									// coordinate X
		ax),
	mY(									// coordinate Y
		ay),
	mZ(									// coordinate Z
		az)
{

}

//----------------------------------------------------------------------------
// Constructor

inline Triple::Triple(
	double coords[3])
{
	X() = coords[0];
	Y() = coords[1];
	Z() = coords[2];
}

//----------------------------------------------------------------------------
// Constructor

inline Triple::Triple(
	const Triple &a,
	const Triple &b)
{
	X() = b.X() - a.X();
	Y() = b.Y() - a.Y();
	Z() = b.Z() - a.Z();
}

//----------------------------------------------------------------------------
// Get()

inline double Triple::Get(
	int i) const
{
	switch (i)
	{
	case 0:
		return mX;
	case 1:
		return mY;
	case 2:
		return mZ;
	}
	return mY;
}

//----------------------------------------------------------------------------
// operator -()

inline Triple Triple::operator -() const
{
	return Triple(-X(),-Y(),-Z());
}

//----------------------------------------------------------------------------
// operator *=()

inline Triple & Triple::operator *=(
	const Triple &b)
{
	double xxx = Y()*b.Z() - Z()*b.Y();
	double yyy = Z()*b.X() - X()*b.Z();
	double zzz = X()*b.Y() - Y()*b.X();
	X() = xxx;
	Y() = yyy;
	Z() = zzz;
	return (*this);
}

//----------------------------------------------------------------------------
// operator *=()

inline Triple & Triple::operator *=(
	double s)
{
	X() *= s;
	Y() *= s;
	Z() *= s;
	return *this;
}

//----------------------------------------------------------------------------
// operator /=()

inline Triple & Triple::operator /=(
	double s)
{
	X() /= s;
	Y() /= s;
	Z() /= s;
	return *this;
}

//----------------------------------------------------------------------------
// operator +=()

inline Triple & Triple::operator +=(
	const Triple &a)
{
	X() += a.X();
	Y() += a.Y();
	Z() += a.Z();
	return *this;
}

//----------------------------------------------------------------------------
// operator -=()

inline Triple & Triple::operator -=(
	const Triple &a)
{
	X() -= a.X();
	Y() -= a.Y();
	Z() -= a.Z();
	return *this;
}

//----------------------------------------------------------------------------
// X()

inline double Triple::X() const
{
	return mX;
}

//----------------------------------------------------------------------------
// X()

inline double & Triple::X()
{
	return mX;
}

//----------------------------------------------------------------------------
// Y()

inline double Triple::Y() const
{
	return mY;
}

//----------------------------------------------------------------------------
// Y()

inline double & Triple::Y()
{
	return mY;
}

//----------------------------------------------------------------------------
// Z()

inline double Triple::Z() const
{
	return mZ;
}

//----------------------------------------------------------------------------
// Z()

inline double & Triple::Z()
{
	return mZ;
}
#endif  								// TRIPLE_INCLUDED

