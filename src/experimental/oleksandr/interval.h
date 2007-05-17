// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: interval.h
  Author: Oleksandr Shevchenko
  Description: class for interval representation
*/

#if !defined(INTERVAL_INCLUDED)
#define INTERVAL_INCLUDED

#include <float.h>

class Interval
{

  public:

	//------------------------------------------------------------------------
	// Constructor
	//
	//  empty Interval
	//
	inline Interval();

	//------------------------------------------------------------------------
	// Constructor
	//
	//  Interval(begin,end) constructor
	//
	inline Interval(
		double interval[2]);

	//------------------------------------------------------------------------
	// Constructor
	//
	//  Interval (begin,end) constructor
	//
	inline Interval(
		double begin,
		double end);

	//------------------------------------------------------------------------
	// Center()
	//
	// calculate center
	//
	inline double Center() const;

	//------------------------------------------------------------------------
	// Contains()
	//
	// interval contains point
	//
	inline int Contains(
		double point) const;

	//------------------------------------------------------------------------
	// Empty()
	//
	// clear interval
	//
	inline void Empty();

	//------------------------------------------------------------------------
	// Enclose()
	//
	// adjust interval
	//
	inline void Enclose(
		double point);

	//------------------------------------------------------------------------
	// Extent()
	//
	// calculate extent
	//
	inline double Extent() const;

	//------------------------------------------------------------------------
	// Max()
	//
	//  get end of interval
	//
	inline double Max() const;

	//------------------------------------------------------------------------
	// Max()
	//
	//  set end of interval
	//
	inline double & Max();

	//------------------------------------------------------------------------
	// Min()
	//
	//  get begin of interval
	//
	inline double Min() const;

	//------------------------------------------------------------------------
	// Min()
	//
	//  set begin of interval
	//
	inline double & Min();

	//------------------------------------------------------------------------
	// Point()
	//
	// calculate point
	//
	inline double Point(
		double r) const;

  private:

	//------------------------------------------------------------------------
	// mMin

	double mMin;						// begin of interval

	//------------------------------------------------------------------------
	// mMax

	double mMax;						// end of interval
};

//----------------------------------------------------------------------------
// Constructor

inline Interval::Interval():

	mMin(								// begin of interval
		DBL_MAX),
	mMax(								// end of interval
		-DBL_MAX)
{

}

//----------------------------------------------------------------------------
// Constructor

inline Interval::Interval(
	double interval[2])
{
	mMin = interval[0];
	mMax = interval[1];
}

//----------------------------------------------------------------------------
// Constructor

inline Interval::Interval(
	double begin,
	double end):

	mMin(								// begin of interval
		begin),
	mMax(								// end of interval
		end)
{

}

//----------------------------------------------------------------------------
// Center()

inline double Interval::Center() const
{
	return (mMin + mMax)/2;
}

//----------------------------------------------------------------------------
// Contains()

inline int Interval::Contains(
	double point) const
{
	return (point >= mMin && point <= mMax);
}

//----------------------------------------------------------------------------
// Empty()

inline void Interval::Empty()
{
	mMin = DBL_MAX;
	mMax = -DBL_MAX;
}

//----------------------------------------------------------------------------
// Enclose()

inline void Interval::Enclose(
	double point)
{
	if (point < mMin) mMin = point;
	if (point > mMax) mMax = point;
}

//----------------------------------------------------------------------------
// Extent()

inline double Interval::Extent() const
{
	return (mMax - mMin)/2;
}

//----------------------------------------------------------------------------
// Max()

inline double Interval::Max() const
{
	return mMax;
}

//----------------------------------------------------------------------------
// Max()

inline double & Interval::Max()
{
	return mMax;
}

//----------------------------------------------------------------------------
// Min()

inline double Interval::Min() const
{
	return mMin;
}

//----------------------------------------------------------------------------
// Min()

inline double & Interval::Min()
{
	return mMin;
}

//----------------------------------------------------------------------------
// Point()

inline double Interval::Point(
	double r) const
{
	return (1-r)*mMin + r*mMax;
}
#endif  								// INTERVAL_INCLUDED

