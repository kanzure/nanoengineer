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

