/*
  Name: hierarchy.cpp
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
  Author: Oleksandr Shevchenko
  Description: class for hierarchy representation 
*/

#include "hierarchy.h"

//----------------------------------------------------------------------------
// Constructor

Hierarchy::Hierarchy():

	// Private data initialization
	mNumber(							// max number of elements in box
		1),
	mRm(								// rotation matrix
		0),
	mTv(								// translation vector
		0)
{
	mTree = new BoxTree;
}

//----------------------------------------------------------------------------
// Destructor

Hierarchy::~Hierarchy()
{
	if (mTree)
	{
		mTree->Delete();
		delete mTree;
		mTree = 0;
	}
}

//------------------------------------------------------------------------
// Initialize()
//
// create box tree 
//
void Hierarchy::Initialize(
	Surface * s)
{
	int i,j;
	int n = 3;
	if (s->Type()) n = 4;
	for (i = 0; i < s->Nt(); i+=n)
	{
		Box b;
		for (j = 0; j < n; j++)
		{
			int ij = s->I(i + j);
			Triple p(s->Px(ij), s->Py(ij), s->Pz(ij));
			b.Enclose(p);
		}
		mBoxes.Add(b);
	}
	for (i = 0; i < s->Nt()/n; i++)
	{
		mTree->Add(&mBoxes[i]);
	}
	mTree->Base = &mBoxes[0];
	mTree->BuildTree();
}

