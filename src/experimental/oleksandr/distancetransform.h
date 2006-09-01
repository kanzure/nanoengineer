/*
  Name: distancetrasform.h
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
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
	DistanceTransform(int l, int m, int n);
	
	//------------------------------------------------------------------------
	// Omega()
	//
	//  calculate predicate for all spheres
	//
	void Omega(const Container<Triple> & centers, const Container<double> & radiuses);
	
	//------------------------------------------------------------------------
	// Distance()
	//
	//  calculate distance transform
	//
	void Distance(const Container<Triple> & centers, const Container<double> & radiuses);
	
	//------------------------------------------------------------------------
	// Omega()
	//
	// calculate omega function
	//
	inline double Omega(const Triple & p);

  private:
          
	//------------------------------------------------------------------------
	// Index()
	//
	// calculate index
	//
	inline void Index(const Triple & p);

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
             
};

//----------------------------------------------------------------------------
// Index()

inline void DistanceTransform::Index(const Triple & p)
{
	//  calculate index for point p
    mU = (mL * (p.X() + 1) / 2);
    mI = (int)mU;
    mU -= mI;
	if ( mI < 0) mI = 0;
	if ( mI >= mL) mI = mL - 1;

    mV = (mM * (p.Y() + 1) / 2);
    mJ = (int)mV;
    mV -= mJ;
	if ( mJ < 0) mJ = 0;
	if ( mJ >= mM) mJ = mM - 1;

    mW = (mN * (p.Z() + 1) / 2);
    mK = (int)mW;
    mW -= mK;
	if ( mK < 0) mK = 0;
	if ( mK >= mN) mK = mN - 1;
}

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

#endif  								// DISTANCETRANSFORM_INCLUDED
