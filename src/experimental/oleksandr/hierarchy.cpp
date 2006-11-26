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
	mS = s;
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
	mTree->BuildTree();
}

//------------------------------------------------------------------------
// Transformation()
//
// rotation and translation entity  
//
int Hierarchy::Transformation(int i, Triple * a)
{
	int n = 3;
	if (mS->Type()) n = 4;
	for (int j = 0; j < n; j++)
	{
		int ij = mS->I(3*i + j);
		Triple p(mS->Px(ij), mS->Py(ij), mS->Pz(ij));
		if (mRm)
		{
			a[j] = *mTv + p * (*mRm); 
		}
		else
		{
			a[j] = *mTv + p;
		}
	}
	return n;
}

