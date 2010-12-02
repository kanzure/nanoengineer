// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: hierarchy.cpp
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
		0),
	mS(								    // surface pointer
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
void Hierarchy::Initialize(Surface * s)
{
	int i,j;
	mS = s;
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
// Initialize()
//
// create box tree 
//
void Hierarchy::Initialize(int type, Container<int> I, Container<Triple> P, Container<int> C)
{
	//  initialize by arrays
	mType = type;
	mNE = I.Size();
	mEntities = I.GetPtr();
	mNP = P.Size();
	mPoints = P.GetPtr();
	mColors = C.GetPtr();

	int i,j;
	int n = 3;
	if (mType) n = 4;
	for (i = 0; i < mNE; i+=n)
	{
		Box b;
		for (j = 0; j < n; j++)
		{
			int ij = mEntities[i + j];
			b.Enclose(mPoints[ij]);
		}
		mBoxes.Add(b);
	}
	for (i = 0; i < mNE/n; i++)
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
	if (mS)
	{
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
	}
	else
	{
		//  calulation from array 
		if (mType) n = 4;
		for (int j = 0; j < n; j++)
		{
			int ij = mEntities[3*i + j];
			if (mRm)
			{
				a[j] = *mTv + mPoints[ij] * (*mRm); 
			}
			else
			{
				a[j] = *mTv + mPoints[ij];
			}
		}
	}
	return n;
}

