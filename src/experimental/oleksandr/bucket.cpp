/*
  Name: bucket.cpp
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
  Author: Oleksandr Shevchenko
  Description: class for bucket representation 
*/

#include "bucket.h"

//----------------------------------------------------------------------------
// Constructor

Bucket::Bucket(int n)
{
	mN = n;
	mNN = n * n;
	mNNN = mNN * n;
	//  memory for bucket
	mA = new Container<int>[mNNN];
	mI = 0;
}

//----------------------------------------------------------------------------
// Add

void Bucket::Add(int i, const Triple & p)
{
	//  add point to bucket
	Index(p);
	mA[mI].Add(i);
}
