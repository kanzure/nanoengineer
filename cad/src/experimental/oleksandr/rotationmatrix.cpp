// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: rotationmatrix.cpp
  Author: Oleksandr Shevchenko
  Description: class for rotation in 3-D space  
*/

#include "rotationmatrix.h"

//----------------------------------------------------------------------------
// Constructor

RotationMatrix::RotationMatrix()
{
	mPx = Triple(1,0,0);
	mPy = Triple(0,1,0);
	mPz = Triple(0,0,1);
}

//----------------------------------------------------------------------------
// Constructor

RotationMatrix::RotationMatrix(
	const Triple & p0,
	const Triple & p1,
	const Triple & p2):

	mPx(								// first row of rotation matrix
		p0),
	mPy(								// second row of rotation matrix
		p1),
	mPz(								// third row of rotation matrix
		p2)
{

}

//----------------------------------------------------------------------------
// Calculate()
//
// apply rotation
//
Triple RotationMatrix::Calculate(
	const Triple & p)
{
	double x = p % mPx;
	double y = p % mPy;
	double z = p % mPz;
	return (Triple(x,y,z));
}

//----------------------------------------------------------------------------
// Initialize()
//
// formation of rotation matrix
//
void RotationMatrix::Initialize(
	const Triple & v,
	double ca)
{
	double eps = 1e-10;
	//    v - rotation axis
	//    ca - cosinus of rotation angle
	double vlen = v.Len();
	if (vlen < eps )
	{
	//      if no rotation
		if (ca < eps - 1)
		{
	//        angle == pi
			mPx = Triple(-1,0,0);
			mPy = Triple(0,-1,0);
			mPz = Triple(0,0,-1);
		}
		return;
	}
	//    calculate constants
	double sa = sqrt(1 - ca*ca);
	double c1 = 1 - ca;
	double vx = v.X()/vlen, vy = v.Y()/vlen, vz = v.Z()/vlen;
	double vxy = vx*vy, vxz = vx*vz, vyz = vy*vz;
	//    formation of rotation matrix
	mPx = Triple(vx * vx * c1 + ca, vxy * c1 + sa * vz, vxz * c1 - sa * vy);
	mPy = Triple(vxy * c1 - sa * vz, vy * vy * c1 + ca, vyz * c1 + sa * vx);
	mPz = Triple(vxz * c1 + sa * vy, vyz * c1 - sa * vx, vz * vz * c1 + ca);
}
