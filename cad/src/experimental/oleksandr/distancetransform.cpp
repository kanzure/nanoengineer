// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: distancetrasform.cpp
  Author: Oleksandr Shevchenko
  Description: class for distancetrasform representation 
*/

#include "distancetransform.h"

//----------------------------------------------------------------------------
// Constructor

DistanceTransform::DistanceTransform(const Container<Triple> & centers, const Container<double> & radiuses, const Container<int> & properties)
{
	mR = 1;
	for (int ir = 0; ir < radiuses.Size(); ir++)
	{
		double r = radiuses[ir];
		if (r < mR) mR = r;
	}
	
    //double f = 20 * mR + 2;
    //int n = (int)(f  / mR);

	int n = 30; 
	if (mR < 0.1) n = 40;
	if (mR < 0.07) n = 50;
	if (mR < 0.05) n = 60;
	if (mR < 0.03) n = 70;
	if (mR < 0.02) n = 80;
	int m = n;
	int l = n;
	mN = n;
	mM = m;
	mL = l;
	//  memory for omega function
	mC = new double[(l+1)*(m+1)*(n+1)];
	mCc = new int[(l+1)*(m+1)*(n+1)];
	mB = new double*[(l+1)*(m+1)];
	mBc = new int*[(l+1)*(m+1)];
	mA = new double**[l+1];
	mAc = new int**[l+1];
	double* c = mC; 
	int* cc = mCc; 
	double** b = mB;
	int** bc = mBc;
	int i, j;
	for (i = 0; i <= l; i++)
	{
		for (j = 0; j <= m; j++)
		{
			b[j] = c;
			bc[j] = cc;
			c += (n+1);
			cc += (n+1);
		}
		mA[i] = b;
		mAc[i] = bc;
		b += (m+1);
		bc += (m+1);
	}
    mU = 0;
    mV = 0;
    mW = 0;
	mI = 0;
	mJ = 0;
	mK = 0;
    for (int i = 0; i <= mL; i++)
    {
        for (int j = 0; j <= mM; j++)
        {
            for (int k = 0; k <= mN; k++)
            {
                mA[i][j][k] = 255;
                mAc[i][j][k] = 0; 
            }
        }
    }
	Distance(centers, radiuses, properties);
}

//------------------------------------------------------------------------
// Omega()
//
//  calculate predicate for all spheres
//
void DistanceTransform::Omega(const Container<Triple> & centers, const Container<double> & radiuses)
{
	for (int i = 0; i <= mL; i++)
    {
		double x = 2.0 * i / mL - 1.0;
        for (int j = 0; j <= mM; j++)
        {
			double y = 2.0 * j / mM - 1.0;
            for (int k = 0; k <= mN; k++)
            {
				double z = 2.0 * k / mN - 1.0;

                if (mA[i][j][k] > -6.5)
                {
	                double om = 0;
					Triple p(x, y, z);
                    for (int ii = 0; ii < centers.Size(); ii++)
                    {
						Triple t = p - centers[ii];
                        double r = radiuses[ii];
                        double s = (r * r - t.X() * t.X() - t.Y() * t.Y() - t.Z() * t.Z()) / (r + r);
                        if (ii > 0)
                        {
							if (om < s) om = s;
                        }
                        else
                        {
                            om = s;
                        }
                    }
					mA[i][j][k] = om;
                }
            }
        }
    }
}

//------------------------------------------------------------------------
// Distance()
//
//  calculate distance transform
//
void DistanceTransform::Distance(const Container<Triple> & centers, const Container<double> & radiuses, const Container<int> & properties)
{
    //  put centers into the array
    for (int ii = 0; ii < centers.Size(); ii++)
    {

        Index(centers[ii]);
        int d = (int)(radiuses[ii] * mL / 2 + 1);
		if (d < 0) d = 0;
        int ic = mI;
        int jc = mJ;
        int kc = mK;
        if (mW > 0.5) kc++;
        if (mV > 0.5) jc++;
        if (mU > 0.5) ic++;

        int ib = ic - d;
        if (ib < 0) ib = 0;
        int ie = ic + d;
        if (ie >= mL) ie = mL;

        int jb = jc - d;
        if (jb < 0) jb = 0;
        int je = jc + d;
        if (je >= mM) je = mM;

        int kb = kc - d;
        if (kb < 0) kb = 0;
        int ke = kc + d;
        if (ke >= mN) ke = mN;

        for (int i = ib; i <= ie; i++)
        {
			double x = i - mI;
            for (int j = jb; j <= je; j++)
            {
				double y = j - mJ;
                for (int k = kb; k <= ke; k++)
                {
					double z = k - mK;
                    double r = sqrt(x * x + y * y + z * z);
                    if (r <= d)
						mA[i][j][k] = 0;
						mAc[i][j][k] = properties[ii];
                }
            }
        }
    }
            
    for (int i = 1; i <= mL; i++)
    {
	    int ii = mL - i;
        for (int j = 1; j <= mM; j++)
        {
			int jj = mM - j;
            for (int k = 1; k <= mN; k++)
            {
				int kk = mN - k;
                double p = mA[ii][jj][kk];
                double px = mA[ii + 1][jj][kk];
                double py = mA[ii][jj + 1][kk];
                double pz = mA[ii][jj][kk + 1];
                double mi = p < px + 1 ? p : px + 1;
                double mj = p < py + 1 ? p : py + 1;
                double mk = p < pz + 1 ? p : pz + 1;
                double mij = mi < mj ? mi : mj;
                double mijk = mij < mk ? mij : mk;
                mA[ii][jj][kk] = mijk;
            }
        }
    }
    for (int i = 1; i <= mL; i++)
    {
        for (int j = 1; j <= mM; j++)
        {
            for (int k = 1; k <= mN; k++)
            {
                double p = mA[i][j][k];
                double px = mA[i - 1][j][k];
                double py = mA[i][j - 1][k];
                double pz = mA[i][j][k - 1];
                double mi = p < px + 1 ? p : px + 1;
                double mj = p < py + 1 ? p : py + 1;
                double mk = p < pz + 1 ? p : pz + 1;
                double mij = mi < mj ? mi : mj;
                double mijk = mij < mk ? mij : mk;
                mA[i][j][k] = mijk;
            }
        }
    }
    for (int j = 1; j <= mM; j++)
    {
        for (int k = 1; k <= mN; k++)
        {
            mA[0][j][k] = mA[1][j][k] + 1;
        }
    }
    for (int i = 1; i <= mL; i++)
    {
        for (int k = 1; k <= mN; k++)
        {
            mA[i][0][k] = mA[i][1][k] + 1;
        }
    }
    for (int i = 1; i <= mL; i++)
    {
        for (int j = 1; j <= mM; j++)
        {
            mA[i][j][0] = mA[i][j][1] + 1;
        }
    }
    for (int i = 1; i <= mL; i++)
    {
        mA[i][0][0] = mA[i][0][1] + 1;
    }
    for (int j = 1; j <= mM; j++)
    {
        mA[0][j][0] = mA[0][j][1] + 1;
    }
    for (int k = 1; k <= mN; k++)
    {
        mA[0][0][k] = mA[0][1][k] + 1;
    }
    for (int i = 0; i <= mL; i++)
    {
        for (int j = 0; j <= mM; j++)
        {
            for (int k = 0; k <= mN; k++)
            {
                mA[i][j][k] = -mA[i][j][k];
            }
        }
    }
}
	

	
