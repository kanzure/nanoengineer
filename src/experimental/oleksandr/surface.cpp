/*
  Name: surface.cpp
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
  Author: Oleksandr Shevchenko
  Description: class for surface representation 
*/

#include "surface.h"
#include "bucket.h"

//------------------------------------------------------------------------
// Subdivide()
//
// recurcive subdividing on sphere
//
void Surface::Subdivide(
	Triple a,
	Triple b,
	Triple c,		
	int deep)
{
    if (deep)
    {
		// recurcive subdividing
        Triple a1 = a.Normalize();
        Triple b1 = b.Normalize();
        Triple c1 = c.Normalize();
        Triple d = (a1 + b1).Normalize();
        Triple e = (b1 + c1).Normalize();
        Triple f = (c1 + a1).Normalize();
        Subdivide(a, d, f, deep - 1);
        Subdivide(d, e, f, deep - 1);
        Subdivide(d, b, e, deep - 1);
        Subdivide(f, e, c, deep - 1);
    }
    else
    {
		//  generate tria
		Tria(a, b, c);
    }
}

//------------------------------------------------------------------------
// SphereTriangles()
//
// create sphere triangles
//
void Surface::SphereTriangles()
{
	mType = 0;
    // the golden ratio
    double phi = (1.0 + sqrt(5.0)) / 2.0;
    Triple vert(phi, 0, 1);
    vert.Normalize();
    double a = vert.X();
    double b = vert.Y();
    double c = vert.Z();

    // vertices of an icosahedron
    Triple p[12];
    p[0] = Triple(-a, b, c);
    p[1] = Triple(b, c, -a);
    p[2] = Triple(b, c, a);
    p[3] = Triple(a, b, -c);
    p[4] = Triple(-c, -a, b);
    p[5] = Triple(-c, a, b);
    p[6] = Triple(b, -c, a);
    p[7] = Triple(c, a, b);
    p[8] = Triple(b, -c, -a);
    p[9] = Triple(a, b, c);
    p[10] = Triple(c, -a, b);
    p[11] = Triple(-a, b, -c);

    int ip [60] = {9, 2, 6, 1, 11, 5, 11, 1, 8, 0, 11, 4, 3, 1, 7,
                   3, 8, 1, 9, 3, 7, 0, 6, 2, 4, 10, 6, 1, 5, 7,
                   7, 5, 2, 8, 3, 10, 4, 11, 8, 9, 7, 2, 10, 9, 6,
                   0, 5, 11, 0, 2, 5, 8, 10, 4, 3, 9, 10, 6, 0, 4};

    for (int i = 0; i < 20; i++)
    {
        Subdivide(p[ip[3 * i]], p[ip[3 * i + 1]], p[ip[3 * i + 2]], mL);
    }
}


//------------------------------------------------------------------------
// CalculateTorus()
//
// torus parametrization
//
Triple Surface::CalculateTorus(double a, double b, double u, double v)
{
	double pi2 = 2 * 3.1415926535897932; 
	//    transformation function - torus
	double cf = cos(pi2*u);
	double sf = sin(pi2*u);
	double ct = cos(pi2*v);
	double st = sin(pi2*v);
	//    point on torus
	Triple temp((a+b*ct)*cf,(a+b*ct)*sf,b*st);
	return(temp);
}

//------------------------------------------------------------------------
// TorusRectangles()
//
// create torus rectangles
//
void Surface::TorusRectangles()
{
	mType = 1;
	int n = 3 * mL;
	double a = 0.7;
	double b = 0.3;
	int n6 = int(6*a*n);
	if (n6 == 0) n6 = 6;
	int n2 = int(6*b*n);
	if (n2 == 0) n2 = 6;
	int i,j;
	for (i=0; i<n6; i++)
	{
		double u0 = i/(double)n6;
		double u1 = (i+1)/(double)n6;
		for (j=0; j<n2; j++)
		{
			double v0 = j/(double) n2;
			double v1 = (j+1)/(double) n2;

			Triple p0 = CalculateTorus(a,b,u0,v0);
			Triple p1 = CalculateTorus(a,b,u1,v0);
			Triple p2 = CalculateTorus(a,b,u1,v1);
			Triple p3 = CalculateTorus(a,b,u0,v1);

			Quad(p0, p1, p2, p3);
		}
	}
}

//------------------------------------------------------------------------
// OmegaRectangles()
//
// create omega rectangles
//
void Surface::OmegaRectangles()
{
	mType = 1;
    int nx = 41;
    int ny = 41;
    int nz = 41;
    for (int i = 0; i < nx; i++)
    {
        double x0 = 2.0 * i / nx - 1.0;
        double x1 = 2.0 * (i + 1) / nx - 1.0;
        for (int j = 0; j < ny; j++)
        {
            double y0 = 2.0 * j / ny - 1.0;
            double y1 = 2.0 * (j + 1) / ny - 1.0;
            for (int k = 0; k < nz; k++)
            {
                double z0 = 2.0 * k / nz - 1.0;
                double z1 = 2.0 * (k + 1) / nz - 1.0;

                Triple p0(x0, y0, z0);
                Triple p1(x0, y0, z1);
                Triple p2(x0, y1, z0);
                Triple p3(x0, y1, z1);
                Triple p4(x1, y0, z0);
                Triple p5(x1, y0, z1);
                Triple p6(x1, y1, z0);
                Triple p7(x1, y1, z1);
                int flag = 0;
                double eps = 0.0001;
                double w0 = Predicate(p0);
                double w1 = Predicate(p1);
                double w2 = Predicate(p2);
                double w3 = Predicate(p3);
                double w4 = Predicate(p4);
                double w5 = Predicate(p5);
                double w6 = Predicate(p6);
                double w7 = Predicate(p7);
                if (w0 < eps) flag += 1;
                if (w1 < eps) flag += 2;
                if (w2 < eps) flag += 4;
                if (w3 < eps) flag += 8;
                if (w4 < eps) flag += 16;
                if (w5 < eps) flag += 32;
                if (w6 < eps) flag += 64;
                if (w7 < eps) flag += 128;
                switch (flag)
                {
                    default:

                        if (w0 < eps && w1 < eps && w3 < eps && w2 < eps)
                        {
                            Quad(p0, p1, p3, p2);
                        }
                        if (w4 < eps && w6 < eps && w7 < eps && w5 < eps)
                        {
                            Quad(p4, p6, p7, p5);
                        }
                        if (w0 < eps && w4 < eps && w5 < eps && w1 < eps)
                        {
                            Quad(p0, p4, p5, p1);
                        }
                        if (w2 < eps && w3 < eps && w7 < eps && w6 < eps)
                        {
                            Quad(p2, p3, p7, p6);
                        }
                        if (w0 < eps && w2 < eps && w6 < eps && w4 < eps)
                        {
                            Quad(p0, p2, p6, p4);
                        }
                        if (w1 < eps && w5 < eps && w7 < eps && w3 < eps)
                        {
                            Quad(p1, p5, p7, p3);
                        }

                        break;
                    case 0:
                        break;
                    case 255:
                        break;
                }
            }
        }
    }
}

//------------------------------------------------------------------------
// Quad()
//
// generate quad
//
void Surface::Quad(Triple p0, Triple p1, Triple p2, Triple p3)
{
	mPoints.Add(p0);
	mPoints.Add(p1);
	mPoints.Add(p2);
	mPoints.Add(p3);
}
       
//------------------------------------------------------------------------
// Tria()
//
// generate tria
//
void Surface::Tria(Triple p0, Triple p1, Triple p2)
{
	mPoints.Add(p0);
	mPoints.Add(p1);
	mPoints.Add(p2);
}
       
//------------------------------------------------------------------------
// Predicate()
//
// calculate omega function
// positive inside 
// equal to zero on the boundary
// negative outside
//
double Surface::Predicate(
	const Triple & p)
{
	double om = 0;
	//  calculate omega functions for all spheres
	for (int i = 0; i < mCenters.Size(); i++)
	{
		Triple t = p - mCenters[i];
		double r = mRadiuses[i];
		double s = (r * r - t.X() * t.X() - t.Y() * t.Y() - t.Z() * t.Z()) / (r + r); 
		if (i)
		{
			if (om < s) om = s;
			//om = (om + s + sqrt(om * om + s * s))/2; 
		}
		else
		{
			om = s;
		}
	}

	double om1 = mBp->Predicate(mCenters, mRadiuses, p);
	return om;
}

//------------------------------------------------------------------------
// CreateSurface()
//
// create surface triangles
//
void Surface::CreateSurface()
{
	mBp = new Bucket(21,17,13);
	mBp->Add(mCenters);
	switch (mM)
	{
	case 0:
        SphereTriangles();
		break;
	case 1:
		TorusRectangles();
		break;
	case 2:
		OmegaRectangles();
		break;
	}
	Duplicate();
	SurfaceNormals();
	int n = 4; // number of iterations
	for (int i = 0; i < n; i++)
	{
		for (int j = 0; j < mPoints.Size(); j++)
		{
			Triple p = mPoints[j];
			Triple n = mNormals[j];
			if (n.Len2() > 0)
				n.Normalize();
			double om = Predicate(p);
			if (om < -1.0) om = -1.0;
			mPoints[j] = p + 0.25 * om * n;
		}
	}
	SurfaceNormals();
	delete mBp;
}

//------------------------------------------------------------------------
// SurfaceNormals()
//
// calculate surface normals
//
void Surface::SurfaceNormals()
{
	int i;
	mNormals.Empty();
	for (i = 0; i< mPoints.Size(); i++)
	{
		mNormals.Add(Triple(0,0,0));
	}
	if (mType)
	{
		for (i = 0; i < mEntities.Size(); i += 4)
		{
			Triple v0(mPoints[mEntities[i]], mPoints[mEntities[i + 2]]);
			Triple v1(mPoints[mEntities[i + 1]], mPoints[mEntities[i + 3]]);
			Triple n = v0 * v1;
			mNormals[mEntities[i]] += n;
			mNormals[mEntities[i + 1]] += n;
			mNormals[mEntities[i + 2]] += n;
			mNormals[mEntities[i + 3]] += n;
		}
	}
	else
	{
		for (i = 0; i < mEntities.Size(); i += 3)
		{
			Triple v0(mPoints[mEntities[i]], mPoints[mEntities[i + 1]]);
			Triple v1(mPoints[mEntities[i]], mPoints[mEntities[i + 2]]);
			Triple n = v0 * v1;
			mNormals[mEntities[i]] += n;
			mNormals[mEntities[i + 1]] += n;
			mNormals[mEntities[i + 2]] += n;
		}
	}
}

//------------------------------------------------------------------------
// Duplicate()
//
// delete duplicate points
//
void Surface::Duplicate()
{
	double eps = 0.0000001;
	int n = mPoints.Size();
	int * ia = new int[n];
	int i, j;
	for (i = 0; i < n; i++)
	{
		ia[i] = i + 1;
	}
	//  find and mark duplicate points
	int nb = 17;
	Bucket bd(nb, nb, nb);
	bd.Add(mPoints);
	bd.Duplicate(mPoints, ia);
	int k = 0;
    //    change array for points & normals
    //    change index
	for (i=0; i<n; i++)
	{
		if (ia[i] > 0)
		{
			mPoints[k] = mPoints[i];
			ia[i] = ++k;
		}
		else
		{
            int ir = ia[i];
            if (ir < 0) ir = -ia[i];
			ia[i] = ia[ir - 1];
		}
	}
    //    delete extra points and normals
	for (i=0; i<n-k; i++)
	{
		mPoints.DeleteLast();
	}
    //    change entities for delete duplicate points
    for (i = 0; i < n; i++)
    {
        mEntities.Add(ia[i] - 1);
    }
}

