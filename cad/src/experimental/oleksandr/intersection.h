// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: intersection.h
  Author: Oleksandr Shevchenko
  Description: class for intersection representation   
*/

#if !defined(INTERSECTION_INCLUDED)
#define INTERSECTION_INCLUDED

#include "couple.h"

class Intersection
{

  public:

	//------------------------------------------------------------------------
	// Destructor

	virtual ~Intersection();

	//------------------------------------------------------------------------
	// Collision()
	//
	// intersect tria-tria
	//
	inline int Collision(
		Triple * a,
		Triple * b,
		Triple * p);

  private:

	//------------------------------------------------------------------------
	// ComputeInterval()
	//
	// Compute interval for triangle
	//
	inline int ComputeInterval(
		double d[5],
		double p[3],
		int & i,
		double ratio[2],
		double array[2]);

	//------------------------------------------------------------------------
	// CoplanarTriaTria()
	//
	// if coplanar trias
	//
	inline int CoplanarTriaTria(
		const Triple & n,
		Triple * a,
		Triple * b);

	//------------------------------------------------------------------------
	// EdgeEdgeTest()
	//
	// test for edge intersect
	//
	inline int EdgeEdgeTest(
		const Couple & a0,
		const Couple & a1,
		const Couple & b0,
		const Couple & b1);

	//------------------------------------------------------------------------
	// PointInTria()
	//
	// if point in tria
	//
	inline int PointInTria(
		const Couple & p,
		const Couple & p0,
		const Couple & p1,
		const Couple & p2);
};

//----------------------------------------------------------------------------
// Collision()

inline int Intersection::Collision(
	Triple * a,
	Triple * b,
	Triple * p)
{
	//  "A Fast Triangle-Triangle Intersection Test" by Tomas Moller
	//
	//  calculate plane na*t+d0
		Triple na = (a[1]-a[0])*(a[2]-a[0]);
		double d0 = na%a[0];
	//  project b onto a
		double db[5];
		db[0] = (na%b[0])-d0;
		db[1] = (na%b[1])-d0;
		db[2] = (na%b[2])-d0;
		db[3] = db[0] * db[1];
		db[4] = db[0] * db[2];
	//  check for intersect
		if(db[3]>0.0 && db[4]>0.0) return 0;
	
	//  calculate plane nb*t+d1
		Triple nb = (b[1]-b[0])*(b[2]-b[0]);
		double d1 = nb%b[0];
	//  project a onto b
		double da[5];
		da[0] = (nb%a[0])-d1;
		da[1] = (nb%a[1])-d1;
		da[2] = (nb%a[2])-d1;
		da[3] = da[0] * da[1];
		da[4] = da[0] * da[2];
	//  check for intersect
		if(da[3]>0.0 && da[4]>0.0) return 0;
	
	//  compute direction of intersection line
		Triple direction = na * nb;
	
	//  compute and index to the largest component
		double max=fabs(direction.X());
		int index=0;
		double bb=fabs(direction.Y());
		double cc=fabs(direction.Z());
		if(bb>max) max=bb,index=1;
		if(cc>max) max=cc,index=2;
	
	//  this is the simplified projection
		double ap[3];
		ap[0] = a[0].Get(index);
		ap[1] = a[1].Get(index);
		ap[2] = a[2].Get(index);
	
		double bp[3];
		bp[0] = b[0].Get(index);
		bp[1] = b[1].Get(index);
		bp[2] = b[2].Get(index);
	
	//  compute intervals for intersection
		int ii,jj;
		double ratio0[2], ratio1[2];
		double array0[2], array1[2];
		if (ComputeInterval(da,ap,ii,ratio0,array0))
		{
			return CoplanarTriaTria(na,a,b);
		}
		if (ComputeInterval(db,bp,jj,ratio1,array1))
		{
			return CoplanarTriaTria(na,a,b);
		}
	
	//  some sorting
		int i = array0[0]>array0[1] ? 1 : 0;
		int j = array1[0]>array1[1] ? 1 : 0;
	
	//  check for intersect
		if(array0[i^1]<array1[j] || array1[j^1]<array0[i]) return 0;
	
	//  calculate coordinates of points
		if (p)
		{
			Triple point0[2], point1[2];
			point0[0]=a[ii]+ratio0[0]*(a[(ii+1)%3]-a[ii]);
			point0[1]=a[ii]+ratio0[1]*(a[(ii+2)%3]-a[ii]);
			point1[0]=b[jj]+ratio1[0]*(b[(jj+1)%3]-b[jj]);
			point1[1]=b[jj]+ratio1[1]*(b[(jj+2)%3]-b[jj]);
	
			if (array0[i^1]-array0[i] > array1[j^1]-array1[j])
			{
	//  first greater than second
				if (array1[j] < array0[i])
				{
	//  one side
					p[0] = point0[i];
					p[1] = point1[j^1];
				}
				else if (array1[j^1] > array0[i^1])
				{
	//  other side
					p[0] = point1[j];
					p[1] = point0[i^1];
				}
				else
				{
	//  inside
					p[0] = point1[j];
					p[1] = point1[j^1];
				}
			}
			else
	//  first lesser than second
			{
				if (array0[i] < array1[j])
				{
	//  one side
					p[0] = point1[j];
					p[1] = point0[i^1];
				}
				else if (array0[i^1] > array1[j^1])
				{
	//  other side
					p[0] = point0[i];
					p[1] = point1[j^1];
				}
				else
				{
	//  inside
					p[0] = point0[i];
					p[1] = point0[i^1];
				}
			}
		}
		return 1;
}

//----------------------------------------------------------------------------
// ComputeInterval()

inline int Intersection::ComputeInterval(
	double d[5],
	double p[3],
	int & i,
	double ratio[2],
	double array[2])
{
	if(d[3]>0.0)
		i=2;
	else if(d[4]>0.0)
		i=1;
	else if(d[1]*d[2]>0.0 || d[0]!=0.0)
		i=0;
	else if(d[1]!=0.0)
		i=1;
	else if(d[2]!=0.0)
		i=2;
	else
	//  triangles are coplanar
		return(1);
	//  intersection parameters
	ratio[0]=d[i]/(d[i]-d[(i+1)%3]);
	ratio[1]=d[i]/(d[i]-d[(i+2)%3]);
	array[0]=p[i]+ratio[0]*(p[(i+1)%3]-p[i]);
	array[1]=p[i]+ratio[1]*(p[(i+2)%3]-p[i]);
	return(0);
}

//----------------------------------------------------------------------------
// CoplanarTriaTria()

inline int Intersection::CoplanarTriaTria(
	const Triple & n,
	Triple * a,
	Triple * b)
{
	double r;
	int variant = n.Greatest(r);
	//  simple projection into 2D
	Couple u0(variant,a[0].X(),a[0].Y(),a[0].Z());
	Couple u1(variant,a[1].X(),a[1].Y(),a[1].Z());
	Couple u2(variant,a[2].X(),a[2].Y(),a[2].Z());
	Couple v0(variant,b[0].X(),b[0].Y(),b[0].Z());
	Couple v1(variant,b[1].X(),b[1].Y(),b[1].Z());
	Couple v2(variant,b[2].X(),b[2].Y(),b[2].Z());
	//  test all edges of triangle 1 against the edges of triangle 2
	if (EdgeEdgeTest(u0,u1,v0,v1)) return 1;
	if (EdgeEdgeTest(u0,u1,v1,v2)) return 1;
	if (EdgeEdgeTest(u0,u1,v2,v0)) return 1;
	//
	if (EdgeEdgeTest(u1,u2,v0,v1)) return 1;
	if (EdgeEdgeTest(u1,u2,v1,v2)) return 1;
	if (EdgeEdgeTest(u1,u2,v2,v0)) return 1;
	//
	if (EdgeEdgeTest(u2,u0,v0,v1)) return 1;
	if (EdgeEdgeTest(u2,u0,v1,v2)) return 1;
	if (EdgeEdgeTest(u2,u0,v2,v0)) return 1;
	//  test if triangle 1 is totally contained in triangle 2 or vice versa
	if (PointInTria(u0, v0, v1, v2)) return 1;
	if (PointInTria(v0, u0, u1, u2)) return 1;
	return 0;
}

//----------------------------------------------------------------------------
// EdgeEdgeTest()

inline int Intersection::EdgeEdgeTest(
	const Couple & a0,
	const Couple & a1,
	const Couple & b0,
	const Couple & b1)
{
	Couple a(a0,a1);
	Couple b(b1,b0);
	Couple c(b0,a0);
	//    calculate determinant
	double ab = a.V()*b.U() - a.U()*b.V();
	if(ab)
	{
	//        solve for first segment
		double bc = b.V()*c.U() - b.U()*c.V();
		if (ab>0.0)
		{
	//            check for intersect
			if(bc>=0.0 && bc<=ab)
			{
	//                solve for second segment
				double ac = a.U()*c.V() - a.V()*c.U();
	//                check for intersect
				if(ac>=0.0 && ac<=ab)
				{
					return 1;
				}
			}
		}
		else
		{
	//            check for intersect
			if(bc<=0.0 && bc>=ab)
			{
	//                solve for second segment
				double ac = a.U()*c.V() - a.V()*c.U();
	//                check for intersect
				if(ac<=0.0 && ac>=ab)
				{
					return 1;
				}
			}
		}
	}
	else
	{
	//        for parallel edges
		double ac = a.U()*c.V() - a.V()*c.U();
		if (ac == 0.0)
		{
	//            coplanar edges
			double ta[2],tb[2];
	//            best direction
			if (fabs(a.U()) > fabs(a.V()))
			{
	//                x interval for a with sorting
				if (a0.U() > a1.U())
				{
					ta[0] = a1.U();
					ta[1] = a0.U();
				}
				else
				{
					ta[0] = a0.U();
					ta[1] = a1.U();
				}
	//                x interval for b with sorting
				if (b0.U() > b1.U())
				{
					tb[0] = b1.U();
					tb[1] = b0.U();
				}
				else
				{
					tb[0] = b0.U();
					tb[1] = b1.U();
				}
			}
			else
			{
	//                y interval for a with sorting
				if (a0.V() > a1.V())
				{
					ta[0] = a1.V();
					ta[1] = a0.V();
				}
				else
				{
					ta[0] = a0.V();
					ta[1] = a1.V();
				}
	//                y interval for b with sorting
				if (b0.V() > b1.V())
				{
					tb[0] = b1.V();
					tb[1] = b0.V();
				}
				else
				{
					tb[0] = b0.V();
					tb[1] = b1.V();
				}
			}
	//            check for ntersect
			if (ta[1] >= tb[0] && tb[1] >= ta[0])
				return 1;
		}
	}
	return 0;
}

//----------------------------------------------------------------------------
// PointInTria()  

inline int Intersection::PointInTria(
	const Couple & p,
	const Couple & p0,
	const Couple & p1,
	const Couple & p2)
{
	//    calculate for first edge
	double a = p1.U() - p0.U();
	double b = p0.V() - p1.V();
	double c = p1.U()*p0.V() - p0.U()*p1.V();
	if (a*p.V() + b*p.U() >= c)
	{
	//        calculate for second edge
		a = p2.U() - p1.U();
		b = p1.V() - p2.V();
		c = p2.U()*p1.V() - p1.U()*p2.V();
		if (a*p.V() + b*p.U() >= c)
		{
	//            calculate for third edge
			a = p0.U() - p2.U();
			b = p2.V() - p0.V();
			c = p0.U()*p2.V() - p2.U()*p0.V();
			if (a*p.V() + b*p.U() >= c) return 1;
		}
	}
	return 0;
}

#endif  								// INTERSECTION_INCLUDED

