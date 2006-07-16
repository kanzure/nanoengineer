/*
  Name: bucket.h
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
  Author: Oleksandr Shevchenko
  Description: class for bucket representation
*/

#if !defined(BUCKET_INCLUDED)
#define BUCKET_INCLUDED

#include "container.h"
#include "triple.h"

class Bucket
{

  public:

	//------------------------------------------------------------------------
	// Constructor
	//
	//  empty bucket
	//
	Bucket(int n);
	
	//------------------------------------------------------------------------
	// Add
	//
	//  add point to bucket
	//
	void Add(int i, const Triple & p);
	
	//------------------------------------------------------------------------
	// Index()
	//
	// calculate index
	//
	inline int Index(const Triple & p);

	//------------------------------------------------------------------------
	// Size()
	//
	// calculate array size
	//
	inline int Size() const;

	//------------------------------------------------------------------------
	// Value()
	//
	// calculate array value
	//
	inline int Value(int i) const;

  private:
          
	//------------------------------------------------------------------------
	// mI

	int mI;							// index

	//------------------------------------------------------------------------
	// mN

	int mN;							// size

	//------------------------------------------------------------------------
	// mNN

	int mNN;						// size square

	//------------------------------------------------------------------------
	// mNNN

	int mNNN;						// size cube

	//------------------------------------------------------------------------
	// mA

    Container<int> * mA;			// array for bucket                                          
             
};

//----------------------------------------------------------------------------
// Index()

inline int Bucket::Index(const Triple & p)
{
	//  calculate index for point p
	int i = int(mN * (p.X() + 1) / 2);
	if ( i >= mN) i = mN - 1;
	int j = int(mN * (p.Y() + 1) / 2);
	if ( j >= mN) j = mN - 1;
	int k = int(mN * (p.Z() + 1) / 2);
	if ( k >= mN) k = mN - 1;
	mI = i * mNN + j * mN + k;
	return mI;
}

//----------------------------------------------------------------------------
// Size()

inline int Bucket::Size() const
{
	return mA[mI].Size();
}

//----------------------------------------------------------------------------
// Value()

inline int Bucket::Value(int i) const
{
	return mA[mI][i];
}

#endif  								// BUCKET_INCLUDED
