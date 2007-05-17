// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: hierarchy.h
  Author: Oleksandr Shevchenko
  Description: class for hierarchy representation 
*/

#if !defined(HIERARCHY_INCLUDED)
#define HIERARCHY_INCLUDED

#include "box.h"
#include "boxtree.h"
#include "container.h"
#include "rotationmatrix.h"
#include "surface.h"

class Hierarchy
{

  public:

	//------------------------------------------------------------------------
	// Constructor

	Hierarchy();

	//------------------------------------------------------------------------
	// Destructor

	~Hierarchy();

	//------------------------------------------------------------------------
	// Behavior()
	//
	// set pointer to rotation matrix
	//
	inline void Behavior(
		RotationMatrix * matrix);

	//------------------------------------------------------------------------
	// Behavior()
	//
	// set pointers to rotation matrix & translation vector
	//
	inline void Behavior(
		RotationMatrix * matrix,
		Triple * vector);

	//------------------------------------------------------------------------
	// Behavior()
	//
	// set pointer to translation vector
	//
	inline void Behavior(
		Triple * vector);

	//------------------------------------------------------------------------
	// Initialize()
	//
	// create box tree 
	//
	void Initialize(Surface * s);

	//------------------------------------------------------------------------
	// Initialize()
	//
	// create box tree 
	//
	void Initialize(int type, Container<int> I, Container<Triple> P, Container<int> C);

	//------------------------------------------------------------------------
	// Matrix()
	//
	// pointer to collision matrix
	//
	inline RotationMatrix * Matrix() const;

	//------------------------------------------------------------------------
	// Base()
	//
	// get base pointer
	//
	inline Box * Base();

	//------------------------------------------------------------------------
	// Size()
	//
	// size of container
	//
	inline int Size();

	//------------------------------------------------------------------------
	// Tree()
	//
	// get tree pointer
	//
	inline BoxTree * Tree() const;

	//------------------------------------------------------------------------
	// Vector()
	//
	// pointer to collision triple
	//
	inline Triple * Vector() const;

	//------------------------------------------------------------------------
	// Transformation()
	//
	// rotation and translation entities 
	//
	int Transformation(int i, Triple * a);

	//------------------------------------------------------------------------
	// S()
	//
	// pointer to surface 
	//
	inline Surface * S() const;

	//------------------------------------------------------------------------
	// Type()
	//
	// get type
	//
	inline int Type();

	//------------------------------------------------------------------------
	// I()
	//
	// get trias index
	//
	inline int I(int i);

	//------------------------------------------------------------------------
	// C()
	//
	// set color property
	//
	inline void C(int i, int c);

  private:

	//------------------------------------------------------------------------
	// mBoxes

	Container<Box> mBoxes;				// array for boxes

	//------------------------------------------------------------------------
	// mTree

	BoxTree * mTree;					// bounding box tree

	//------------------------------------------------------------------------
	// mRm

	RotationMatrix * mRm;				// rotation matrix

	//------------------------------------------------------------------------
	// mTv

	Triple * mTv;						// translation vector

	//------------------------------------------------------------------------
	// mS

	Surface * mS;						// pointer to surface

	//------------------------------------------------------------------------
	// mType

	int mType;							// type of surface

	//------------------------------------------------------------------------
	// mNP

	int mNP;							// size of points array

	//------------------------------------------------------------------------
	// mNE

	int mNE;							// size of entities array

	//------------------------------------------------------------------------
	// mPoints

    Triple * mPoints;					// array for points on surface                                           

	//------------------------------------------------------------------------
	// mColors

    int * mColors;						// array for colors on surface                                          
             
	//------------------------------------------------------------------------
	// mEntities

    int * mEntities;					// array for indices                                          
};

//----------------------------------------------------------------------------
// Behavior()

inline void Hierarchy::Behavior(
	RotationMatrix * matrix)
{
	mRm = matrix;
}

//----------------------------------------------------------------------------
// Behavior()

inline void Hierarchy::Behavior(
	RotationMatrix * matrix,
	Triple * vector)
{
	mRm = matrix;
	mTv = vector;
}

//----------------------------------------------------------------------------
// Behavior()

inline void Hierarchy::Behavior(
	Triple * vector)
{
	mTv = vector;
}

//----------------------------------------------------------------------------
// Matrix()

inline RotationMatrix * Hierarchy::Matrix() const
{
	return (mRm);
}

//----------------------------------------------------------------------------
// Base()

inline Box * Hierarchy::Base()
{
	return (&mBoxes[0]);
}

//----------------------------------------------------------------------------
// Size()

inline int Hierarchy::Size()
{
	return (mBoxes.Size());
}

//----------------------------------------------------------------------------
// Tree()

inline BoxTree * Hierarchy::Tree() const
{
	return (mTree);
}

//----------------------------------------------------------------------------
// Vector()

inline Triple * Hierarchy::Vector() const
{
	return (mTv);
}

//------------------------------------------------------------------------
// S()

inline Surface * Hierarchy::S() const
{
	return (mS);
}

//------------------------------------------------------------------------
// Type()
//
inline int Hierarchy::Type()
{
	return mType;
}

//------------------------------------------------------------------------
// I()
//
inline int Hierarchy::I(int i)
{
	return mEntities[i];
}

//------------------------------------------------------------------------
// C()
//
inline void Hierarchy::C(int i, int c)
{
	mColors[i] = c; 
}

#endif  								// HIERARCHY_INCLUDED

