// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/*
  Name: surface.h
  Author: Oleksandr Shevchenko
  Description: class for surface representation 
*/

#if !defined(SURFACE_INCLUDED)
#define SURFACE_INCLUDED

#include "container.h"
#include "triple.h"
#include "distancetransform.h"

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
	// CreateSurface()
	//
	// create surface
	//
	void CreateSurface(Surface * s0, Surface * s1, double delta);  

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
	// Method()
	//
	// set surface method
	//
	inline void Method(int m);

	//------------------------------------------------------------------------
	// Add()
	//
	// add centers and radiuses and properties
	//
	inline void Add(double x, double y, double z, double r, int p);

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
	// Nc()
	//
	// get size of properties
	//
	inline int Nc();

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
	// C()
	//
	// get color property
	//
	inline int C(int i);

	//------------------------------------------------------------------------
	// C()
	//
	// set color property
	//
	inline void C(int i, int c);

	//------------------------------------------------------------------------
	// I()
	//
	// get trias index
	//
	inline int I(int i);

  private:
          
	//------------------------------------------------------------------------
	// CleanQuads()
	//
	// delete duplicate quads
	//
	void CleanQuads();

	//------------------------------------------------------------------------
	// SurfaceNormals()
	//
	// calculate surface normals
	//
	void SurfaceNormals();

	//------------------------------------------------------------------------
	// SurfaceColors()
	//
	// calculate surface colors
	//
	void SurfaceColors();

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
	// mProperties

    Container<int> mProperties;     // array for properties                                          
             
	//------------------------------------------------------------------------
	// mType

	int mType;						// type of entity (tria, quad)

	//------------------------------------------------------------------------
	// mDT

	DistanceTransform * mDT;		// distance transform for predicate

	//------------------------------------------------------------------------
	// mL

	int mL;							// level for trias generation

	//------------------------------------------------------------------------
	// mM

	int mM;							// surface method

	//------------------------------------------------------------------------
	// mPoints

    Container<Triple> mPoints;      // array for points on surface                                          
             
	//------------------------------------------------------------------------
	// mNormals

    Container<Triple> mNormals;      // array for normals to surface                                          
             
	//------------------------------------------------------------------------
	// mColors

    Container<int> mColors;      // array for colors on surface                                          
             
	//------------------------------------------------------------------------
	// mEntities

    Container<int> mEntities;        // array for indices                                          
             
};

//----------------------------------------------------------------------------
// Constructor

inline Surface::Surface()
{
	mDT = 0;
    mType = 0;
	mM = 0;
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
// Method()
//
// set surface method
//
inline void Surface::Method(int m)
{
	mM = m; 
}

//------------------------------------------------------------------------
// Add()
//
// add centers and radiuses and properties
//
inline void Surface::Add(double x, double y, double z, double r, int p)
{
	mCenters.Add(Triple(x, y, z));
	mRadiuses.Add(r);
	mProperties.Add(p);
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
// C()
//
// get color property 
//
inline int Surface::C(int i)
{
	return mColors[i];
}

//------------------------------------------------------------------------
// C()
//
// set color property  
//
inline void Surface::C(int i, int c)
{
	mColors[i] = c; 
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
