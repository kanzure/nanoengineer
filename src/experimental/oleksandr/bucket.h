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
	Bucket(int l, int m, int n);
	
	//------------------------------------------------------------------------
	// Add
	//
	//  add points to bucket
	//
	void Add(const Container<Triple> & points);
	
	//------------------------------------------------------------------------
	// Duplicate
	//
	//  find duplicate points
	//
	void Duplicate(const Container<Triple> & points, int * ia);
	
	//------------------------------------------------------------------------
	// Predicate
	//
	//  calculate predicate for all spheres
	//
	double Predicate(const Container<Triple> & centers, const Container<double> & radiuses, const Triple & p);
	
  private:
          
	//------------------------------------------------------------------------
	// Index()
	//
	// calculate index
	//
	inline void Index(const Triple & p);

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

	//------------------------------------------------------------------------
	// mI

	int mI;							// index i

	//------------------------------------------------------------------------
	// mJ

	int mJ;							// index j

	//------------------------------------------------------------------------
	// mK

	int mK;							// index k

	//------------------------------------------------------------------------
	// mL

	int mL;							// size x

	//------------------------------------------------------------------------
	// mM

	int mM;							// size y

	//------------------------------------------------------------------------
	// mN

	int mN;							// size z

	//------------------------------------------------------------------------
	// mA

    Container<int> *** mA;			// array for bucket                                          
             
	//------------------------------------------------------------------------
	// mB

    Container<int> ** mB;			// array for bucket                                          
             
	//------------------------------------------------------------------------
	// mC

    Container<int> * mC;			// array for bucket                                          
             
};

//----------------------------------------------------------------------------
// Index()

inline void Bucket::Index(const Triple & p)
{
	//  calculate index for point p
	mI = int(mL * (p.X() + 1) / 2);
	if ( mI < 0) mI = 0;
	if ( mI >= mL) mI = mL - 1;

	mJ = int(mM * (p.Y() + 1) / 2);
	if ( mJ < 0) mJ = 0;
	if ( mJ >= mM) mJ = mM - 1;

	mK = int(mN * (p.Z() + 1) / 2);
	if ( mK < 0) mK = 0;
	if ( mK >= mN) mK = mN - 1;
}

//----------------------------------------------------------------------------
// Size()

inline int Bucket::Size() const
{
	return mA[mI][mJ][mK].Size();
}

//----------------------------------------------------------------------------
// Value()

inline int Bucket::Value(int i) const
{
	return mA[mI][mJ][mK][i];
}

#endif  								// BUCKET_INCLUDED
