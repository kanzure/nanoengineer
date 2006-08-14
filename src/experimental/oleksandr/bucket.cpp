/*
  Name: bucket.cpp
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
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

void Bucket::Add(const Container<Triple> & points)
{
	//  add points to bucket
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
	
//------------------------------------------------------------------------
// Predicate
//
//  calculate predicate for all spheres
//
double Bucket::Predicate(const Container<Triple> & centers, const Container<double> & radiuses, const Triple & p)
{
	double om = -1;
	//  calculate omega functions for all spheres
	int d = 1;

	Index(p);
	int ib = mI - d;
	if ( ib < 0) ib = 0;
	int ie = mI + d;
	if ( ie >= mL) ie = mL - 1;

	int jb = mJ - d;
	if ( jb < 0) jb = 0;
	int je = mJ + d;
	if ( je >= mM) je = mM - 1;

	int kb = mK - d;
	if ( kb < 0) kb = 0;
	int ke = mK + d;
	if ( ke >= mN) ke = mN - 1;

	int ijk = 0;
	for (int i = ib; i <= ie; i++)
	{
		for (int j = jb; j <= je; j++)
		{
			for (int k = kb; k <= ke; k++)
			{
				for (int ii = 0; ii < mA[i][j][k].Size(); ii++)
				{
					int iii = mA[i][j][k][ii];
					Triple t = p - centers[iii];
					double r = radiuses[iii];
					double s = (r * r - t.X() * t.X() - t.Y() * t.Y() - t.Z() * t.Z()) / (r + r); 
					if (ijk)
					{
						if (om < s) om = s;
					}
					else
					{
						om = s;
						ijk++;
					}
				}
			}
		}
	}
	return om;
}

	
