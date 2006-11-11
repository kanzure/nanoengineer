/*
  Name: collisiondetector.h
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
  Author: Oleksandr Shevchenko
  Description: class for collisiondetector representation  
*/

#if !defined(COLLISIONDETECTOR_INCLUDED)
#define COLLISIONDETECTOR_INCLUDED

#include "triple.h"
#include "boxtree.h"
#include "hierarchy.h"
#include "rotationmatrix.h"
#include "intersection.h"

class CollisionDetector
{

  public:

	//------------------------------------------------------------------------
	// Constructor

	inline CollisionDetector();

	//------------------------------------------------------------------------
	// Destructor

	virtual ~CollisionDetector();

	//------------------------------------------------------------------------
	// AllContacts()
	//
	// set flag for all contacts
	//
	inline void AllContacts();

	//------------------------------------------------------------------------
	// CalculateDistance()
	//
	// calculate distance
	//
	void CalculateDistance();

	//------------------------------------------------------------------------
	// CalculatePoints()
	//
	// calculate intersection points
	//
	void CalculatePoints();

	//------------------------------------------------------------------------
	// CheckCollision()
	//
	// check for collision between two trees
	//
	void CheckCollision(
		Hierarchy * h0,
		Hierarchy * h1);

	//------------------------------------------------------------------------
	// Clear()
	//
	// clear collision elements
	//
	inline void Clear();

	//------------------------------------------------------------------------
	// CollisionCount()
	//
	// get number of collision
	//
	inline int CollisionCount() const;

	//------------------------------------------------------------------------
	// EntityCount()
	//
	// get number of entities
	//
	inline int EntityCount() const;

	//------------------------------------------------------------------------
	// FirstContact()
	//
	// set flag for first contact
	//
	inline void FirstContact();

	//------------------------------------------------------------------------
	// GetDistance()
	//
	// return mDistance
	//
	inline double GetDistance(
		int i) const;

	//------------------------------------------------------------------------
	// GetDistance()
	//
	// return mDistance
	//
	inline double GetDistance() const;

	//------------------------------------------------------------------------
	// GetEntity()
	//
	// return pointer to entity
	//
	inline Box * GetBox(
		int i) const;

	//------------------------------------------------------------------------
	// GetPoints()
	//
	// pointer to collision triple
	//
	inline Triple * GetPoints() const;

	//------------------------------------------------------------------------
	// PairCount()
	//
	// get number of pair
	//
	inline int PairCount() const;

	//------------------------------------------------------------------------
	// Proximity()
	//
	// set proximity
	//
	inline void Proximity(
		double value);

	//------------------------------------------------------------------------
	// Select()
	//
	// select collision elements
	//
	inline void Select() const;

	//------------------------------------------------------------------------
	// VolumeCount()
	//
	// get number of volumes
	//
	inline int VolumeCount() const;

  private:

	//------------------------------------------------------------------------
	// mEntities

	Container<Box *> mBoxes;	// container for entities in the box

	//------------------------------------------------------------------------
	// mPoints

	Triple * mPoints;					// array for intersection points

	//------------------------------------------------------------------------
	// mDistance

	double * mDistance;					// array for distances

	//------------------------------------------------------------------------
	// mD

	double mD;							// current distance

	//------------------------------------------------------------------------
	// mRm

	RotationMatrix mRm;				// rotation matrix

	//------------------------------------------------------------------------
	// mFrm

	RotationMatrix mFrm;				// rotation matrix (absolute value)

	//------------------------------------------------------------------------
	// mTv

	Triple mTv;						// translation vector

	//------------------------------------------------------------------------
	// mM0

	RotationMatrix * mM0;				// rotation matrix for first object

	//------------------------------------------------------------------------
	// mM1

	RotationMatrix * mM1;				// rotation matrix for second object

	//------------------------------------------------------------------------
	// mV0

	Triple * mV0;						// translation vector for first object

	//------------------------------------------------------------------------
	// mV1

	Triple * mV1;						// translation vector for second object

	//------------------------------------------------------------------------
	// mDelta

	Triple mDelta;					// for boxes adjustment

	//------------------------------------------------------------------------
	// mVolume

	int mVolume;						// number of cheked boxes

	//------------------------------------------------------------------------
	// mEntity

	int mEntity;						// number of cheked trias

	//------------------------------------------------------------------------
	// mCollision

	int mCollision;						// number of collision entities

	//------------------------------------------------------------------------
	// mPair

	int mPair;							// number of pair

	//------------------------------------------------------------------------
	// mFirst

	int mFirst;							// flag for first contact

	//------------------------------------------------------------------------
	// CalculateTransformation()
	//
	// calculate rotation matrix and absolute value
	// and translation vector
	//
	inline void CalculateTransformation(
		Hierarchy * b0,
		Hierarchy * b1);

	//------------------------------------------------------------------------
	// CheckCollision()
	//
	// recursive check for collision
	//
	void CheckCollision(
		BoxTree * bt0,
		BoxTree * bt1);

	//------------------------------------------------------------------------
	// Collision()
	//
	// intersect trias in boxes
	//
	int Collision(
		BoxTree * bt0,
		BoxTree * bt1);

	//------------------------------------------------------------------------
	// Collision()
	//
	// intersection detection
	//
	inline int Collision(
		int ni,
		Triple * a,
		int nj,
		Triple * b,
		Triple * p);

	//------------------------------------------------------------------------
	// IsOverlap()
	//
	// check for boxes overlap
	//
	inline int IsOverlap(
		const Triple & a,
		const Triple & b,
		const Triple & ac,
		const Triple & bc);

	//------------------------------------------------------------------------
	// SplitQuad()
	//
	// divide quad onto 2 trias
	//
	inline void SplitQuad(
		Triple * a,
		Triple * a1,
		Triple * a2);
};

//----------------------------------------------------------------------------
// Constructor

inline CollisionDetector::CollisionDetector():

	mPoints(							// array for intersection points
		0),
	mDistance(							// array for distances
		0),
	mVolume(							// number of cheked boxes
		0),
	mEntity(							// number of cheked trias
		0),
	mCollision(							// number of collision entities
		0),
	mPair(								// number of pair
		0),
	mFirst(								// flag for first contact
		0)
{

}

//----------------------------------------------------------------------------
// AllContacts()

inline void CollisionDetector::AllContacts()
{
	mFirst = 0;
}

//----------------------------------------------------------------------------
// CalculateTransformation()

inline void CollisionDetector::CalculateTransformation(
	Hierarchy * h0,
	Hierarchy * h1)
{
	mM0 = h0->Matrix();
	mM1 = h1->Matrix();
	mV0 = h0->Vector();
	mV1 = h1->Vector();
	
	double EPS = 0.00000001;
	if (mM0 && mM1)
	{
		mRm.Px() = Triple(mM1->Px()%mM0->Px(),mM1->Py()%mM0->Px(),mM1->Pz()%mM0->Px());
		mRm.Py() = Triple(mM1->Px()%mM0->Py(),mM1->Py()%mM0->Py(),mM1->Pz()%mM0->Py());
		mRm.Pz() = Triple(mM1->Px()%mM0->Pz(),mM1->Py()%mM0->Pz(),mM1->Pz()%mM0->Pz());
	}
	else if (mM0)
	{
		mRm.Px() = Triple(mM0->Xx(),mM0->Xy(),mM0->Xz());
		mRm.Py() = Triple(mM0->Yx(),mM0->Yy(),mM0->Yz());
		mRm.Pz() = Triple(mM0->Zx(),mM0->Zy(),mM0->Zz());
	}
	else if (mM1)
	{
		mRm.Px() = Triple(mM1->Xx(),mM1->Yx(),mM1->Zx());
		mRm.Py() = Triple(mM1->Xy(),mM1->Yy(),mM1->Zy());
		mRm.Pz() = Triple(mM1->Xz(),mM1->Yz(),mM1->Zz());
	}
	if (mM0 || mM1)
	{
		mFrm.Px() = Triple(fabs(mRm.Xx())+EPS,fabs(mRm.Xy())+EPS,fabs(mRm.Xz())+EPS);
		mFrm.Py() = Triple(fabs(mRm.Yx())+EPS,fabs(mRm.Yy())+EPS,fabs(mRm.Yz())+EPS);
		mFrm.Pz() = Triple(fabs(mRm.Zx())+EPS,fabs(mRm.Zy())+EPS,fabs(mRm.Zz())+EPS);
	}
	if (mM0)
	{
		mTv = (*mM0) * (*mV1 - *mV0);
	}
	else
	{
		mTv = *mV1 - *mV0;
	}
}

//----------------------------------------------------------------------------
// Clear()

inline void CollisionDetector::Clear()
{
	if (mDistance) delete [] mDistance;
	if (mPoints) delete [] mPoints;
	mDistance = 0;
	mPoints = 0;
	mBoxes.Empty();
	mVolume = 0;
	mEntity = 0;
	mCollision = 0;
	mPair = 0;
}

//----------------------------------------------------------------------------
// Collision()

inline int CollisionDetector::Collision(
	int ni,
	Triple * a,
	int nj,
	Triple * b,
	Triple * p)
{
	Intersection inter;
	int count = 0;
	int i,i1,i2,i3,i4;
	Triple a1[3],a2[3];
	Triple b1[3],b2[3];
	switch (ni)
	{
	case 3:
		switch (nj)
		{
		case 3:
			i = inter.Collision(a,b,p);
			return (i);
		case 4:
			SplitQuad(b,b1,b2);
			i3 = inter.Collision(a,b1,p);
			if (p) count += i3;
			i4 = inter.Collision(a,b2,p+2*count);
			return i3+i4;
		default:
			return 0;
		}
	case 4:
		switch (nj)
		{
		case 3:
			SplitQuad(a,a1,a2);
			i1 = inter.Collision(a1,b,p);
			if (p) count += i1;
			i2 = inter.Collision(a2,b,p+2*count);
			return i1+i2;
		case 4:
			SplitQuad(a,a1,a2);
			SplitQuad(b,b1,b2);
			i1 = inter.Collision(a1,b1,p);
			if (p) count += i1;
			i2 = inter.Collision(a1,b2,p+2*count);
			if (p) count += i2;
			i3 = inter.Collision(a2,b1,p+2*count);
			if (p) count += i3;
			i4 = inter.Collision(a2,b2,p+2*count);
			return i1+i2+i3+i4;
		default:
			return 0;
		}
	default:
		return 0;
	}
}

//----------------------------------------------------------------------------
// CollisionCount()

inline int CollisionDetector::CollisionCount() const
{
	return (mCollision);
}

//----------------------------------------------------------------------------
// EntityCount()

inline int CollisionDetector::EntityCount() const
{
	return (mEntity);
}

//----------------------------------------------------------------------------
// FirstContact()

inline void CollisionDetector::FirstContact()
{
	mFirst = 1;
}

//----------------------------------------------------------------------------
// GetDistance()

inline double CollisionDetector::GetDistance(
	int i) const
{
	return (mDistance[i]);
}

//----------------------------------------------------------------------------
// GetDistance()

inline double CollisionDetector::GetDistance() const
{
	return (mD);
}

//----------------------------------------------------------------------------
// GetBox()

inline Box * CollisionDetector::GetBox(
	int i) const
{
	return (mBoxes[i]);
}

//----------------------------------------------------------------------------
// GetPoints()

inline Triple * CollisionDetector::GetPoints() const
{
	return (mPoints);
}

//----------------------------------------------------------------------------
// IsOverlap()

inline int CollisionDetector::IsOverlap(
	const Triple & a,
	const Triple & b,
	const Triple & ac,
	const Triple & bc)
{
	mVolume++;
	if (!mM0 || !mM1)
	{
	//  static case
		if (fabs(bc.X() + mTv.X() - ac.X()) > b.X() + a.X()) return (0);
		if (fabs(bc.Y() + mTv.Y() - ac.Y()) > b.Y() + a.Y()) return (0);
		if (fabs(bc.Z() + mTv.Z() - ac.Z()) > b.Z() + a.Z()) return (0);
	}
	else
	{
	//  dynamic case
	//  test for overlap (separating axis theorem)
		double m,s;
	//  Ax
		double rax = bc.X()*mRm.Xx() + bc.Y()*mRm.Xy() + bc.Z()*mRm.Xz() + mTv.X() - ac.X();
		m = fabs(rax);
		s = b.X()*mFrm.Xx() + b.Y()*mFrm.Xy() + b.Z()*mFrm.Xz();
		if (m > s + a.X()) return (0);
	//  Ay
		double ray = bc.X()*mRm.Yx() + bc.Y()*mRm.Yy() + bc.Z()*mRm.Yz() + mTv.Y() - ac.Y();
		m = fabs(ray);
		s = b.X()*mFrm.Yx() + b.Y()*mFrm.Yy() + b.Z()*mFrm.Yz();
		if (m > s +a.Y()) return (0);
	//  Az
		double raz = bc.X()*mRm.Zx() + bc.Y()*mRm.Zy() + bc.Z()*mRm.Zz() + mTv.Z() - ac.Z();
		m = fabs(raz);
		s = b.X()*mFrm.Zx() + b.Y()*mFrm.Zy() + b.Z()*mFrm.Zz();
		if (m > s + a.Z()) return (0);
	//  Bx
		m = fabs(rax*mRm.Xx() + ray*mRm.Yx() + raz*mRm.Zx());
		s = a.X()*mFrm.Xx() + a.Y()*mFrm.Yx() + a.Z()*mFrm.Zx();
		if (m > s + b.X()) return (0);
	//  By
		m = fabs(rax*mRm.Xy() + ray*mRm.Yy() + raz*mRm.Zy());
		s = a.X()*mFrm.Xy() + a.Y()*mFrm.Yy() + a.Z()*mFrm.Zy();
		if (m > s + b.Y()) return (0);
	//  Bz
		m = fabs(rax*mRm.Xz() + ray*mRm.Yz() + raz*mRm.Zz());
		s = a.X()*mFrm.Xz() + a.Y()*mFrm.Yz() + a.Z()*mFrm.Zz();
		if (m > s + b.Z()) return (0);
	//  Ax * Bx
		m = fabs(raz*mRm.Yx() - ray*mRm.Zx());
		s = a.Y()*mFrm.Zx() + a.Z()*mFrm.Yx() + b.Y()*mFrm.Xz() + b.Z()*mFrm.Xy();
		if (m > s) return (0);
	//  Ax * By
		m = fabs(raz*mRm.Yy() - ray*mRm.Zy());
		s = a.Y()*mFrm.Zy() + a.Z()*mFrm.Yy() + b.X()*mFrm.Xz() + b.Z()*mFrm.Xx();
		if (m > s) return (0);
	//  Ax * Bz
		m = fabs(raz*mRm.Yz() - ray*mRm.Zz());
		s = a.Y()*mFrm.Zz() + a.Z()*mFrm.Yz() + b.X()*mFrm.Xy() + b.Y()*mFrm.Xx();
		if (m > s) return (0);
	//  Ay * Bx
		m = fabs(rax*mRm.Zx() - raz*mRm.Xx());
		s = a.X()*mFrm.Zx() + a.Z()*mFrm.Xx() + b.Y()*mFrm.Yz() + b.Z()*mFrm.Yy();
		if (m > s) return (0);
	//  Ay * By
		m = fabs(rax*mRm.Zy() - raz*mRm.Xy());
		s = a.X()*mFrm.Zy() + a.Z()*mFrm.Xy() + b.X()*mFrm.Yz() + b.Z()*mFrm.Yx();
		if (m > s) return (0);
	//  Ay * Bz
		m = fabs(rax*mRm.Zz() - raz*mRm.Xz());
		s = a.X()*mFrm.Zz() + a.Z()*mFrm.Xz() + b.X()*mFrm.Yy() + b.Y()*mFrm.Yx();
		if (m > s) return (0);
	//  Az * Bx
		m = fabs(ray*mRm.Xx() - rax*mRm.Yx());
		s = a.X()*mFrm.Yx() + a.Y()*mFrm.Xx() + b.Y()*mFrm.Zz() + b.Z()*mFrm.Zy();
		if (m > s) return (0);
	//  Az * By
		m = fabs(ray*mRm.Xy() - rax*mRm.Yy());
		s = a.X()*mFrm.Yy() + a.Y()*mFrm.Xy() + b.X()*mFrm.Zz() + b.Z()*mFrm.Zx();
		if (m > s) return (0);
	//  Az * Bz
		m = fabs(ray*mRm.Xz() - rax*mRm.Yz());
		s = a.X()*mFrm.Yz() + a.Y()*mFrm.Xz() + b.X()*mFrm.Zy() + b.Y()*mFrm.Zx();
		if (m > s) return (0);
	}
	return (1);
}

//----------------------------------------------------------------------------
// PairCount()

inline int CollisionDetector::PairCount() const
{
	return (mPair);
}

//----------------------------------------------------------------------------
// Select()

inline void CollisionDetector::Select() const
{
}

//----------------------------------------------------------------------------
// SplitQuad()

inline void CollisionDetector::SplitQuad(
	Triple * a,
	Triple * a1,
	Triple * a2)
{
	double l1 = (a[0]-a[2]).Len2();
	double l2 = (a[1]-a[3]).Len2();
	if (l1<l2)
	{
		a1[0] = a[0];
		a1[1] = a[1];
		a1[2] = a[2];
		a2[0] = a[0];
		a2[1] = a[2];
		a2[2] = a[3];
	}
	else
	{
		a1[0] = a[0];
		a1[1] = a[1];
		a1[2] = a[3];
		a2[0] = a[1];
		a2[1] = a[2];
		a2[2] = a[3];
	}
}

//----------------------------------------------------------------------------
// VolumeCount()

inline int CollisionDetector::VolumeCount() const
{
	return (mVolume);
}
#endif  								// COLLISIONDETECTOR_INCLUDED

