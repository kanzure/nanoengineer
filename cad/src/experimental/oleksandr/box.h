// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: box.h
  Author: Oleksandr Shevchenko
  Description: class for box representation
*/

#if !defined(BOX_INCLUDED)
#define BOX_INCLUDED

#include "interval.h"
#include "triple.h"

class Box
{

  public:

	//------------------------------------------------------------------------
	// Constructor
	//
	//  empty Box
	//
	inline Box();

	//------------------------------------------------------------------------
	// Constructor
	//
	//  Box (interval, interval, interval) constructor
	//
	inline Box(
		const Interval & x,
		const Interval & y,
		const Interval & z);

	//------------------------------------------------------------------------
	// Center()
	//
	// calculate center
	//
	inline Triple Center() const;

	//------------------------------------------------------------------------
	// Contains()
	//
	// box contains point
	//
	inline int Contains(
		const Triple & p) const;

	//------------------------------------------------------------------------
	// Empty()
	//
	// clear rectangle
	//
	inline void Empty();

	//------------------------------------------------------------------------
	// Enclose()
	//
	// adjust rectangle
	//
	inline void Enclose(
		const Triple & p);

	//------------------------------------------------------------------------
	// Extent()
	//
	// calculate extent
	//
	inline Triple Extent() const;

	//------------------------------------------------------------------------
	// Max()
	//
	//  get max point
	//
	inline Triple Max() const;

	//------------------------------------------------------------------------
	// Min()
	//
	//  get min point
	//
	inline Triple Min() const;

  private:

	//------------------------------------------------------------------------
	// mX

	Interval mX;						// interval for X

	//------------------------------------------------------------------------
	// mY

	Interval mY;						// interval for Y

	//------------------------------------------------------------------------
	// mZ

	Interval mZ;						// interval for Z
};

//----------------------------------------------------------------------------
// Constructor

inline Box::Box()
{

}

//----------------------------------------------------------------------------
// Constructor

inline Box::Box(
	const Interval & x,
	const Interval & y,
	const Interval & z):

	mX(									// interval for X
		x),
	mY(									// interval for Y
		y),
	mZ(									// interval for Z
		z)
{

}

//----------------------------------------------------------------------------
// Center()

inline Triple Box::Center() const
{
	return Triple(mX.Center(),mY.Center(),mZ.Center());
}

//----------------------------------------------------------------------------
// Contains()

inline int Box::Contains(
	const Triple & p) const
{
	return (mX.Contains(p.X()) && mY.Contains(p.Y()) && mZ.Contains(p.Z()));
}

//----------------------------------------------------------------------------
// Empty()

inline void Box::Empty()
{
	mX.Empty();
	mY.Empty();
	mZ.Empty();
}

//----------------------------------------------------------------------------
// Enclose()

inline void Box::Enclose(
	const Triple & p)
{
	mX.Enclose(p.X());
	mY.Enclose(p.Y());
	mZ.Enclose(p.Z());
}

//----------------------------------------------------------------------------
// Extent()

inline Triple Box::Extent() const
{
	return Triple(mX.Extent(),mY.Extent(),mZ.Extent());
}

//----------------------------------------------------------------------------
// Max()

inline Triple Box::Max() const
{
	return Triple(mX.Max(),mY.Max(),mZ.Max());
}

//----------------------------------------------------------------------------
// Min()

inline Triple Box::Min() const
{
	return Triple(mX.Min(),mY.Min(),mZ.Min());
}
#endif  								// BOX_INCLUDED

