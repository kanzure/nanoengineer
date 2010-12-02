// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: rotationmatrix.h
  Author: Oleksandr Shevchenko
  Description: class for rotation in 3-D space  
*/

#if !defined(ROTATIONMATRIX_INCLUDED)
#define ROTATIONMATRIX_INCLUDED

#include <math.h>
#include "triple.h"

class RotationMatrix
{

  public:

	//------------------------------------------------------------------------
	// Constructor

	RotationMatrix();

	//------------------------------------------------------------------------
	// Constructor

	RotationMatrix(
		const Triple & p0,
		const Triple & p1,
		const Triple & p2);

	//------------------------------------------------------------------------
	// Calculate()
	//
	// apply rotation
	//
	Triple Calculate(
		const Triple & p);

	//------------------------------------------------------------------------
	// Initialize()
	//
	// formation of rotation matrix
	//
	void Initialize(
		const Triple & v,
		double ca);

	//------------------------------------------------------------------------
	// Px()
	//
	// direction for x axis
	//
	inline Triple Px() const;

	//------------------------------------------------------------------------
	// Px()
	//
	// direction for x axis
	//
	inline Triple & Px();

	//------------------------------------------------------------------------
	// Py()
	//
	// direction for y axis
	//
	inline Triple Py() const;

	//------------------------------------------------------------------------
	// Py()
	//
	// direction for y axis
	//
	inline Triple & Py();

	//------------------------------------------------------------------------
	// Pz()
	//
	// direction for z axis
	//
	inline Triple Pz() const;

	//------------------------------------------------------------------------
	// Pz()
	//
	// direction for z axis
	//
	inline Triple & Pz();

	//------------------------------------------------------------------------
	// RotateX()
	//
	// rotation around X axis
	//
	inline void RotateX(
		double sa,
		double ca);

	//------------------------------------------------------------------------
	// RotateXY()
	//
	// rotation around X axis then Y axis
	//
	inline void RotateXY(
		double sa,
		double ca);

	//------------------------------------------------------------------------
	// RotateXYZ()
	//
	// rotation around X axis, Y axis then Z axis
	//
	inline void RotateXYZ(
		double sa,
		double ca);

	//------------------------------------------------------------------------
	// RotateXZ()
	//
	// rotation around X axis then Z axis
	//
	inline void RotateXZ(
		double sa,
		double ca);

	//------------------------------------------------------------------------
	// RotateY()
	//
	// rotation around Y axis
	//
	inline void RotateY(
		double sa,
		double ca);

	//------------------------------------------------------------------------
	// RotateYZ()
	//
	// rotation around Y axis then Z axis
	//
	inline void RotateYZ(
		double sa,
		double ca);

	//------------------------------------------------------------------------
	// RotateZ()
	//
	// rotation around Z axis
	//
	inline void RotateZ(
		double sa,
		double ca);

	//------------------------------------------------------------------------
	// Xx()
	//
	// get matrix element
	//
	inline double Xx() const;

	//------------------------------------------------------------------------
	// Xy()
	//
	// get matrix element
	//
	inline double Xy() const;

	//------------------------------------------------------------------------
	// Xz()
	//
	// get matrix element
	//
	inline double Xz() const;

	//------------------------------------------------------------------------
	// Yx()
	//
	// get matrix element
	//
	inline double Yx() const;

	//------------------------------------------------------------------------
	// Yy()
	//
	// get matrix element
	//
	inline double Yy() const;

	//------------------------------------------------------------------------
	// Yz()
	//
	// get matrix element
	//
	inline double Yz() const;

	//------------------------------------------------------------------------
	// Zx()
	//
	// get matrix element
	//
	inline double Zx() const;

	//------------------------------------------------------------------------
	// Zy()
	//
	// get matrix element
	//
	inline double Zy() const;

	//------------------------------------------------------------------------
	// Zz()
	//
	// get matrix element
	//
	inline double Zz() const;

  private:

	//------------------------------------------------------------------------
	// mPx

	Triple mPx;						// first row of rotation matrix

	//------------------------------------------------------------------------
	// mPy

	Triple mPy;						// second row of rotation matrix

	//------------------------------------------------------------------------
	// mPz

	Triple mPz;						// third row of rotation matrix
};

//----------------------------------------------------------------------------
// operator *()
//
// multipliction of two matrix C = AxB
//
inline RotationMatrix operator *(
	const RotationMatrix & a,
	const RotationMatrix & b);

//----------------------------------------------------------------------------
// operator *()
//
//  matrix * vector product
//
inline Triple operator *(
	const RotationMatrix & a,
	const Triple & b);

//----------------------------------------------------------------------------
// operator *()
//
//  vector * matrix product
//
inline Triple operator *(
	const Triple & a,
	const RotationMatrix & b);

//----------------------------------------------------------------------------
// operator *()

inline RotationMatrix operator *(
	const RotationMatrix & a,
	const RotationMatrix & b)
{
	return RotationMatrix(
		Triple(a.Px() % b.Px(),a.Py() % b.Px(),a.Pz() % b.Px()),
		Triple(a.Px() % b.Py(),a.Py() % b.Py(),a.Pz() % b.Py()),
		Triple(a.Px() % b.Pz(),a.Py() % b.Pz(),a.Pz() % b.Pz())
		);
}

//----------------------------------------------------------------------------
// operator *()

inline Triple operator *(
	const RotationMatrix & a,
	const Triple & b)
{
	return Triple(a.Px() % b,a.Py() % b,a.Pz() % b);
}

//----------------------------------------------------------------------------
// operator *()

inline Triple operator *(
	const Triple & a,
	const RotationMatrix & b)
{
	return Triple(
		b.Xx() * a.X() + b.Yx() * a.Y() + b.Zx() * a.Z(),
		b.Xy() * a.X() + b.Yy() * a.Y() + b.Zy() * a.Z(),
		b.Xz() * a.X() + b.Yz() * a.Y() + b.Zz() * a.Z()
		);
}

//----------------------------------------------------------------------------
// Px()

inline Triple RotationMatrix::Px() const
{
	return (mPx);
}

//----------------------------------------------------------------------------
// Px()

inline Triple & RotationMatrix::Px()
{
	return (mPx);
}

//----------------------------------------------------------------------------
// Py()

inline Triple RotationMatrix::Py() const
{
	return (mPy);
}

//----------------------------------------------------------------------------
// Py()

inline Triple & RotationMatrix::Py()
{
	return (mPy);
}

//----------------------------------------------------------------------------
// Pz()

inline Triple RotationMatrix::Pz() const
{
	return (mPz);
}

//----------------------------------------------------------------------------
// Pz()

inline Triple & RotationMatrix::Pz()
{
	return (mPz);
}

//----------------------------------------------------------------------------
// RotateX()

inline void RotationMatrix::RotateX(
	double sa,
	double ca)
{
	//    rotation x
	Px() = Triple(1,0,0);
	Py() = Triple(0,ca,sa);
	Pz() = Triple(0,-sa,ca);
}

//----------------------------------------------------------------------------
// RotateXY()

inline void RotationMatrix::RotateXY(
	double sa,
	double ca)
{
	//    rotation xy
	Px() = Triple(ca,sa*sa,-sa*ca);
	Py() = Triple(0,ca,sa);
	Pz() = Triple(sa,-sa*ca,ca*ca);
}

//----------------------------------------------------------------------------
// RotateXYZ()

inline void RotationMatrix::RotateXYZ(
	double sa,
	double ca)
{
	//    rotation xyz
	Px() = Triple(ca*ca,sa*ca+sa*sa*ca,sa*sa-sa*ca*ca);
	Py() = Triple(-sa*ca,ca*ca-sa*sa*sa,sa*ca+sa*sa*ca);
	Pz() = Triple(sa,-sa*ca,ca*ca);
}

//----------------------------------------------------------------------------
// RotateXZ()

inline void RotationMatrix::RotateXZ(
	double sa,
	double ca)
{
	//    rotation xz
	Px() = Triple(ca,ca*sa,sa*sa);
	Py() = Triple(-sa,ca*ca,sa*ca);
	Pz() = Triple(0,-sa,ca);
}

//----------------------------------------------------------------------------
// RotateY()

inline void RotationMatrix::RotateY(
	double sa,
	double ca)
{
	//    rotation y
	Px() = Triple(ca,0,-sa);
	Py() = Triple(0,1,0);
	Pz() = Triple(sa,0,ca);
}

//----------------------------------------------------------------------------
// RotateYZ()

inline void RotationMatrix::RotateYZ(
	double sa,
	double ca)
{
	//    rotation yz
	Px() = Triple(ca*ca,sa,-sa*ca);
	Py() = Triple(-sa*ca,ca,sa*sa);
	Pz() = Triple(sa,0,ca);
}

//----------------------------------------------------------------------------
// RotateZ()

inline void RotationMatrix::RotateZ(
	double sa,
	double ca)
{
	//    rotation z
	Px() = Triple(ca,sa,0);
	Py() = Triple(-sa,ca,0);
	Pz() = Triple(0,0,1);
}

//----------------------------------------------------------------------------
// Xx()

inline double RotationMatrix::Xx() const
{
	return(mPx.X());
}

//----------------------------------------------------------------------------
// Xy()

inline double RotationMatrix::Xy() const
{
	return(mPx.Y());
}

//----------------------------------------------------------------------------
// Xz()

inline double RotationMatrix::Xz() const
{
	return(mPx.Z());
}

//----------------------------------------------------------------------------
// Yx()

inline double RotationMatrix::Yx() const
{
	return(mPy.X());
}

//----------------------------------------------------------------------------
// Yy()

inline double RotationMatrix::Yy() const
{
	return(mPy.Y());
}

//----------------------------------------------------------------------------
// Yz()

inline double RotationMatrix::Yz() const
{
	return(mPy.Z());
}

//----------------------------------------------------------------------------
// Zx()

inline double RotationMatrix::Zx() const
{
	return(mPz.X());
}

//----------------------------------------------------------------------------
// Zy()

inline double RotationMatrix::Zy() const
{
	return(mPz.Y());
}

//----------------------------------------------------------------------------
// Zz()

inline double RotationMatrix::Zz() const
{
	return(mPz.Z());
}
#endif  								// ROTATIONMATRIX_INCLUDED

