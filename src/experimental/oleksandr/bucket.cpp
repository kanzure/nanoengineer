// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: bucket.cpp
  Author: Oleksandr Shevchenko
  Description: class for bucket representation 
*/

#include "bucket.h"

//----------------------------------------------------------------------------
// Constructor

Bucket::Bucket(int l, int m, int n)
{
	mN = n;
	mM = m;
	mL = l;
	//  memory for bucket
	mC = new Container<int>[l*m*n];
	mB = new Container<int>*[l*m];
	mA = new Container<int>**[l];
	Container<int>* c = mC; 
	Container<int>** b = mB;
	int i, j;
	for (i = 0; i < l; i++)
	{
		for (j = 0; j < m; j++)
		{
			b[j] = c;
			c += n;
		}
		mA[i] = b;
		b += m;
	}
	mI = 0;
	mJ = 0;
	mK = 0;
}

//----------------------------------------------------------------------------
// Add
//
//  add points to bucket
//

void Bucket::Add(const Container<Triple> & points)
{
	for (int i = 0; i < points.Size(); i++)
	{
		Index(points[i]);
		mA[mI][mJ][mK].Add(i);
	}
}

//------------------------------------------------------------------------
// Duplicate
//
//  find duplicate points
//
void Bucket::Duplicate(const Container<Triple> & points, int * ia)
{
	double eps = 0.0000001;
	for (int i = 0; i < points.Size(); i++)
	{
		Triple p = points[i];
		Index(p);
		for (int jv = 0; jv < Size(); jv++)
		{
			int j = Value(jv);
			if (i == j) continue;
			if (ia[j] > 0)
			{
				if ((p - points[j]).Len2() < eps)
				{
					ia[j] = -ia[i];
				}
			}
		}
	}
}

	
