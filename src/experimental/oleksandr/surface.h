/*
  Name: surface.h
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
  Author: Oleksandr Shevchenko
  Description: class for surface representation 
*/

#if !defined(SURFACE_INCLUDED)
#define SURFACE_INCLUDED

#include "container.h"
#include "triple.h"
#include "bucket.h"

class Surface
{

  public:
	//------------------------------------------------------------------------
	// Constructor
	//
	//  empty Surface
	//
	inline Surface();
	
	//------------------------------------------------------------------------
	// CreateSurface()
	//
	// create surface triangles
	//
	void CreateSurface();

	//------------------------------------------------------------------------
	// Level()
	//
	// set level member
	//
	inline void Level(int l);

	//------------------------------------------------------------------------
	// Type()
	//
	// get type
	//
	inline int Type();

	//------------------------------------------------------------------------
	// Add()
	//
	// add centers and radiuses
	//
	inline void Add(double x, double y, double z, double r);

	//------------------------------------------------------------------------
	// Np()
	//
	// get size of points
	//
	inline int Np();

	//------------------------------------------------------------------------
	// Nt()
	//
	// get size of trias
	//
	inline int Nt();

	//------------------------------------------------------------------------
	// Px()
	//
	// get x coordinate
	//
	inline double Px(int i);

	//------------------------------------------------------------------------
	// Py()
	//
	// get y coordinate
	//
	inline double Py(int i);

	//------------------------------------------------------------------------
	// Pz()
	//
	// get z coordinate
	//
	inline double Pz(int i);

	//------------------------------------------------------------------------
	// Nx()
	//
	// get x normal component
	//
	inline double Nx(int i);

	//------------------------------------------------------------------------
	// Ny()
	//
	// get y normal component
	//
	inline double Ny(int i);

	//------------------------------------------------------------------------
	// Nz()
	//
	// get z normal component
	//
	inline double Nz(int i);

	//------------------------------------------------------------------------
	// I()
	//
	// get trias index
	//
	inline int I(int i);

  private:
          
	//------------------------------------------------------------------------
	// SurfaceNormals()
	//
	// calculate surface normals
	//
	void SurfaceNormals();

	//------------------------------------------------------------------------
	// Duplicate()
	//
	// delete duplicate points
	//
	void Duplicate();

	//------------------------------------------------------------------------
	// SphereTriangles()
	//
	// create sphere triangles
	//
	void SphereTriangles();

	//------------------------------------------------------------------------
	// TorusRectangles()
	//
	// create torus rectangles
	//
	void TorusRectangles();

	//------------------------------------------------------------------------
	// CalculateTorus()
	//
	// torus parametrization
	//
	Triple CalculateTorus(double a, double b, double u, double v);

    //------------------------------------------------------------------------
    // OmegaRectangles()
    //
    // create omega rectangles
    //
    void OmegaRectangles();

    //------------------------------------------------------------------------
    // Quad()
    //
    // generate quad
    //
    void Quad(Triple p0, Triple p1, Triple p2, Triple p3);

    //------------------------------------------------------------------------
    // Tria()
    //
    // generate tria
    //
    void Tria(Triple p0, Triple p1, Triple p2);

    //------------------------------------------------------------------------
	// Subdivide()
	//
	// recurcive subdividing on sphere
	//
	void Subdivide(
		Triple a,
		Triple b,
		Triple c,		
		int deep);

	//------------------------------------------------------------------------
	// Predicate()
	//
	// calculate omega function
	// positive inside 
	// equal to zero on the boundary
	// negative outside
	//
	double Predicate(
		const Triple & p);

	//------------------------------------------------------------------------
	// mSpheres

    Container<Triple> mCenters;      // array for centers of spheres                                          
             
	//------------------------------------------------------------------------
	// mRadiuses

    Container<double> mRadiuses;     // array for radiuses                                          
             
	//------------------------------------------------------------------------
	// mType

	int mType;						// type of entity (tria, quad)

	//------------------------------------------------------------------------
	// mBp

	Bucket * mBp;					// bucket for predicate

	//------------------------------------------------------------------------
	// mL

	int mL;							// level for trias generation

	//------------------------------------------------------------------------
	// mPoints

    Container<Triple> mPoints;      // array for points on surface                                          
             
	//------------------------------------------------------------------------
	// mNormals

    Container<Triple> mNormals;      // array for normals to surface                                          
             
	//------------------------------------------------------------------------
	// mEntities

    Container<int> mEntities;        // array for indices                                          
             
};

//----------------------------------------------------------------------------
// Constructor

inline Surface::Surface()
{
	mBp = 0;
    mType = 0;
    mL = 3;
}

//------------------------------------------------------------------------
// Level()
//
// set level member
//
inline void Surface::Level(int l)
{
	mL = l;
}

//------------------------------------------------------------------------
// Type()
//
// get type
//
inline int Surface::Type()
{
	return mType;
}

//------------------------------------------------------------------------
// Add()
//
// add centers and radiuses
//
inline void Surface::Add(double x, double y, double z, double r)
{
	mCenters.Add(Triple(x, y, z));
	mRadiuses.Add(r);
}

//------------------------------------------------------------------------
// Np()
//
// get size of points
//
inline int Surface::Np()
{
	return mPoints.Size();
}

//------------------------------------------------------------------------
// Nt()
//
// get size of entities
//
inline int Surface::Nt()
{
	return mEntities.Size();
}

//------------------------------------------------------------------------
// Px()
//
// get x coordinate
//
inline double Surface::Px(int i)
{
	return mPoints[i].X();
}

//------------------------------------------------------------------------
// Py()
//
// get y coordinate
//
inline double Surface::Py(int i)
{
	return mPoints[i].Y();
}

//------------------------------------------------------------------------
// Pz()
//
// get z coordinate
//
inline double Surface::Pz(int i)
{
	return mPoints[i].Z();
}

//------------------------------------------------------------------------
// Nx()
//
// get x normal component
//
inline double Surface::Nx(int i)
{
	return mNormals[i].X();
}

//------------------------------------------------------------------------
// Ny()
//
// get y normal component
//
inline double Surface::Ny(int i)
{
	return mNormals[i].Y();
}

//------------------------------------------------------------------------
// Nz()
//
// get z normal component
//
inline double Surface::Nz(int i)
{
	return mNormals[i].Z();
}

//------------------------------------------------------------------------
// I()
//
// get trias index
//
inline int Surface::I(int i)
{
	return mEntities[i];
}

#endif  								// SURFACE_INCLUDED
