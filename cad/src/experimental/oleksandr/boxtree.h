// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: boxtree.h
  Author: Oleksandr Shevchenko
  Description: class for boxtree representation 
*/

#if !defined(BOXTREE_INCLUDED)
#define BOXTREE_INCLUDED

#include "box.h"
#include "container.h"

class BoxTree
{

  public:

	//------------------------------------------------------------------------
	// Constructor

	BoxTree();

	//------------------------------------------------------------------------
	// Destructor

	~BoxTree();

	//------------------------------------------------------------------------
	// Add()
	//
	// add box into container
	//
	void Add(
		Box * box);

	//------------------------------------------------------------------------
	// AllocateTree()
	//
	// memory for tree
	//
	inline int AllocateTree();

	//------------------------------------------------------------------------
	// BestAxe()
	//
	// best split axe
	//
	int BestAxe();

	//------------------------------------------------------------------------
	// BuildTree()
	//
	// create bounding volume box tree
	//
	int BuildTree();

	//------------------------------------------------------------------------
	// Delete()
	//
	// delete tree
	//
	inline void Delete();

	//------------------------------------------------------------------------
	// DeleteLeaf()
	//
	// delete memory for tree
	//
	inline void DeleteLeaf();

	//------------------------------------------------------------------------
	// Duplicate()
	//
	// delete duplicate entities
	//
	void Duplicate(
		Box * base,
		int * ia);

	//------------------------------------------------------------------------
	// Duplicate()
	//
	// delete duplicate entities
	//
	void Duplicate(
		Box * base, 
		int * ia,
		BoxTree * bt);

	//------------------------------------------------------------------------
	// Empty()
	//
	// break tree
	//
	inline int Empty();

	//------------------------------------------------------------------------
	// FreeTree()
	//
	// delete memory for tree
	//
	inline void FreeTree();

	//------------------------------------------------------------------------
	// GetBox()
	//
	// return box pointer
	//
	inline Box * GetBox();

	//------------------------------------------------------------------------
	// GetBox()
	//
	// return pointer to box
	//
	inline Box * GetBox(
		int i) const;

	//------------------------------------------------------------------------
	// Initialize()
	//
	// formation of main box
	//
	int Initialize(
		const Container<Box *> & box);

	//------------------------------------------------------------------------
	// Left()
	//
	// get left pointer
	//
	inline BoxTree * Left() const;

	//------------------------------------------------------------------------
	// Right()
	//
	// get right pointer
	//
	inline BoxTree * Right() const;

	//------------------------------------------------------------------------
	// Size()
	//
	// get number of elements
	//
	inline int Size() const;

	//------------------------------------------------------------------------
	// WhichBox()
	//
	// classification of points
	//
	inline int WhichBox(
		int variant,
		int i);

  protected:

	//------------------------------------------------------------------------
	// Delete()
	//
	// recursive delete
	//
	void Delete(
		BoxTree * tree);

  private:

	//------------------------------------------------------------------------
	// mLeft

	BoxTree * mLeft;					// first leaf for tree

	//------------------------------------------------------------------------
	// mRight

	BoxTree * mRight;					// second leaf for tree

	//------------------------------------------------------------------------
	// mBox

	Box mBox;							// bounding box

	//------------------------------------------------------------------------
	// mBoxes

	Container<Box *> mBoxes;			// container for entities in the box

	//------------------------------------------------------------------------
	// Split()
	//
	// split box
	//
	int Split();
};

//----------------------------------------------------------------------------
// AllocateTree()

inline int BoxTree::AllocateTree()
{
	mLeft = new BoxTree;
	if (!mLeft) return 0;
	mRight = new BoxTree;
	if (!mRight) return 0;
	return 1;
}

//----------------------------------------------------------------------------
// Delete()

inline void BoxTree::Delete()
{
	Delete(this);
}

//----------------------------------------------------------------------------
// DeleteLeaf()

inline void BoxTree::DeleteLeaf()
{
	if (mLeft)
	{
		delete mLeft;
		mLeft = 0;
	}
	if (mRight)
	{
		delete mRight;
		mRight = 0;
	}
}

//----------------------------------------------------------------------------
// Empty()

inline int BoxTree::Empty()
{
	return (!(Left() || Right()));
}

//----------------------------------------------------------------------------
// FreeTree()

inline void BoxTree::FreeTree()
{
	if (mLeft)
	{
		delete mLeft;
		mLeft = 0;
	}
	if (mRight)
	{
		delete mRight;
		mRight = 0;
	}
}

//----------------------------------------------------------------------------
// GetBox()

inline Box * BoxTree::GetBox()
{
	return (&mBox);
}

//----------------------------------------------------------------------------
// GetBox()

inline Box * BoxTree::GetBox(
	int i) const
{
	return (mBoxes[i]);
}

//----------------------------------------------------------------------------
// Left()

inline BoxTree * BoxTree::Left() const
{
	return (mLeft);
}

//----------------------------------------------------------------------------
// Right()

inline BoxTree * BoxTree::Right() const
{
	return (mRight);
}

//----------------------------------------------------------------------------
// Size()

inline int BoxTree::Size() const
{
	return (mBoxes.Size());
}

//----------------------------------------------------------------------------
// WhichBox()

inline int BoxTree::WhichBox(
	int variant,
	int i)
{
	Triple center = mBoxes[i]->Center() - mBox.Center();
	Triple d2 = 2*mBox.Extent();
	double x,y,z,u=0;
	switch (variant)
	{
	default:
		break;
	case 1:
		z = center.Z();
		u = z/d2.Z();
		break;
	case 2:
		y = center.Y();
		u = y/d2.Y();
		break;
	case 3:
		x = center.X();
		u = x/d2.X();
		break;
	}
	return (u<0 ? 0 : 1);
}
#endif  								// BOXTREE_INCLUDED

