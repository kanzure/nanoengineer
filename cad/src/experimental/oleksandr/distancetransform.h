// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: distancetrasform.h
  Author: Oleksandr Shevchenko
  Description: class for distancetrasform representation
*/

#if !defined(DISTANCETRANSFORM_INCLUDED)
#define DISTANCETRANSFORM_INCLUDED

#include "container.h"
#include "triple.h"

class DistanceTransform
{

  public:

	//------------------------------------------------------------------------
	// Constructor
	//
	//  distancetrasform
	//
	DistanceTransform(const Container<Triple> & centers, const Container<double> & radiuses, const Container<int> & properties);
	
	//------------------------------------------------------------------------
	// Omega()
	//
	// calculate omega function
	//
	inline double Omega(const Triple & p);

	//------------------------------------------------------------------------
	// Property()
	//
	// calculate property
	//
	inline int Property(const Triple & p);

	//------------------------------------------------------------------------
	// Omega()
	//
	// calculate omega function
	//
	inline double Omega(int i, int j, int k);

	//------------------------------------------------------------------------
	// Omega()
	//
	//  calculate predicate for all spheres
	//
	void Omega(const Container<Triple> & centers, const Container<double> & radiuses);
	
	//------------------------------------------------------------------------
	// L()
	//
	// returns size x 
	//
	inline int L();

	//------------------------------------------------------------------------
	// M()
	//
	// returns size y
	//
	inline int M();

	//------------------------------------------------------------------------
	// N()
	//
	// returns size z
	//
	inline int N();

  private:
          
	//------------------------------------------------------------------------
	// Index()
	//
	// calculate index
	//
	inline void Index(const Triple & p);

	//------------------------------------------------------------------------
	// Distance()
	//
	//  calculate distance transform
	//
	void Distance(const Container<Triple> & centers, const Container<double> & radiuses, const Container<int> & properties);
	
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
	// mU

	double mU;						// parameter u

	//------------------------------------------------------------------------
	// mV

	double mV;						// parameter v

	//------------------------------------------------------------------------
	// mW

	double mW;						// parameter w

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

    double *** mA;					// array for omega                                          
             
	//------------------------------------------------------------------------
	// mB

    double ** mB;					// array for omega                                          
             
	//------------------------------------------------------------------------
	// mC

    double * mC;					// array for omega                                          
             
	//------------------------------------------------------------------------
	// mAc

    int *** mAc;					// array for color                                          
             
	//------------------------------------------------------------------------
	// mBc

    int ** mBc;						// array for color                                          
             
	//------------------------------------------------------------------------
	// mCc

    int * mCc;						// array for color                                          
             
	//------------------------------------------------------------------------
	// mR

	double mR;						// minimal radius

};

//----------------------------------------------------------------------------
// Index()
//
// calculate index
//

inline void DistanceTransform::Index(const Triple & p)
{
	//  calculate index for point p
    mU = (mL * (p.X() + 1) / 2);
    mI = (int)mU;
    mU -= mI;
	if ( mI < 0) mI = 0;
	if ( mI >= mL) 
	{
		mI = mL - 1;
		mU = 1;
	}

    mV = (mM * (p.Y() + 1) / 2);
    mJ = (int)mV;
    mV -= mJ;
	if ( mJ < 0) mJ = 0;
	if ( mJ >= mM) 
	{
		mJ = mM - 1;
		mV = 1;
	}

    mW = (mN * (p.Z() + 1) / 2);
    mK = (int)mW;
    mW -= mK;
	if ( mK < 0) mK = 0;
	if ( mK >= mN) 
	{
		mK = mN - 1;
		mW = 1;
	}
}

//------------------------------------------------------------------------
// Omega()
//
// calculate omega function
//
double DistanceTransform::Omega(const Triple & p)
{
	//  calculate omega function
    Index(p);
    double om;
    om = (1 - mU) * (1 - mV) * (1 - mW) * mA[mI][mJ][mK] +
        mU * (1 - mV) * (1 - mW) * mA[mI + 1][mJ][mK] +
        mU * mV * (1 - mW) * mA[mI + 1][mJ + 1][mK] +
        (1 - mU) * mV * (1 - mW) * mA[mI][mJ + 1][mK] +
        (1 - mU) * (1 - mV) * mW * mA[mI][mJ][mK + 1] +
        mU * (1 - mV) * mW * mA[mI + 1][mJ][mK + 1] +
        mU * mV * mW * mA[mI + 1][mJ + 1][mK + 1] +
        (1 - mU) * mV * mW * mA[mI][mJ + 1][mK + 1];
    return om;
}

//------------------------------------------------------------------------
// Property()
//
// calculate property
//
int DistanceTransform::Property(const Triple & p)
{
	//  calculate property
    Index(p);
    int ic = mI;
    int jc = mJ;
    int kc = mK;
    if (mW > 0.5) kc++;
    if (mV > 0.5) jc++;
    if (mU > 0.5) ic++;
	return mAc[ic][jc][kc];
}

//------------------------------------------------------------------------
// Omega()
//
// calculate omega function
//
double DistanceTransform::Omega(int i, int j, int k)
{
	//  calculate omega function
    return mA[i][j][k];
}

//------------------------------------------------------------------------
// L()
//
// returns size x
//
int DistanceTransform::L()
{
	return mL;
}

//------------------------------------------------------------------------
// M()
//
// returns size y
//
int DistanceTransform::M()
{
	return mM;
}

//------------------------------------------------------------------------
// N()
//
// returns size z
//
int DistanceTransform::N()
{
	return mN;
}

#endif  								// DISTANCETRANSFORM_INCLUDED
