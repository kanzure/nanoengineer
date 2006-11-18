/*
  Name: hierarchy.h
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
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
	void Initialize(
		Surface * s);

	//------------------------------------------------------------------------
	// Matrix()
	//
	// pointer to collision matrix
	//
	inline RotationMatrix * Matrix() const;

	//------------------------------------------------------------------------
	// Number()
	//
	// set number
	//
	inline int & Number();

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

  private:

	//------------------------------------------------------------------------
	// mBoxes

	Container<Box> mBoxes;				// array for boxes

	//------------------------------------------------------------------------
	// mNumber

	int mNumber;						// max number of elements in box

	//------------------------------------------------------------------------
	// mTree

	BoxTree * mTree;					// bounding box tree

	//------------------------------------------------------------------------
	// mRm

	RotationMatrix * mRm;				// rotation matrix

	//------------------------------------------------------------------------
	// mTv

	Triple * mTv;						// translation vector
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
// Number()

inline int & Hierarchy::Number()
{
	return (mNumber);
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
#endif  								// HIERARCHY_INCLUDED

