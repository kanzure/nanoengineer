// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: collisiondetector.cpp
  Author: Oleksandr Shevchenko
  Description: class for collisiondetector representation  
*/

#include "collisiondetector.h"

//----------------------------------------------------------------------------
// Destructor

CollisionDetector::~CollisionDetector()
{
	if (mPoints) delete [] mPoints;
	mPoints = 0;
}

//----------------------------------------------------------------------------
// CalculatePoints()
//
// calculate intersection points
//
void CollisionDetector::CalculatePoints()
{
	int np = 2*(mPair+1);
	mPoints = new Triple[np]; 
	int n = mEntities.Size();
	int count = 0;
	Triple a[4],b[4];
	for (int i=0; i<n; i+=2)
	{
		int ii = mEntities[i];
		int ni = mH0->Transformation(ii, a);
		int jj = mEntities[i+1];
		int nj = mH1->Transformation(jj, b);
		int num = Collision(ni,a,nj,b,mPoints+count);
		if (num)
		{
			count += (num+num);
		}
	}
}

//----------------------------------------------------------------------------
// CheckCollision()
//
// recursive check for collision
//
void CollisionDetector::CheckCollision(
	BoxTree * bt0,
	BoxTree * bt1)
{
	if (!bt0 || !bt1) return;
	Box * b0 = bt0->GetBox();
	Box * b1 = bt1->GetBox();
	int flag = IsOverlap(b0->Extent()+mDelta,b1->Extent(),b0->Center(),b1->Center());
	//  if boxes are disjoint
	if (!flag) return;
	//  if boxes are overlap
	if (bt0->Empty() && bt1->Empty())
	{
	//  check for intersect entities
		mCollision += Collision(bt0,bt1);
		return;
	}
	if (!bt0->Empty() && !bt1->Empty())
	{
		double r0,r1;
		b0->Extent().Greatest(r0);
		b1->Extent().Greatest(r1);
		if (r0 > r1)
		{
			if (bt0->Left()) CheckCollision(bt0->Left(),bt1);
			if (mCollision && mFirst) return;
			if (bt0->Right()) CheckCollision(bt0->Right(),bt1);
		}
		else
		{
			if (bt1->Left()) CheckCollision(bt0,bt1->Left());
			if (mCollision && mFirst) return;
			if (bt1->Right()) CheckCollision(bt0,bt1->Right());
		}
	}
	else if (bt0->Empty() && !bt1->Empty())
	{
		if (bt1->Left()) CheckCollision(bt0,bt1->Left());
		if (mCollision && mFirst) return;
		if (bt1->Right()) CheckCollision(bt0,bt1->Right());
	}
	else if (!bt0->Empty() && bt1->Empty())
	{
		if (bt0->Left()) CheckCollision(bt0->Left(),bt1);
		if (mCollision && mFirst) return;
		if (bt0->Right()) CheckCollision(bt0->Right(),bt1);
	}
	return;
}

//----------------------------------------------------------------------------
// CheckCollision()
//
// check for collision between two trees
//
void CollisionDetector::CheckCollision(
	Hierarchy * h0,
	Hierarchy * h1)
{
	if (!h0 || !h1) return;
	mH0 = h0;
	mH1 = h1;
	CalculateTransformation();
	CheckCollision(h0->Tree(),h1->Tree());
	return;
}

//----------------------------------------------------------------------------
// Collision()
//
// intersect trias in boxes
//
int CollisionDetector::Collision(
	BoxTree * bt0,
	BoxTree * bt1)
{
	Triple a[4],b[4];
	int n0 = bt0->Size();
	int n1 = bt1->Size();
	int count = 0;
	int num;
	for (int i=0; i<n0; i++)
	{
		Box * b0 = bt0->GetBox(i);
		int ii = int(b0 - mH0->Base());
		int ni = mH0->Transformation(ii, a);
		for (int j=0; j<n1; j++)
		{
			Box * b1 = bt1->GetBox(j);
			int jj = int(b1 - mH1->Base());
			int nj = mH1->Transformation(jj, b);
			mEntity++;
            if (num = Collision(ni,a,nj,b,0))
            {
				//  save collision elements
                mEntities.Add(ii);
                mEntities.Add(jj);
                count++;
                mPair+=num;
            }
		}
	}
	return (count);
}

//----------------------------------------------------------------------------
// Select()
//
// select collision elements
//
void CollisionDetector::Select(int c) const
{
	if (mH0->S() && mH1->S())
	{
		int ni = 3;
		if (mH0->S()->Type()) ni = 4;
		int nj = 3;
		if (mH1->S()->Type()) nj = 4;
		for (int i = 0; i < mCollision; i++)
		{
			int ie = mEntities[2 * i];
			int ii;
			for (ii = 0; ii < ni; ii++)
			{
				int i0 = mH0->S()->I(3 * ie + ii);
				mH0->S()->C(i0, c); 
			}
			int je = mEntities[2 * i + 1];
			for (ii = 0; ii < nj; ii++)
			{
				int j0 = mH1->S()->I(3 * je + ii);
				mH1->S()->C(j0, c);
			}
		}
	}
	else
	{
		//  if no surfaces 
		int ni = 3;
		if (mH0->Type()) ni = 4;
		int nj = 3;
		if (mH1->Type()) nj = 4;
		for (int i = 0; i < mCollision; i++)
		{
			int ie = mEntities[2 * i];
			int ii;
			for (ii = 0; ii < ni; ii++)
			{
				int i0 = mH0->I(3 * ie + ii);
				mH0->C(i0, c); 
			}
			int je = mEntities[2 * i + 1];
			for (ii = 0; ii < nj; ii++)
			{
				int j0 = mH1->I(3 * je + ii);
				mH1->C(j0, c);
			}
		}
	}
}

