/*
  Name: collisiondetector.cpp
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
  Author: Oleksandr Shevchenko
  Description: class for collisiondetector representation  
*/

#include "collisiondetector.h"

//----------------------------------------------------------------------------
// Destructor

CollisionDetector::~CollisionDetector()
{
	if (mDistance) delete [] mDistance;
	if (mPoints) delete [] mPoints;
	mDistance = 0;
	mPoints = 0;
}

//----------------------------------------------------------------------------
// CalculateDistance()
//
// calculate distance
//
void CollisionDetector::CalculateDistance()
{
}

//----------------------------------------------------------------------------
// CalculatePoints()
//
// calculate intersection points
//
void CollisionDetector::CalculatePoints()
{
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
	CalculateTransformation(h0,h1);
	CheckCollision(h0,h1);
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
	return (count);
}
