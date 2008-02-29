#ifndef MATH_VECTOR3_H
#define MATH_VECTOR3_H

/*

  GLT OpenGL C++ Toolkit (LGPL)
  Copyright (C) 2000-2002 Nigel Stewart  

  Email: nigels@nigels.com   
  WWW:   http://www.nigels.com/glt/

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

*/

/*! \file 
\brief   3D Vector
\ingroup Math
*/

#include <iosfwd>
#include <string>

#include "glt_config.h"
#include "glt_real.h"

class GltMatrix;
class GltViewport;

////////////////////////// Vector /////////////////////////////////

/*! \class   Vector 
\brief   3D Vector
\ingroup Math
\todo    Nice pictures and explanation. Dot product, Cross product, etc.
*/

class Vector
{
    friend std::ostream &operator<<(std::ostream &os, const Vector &x);
    friend std::istream &operator>>(std::istream &is,       Vector &x);
    
    friend Vector operator*(const Vector  &v, const real x);
    friend Vector operator/(const Vector  &v, const real x);
    friend Vector operator*(const real     x, const Vector &v);
    friend Vector operator+(const Vector &v1, const Vector &v2);
    friend Vector operator-(const Vector &v1, const Vector &v2);
    friend Vector xProduct (const Vector &v1, const Vector &v2);
    
    friend Vector planeNormal(const Vector &v1, const Vector &v2,const Vector &v3);
    
    friend Vector polar(const real lat,const real longitude);
    
    friend void orthogonalSystem(Vector &a,Vector &b,Vector &c);
    
public:
    /// Default constructor
    Vector();
    /// Copy constructor
    Vector(const Vector &v);
    /// Constructor
    Vector(const real x, const real y,const real z);
    /// Constructor
    Vector(const float  *v);
    /// Constructor
    Vector(const double *v);
    /// Construct from string
    Vector(const std::string &str);
    
    /// x co-ordinate
    real &x();
    /// x co-ordinate
    const real &x() const;
    
    /// y co-ordinate
    real &y();
    /// y co-ordinate
    const real &y() const;
    
    /// z co-ordinate
    real &z();
    /// z co-ordinate
    const real &z() const;
    
    /// i'th co-ordinate
    real &operator[](const int i);
    /// i'th co-ordinate
    const real &operator[](const int i) const;
    
    /// Access as array
    operator real* (void) { return _vector; }
    
    /// Equality operator
    bool operator==(const Vector &v) const;
    /// Inequality operator
    bool operator!=(const Vector &v) const;
    /// Equality operator: x==a && y==a && z==a
    bool operator==(const real &a) const;
    
    /// less-than comparison
    bool operator< (const Vector &c) const;
    /// greater-than comparison
    bool operator> (const Vector &c) const;
    
    /// Assignment operator
    Vector &operator= (const Vector &v);
    /// Assignment operator
    Vector &operator= (const float *);
    /// Assignment operator
    Vector &operator= (const double *);
    /// Addition
    Vector &operator+=(const Vector &v);
    /// Subtraction
    Vector &operator-=(const Vector &v);
    
    /// Vector dot product (aka scalar product)
    real operator*(const Vector &v) const;
    /// Multiply
    Vector &operator*=(const real &x);
    /// GltMatrix Transformation
    Vector &operator*=(const GltMatrix &m);
    /// Negative
    Vector operator-() const;
    
                    /// Scale 
    void scale(const real &x);
                    /// Scale
    void scale(const Vector &x);
    
                    /// Normalise the vector: |x| = 1.0
    void normalize();
                    /// Make x, y and z positive
    void abs();
                    /// Find the dominant component: x, y or z
    int  dominant() const;
    
                    /// Squared length of vector
    real norm() const;
                    /// Squared distance between vectors
    real dist(const Vector &x) const;
    
                    /// Length of vector
    real length() const;
    
                    /// Map object co-ordinates to window co-ordinates
    bool project(const GltMatrix &model,const GltMatrix &proj,const GltViewport &view);
    
                    /// Replace with minimum x, y and z
    Vector &vmin(const Vector &v);
                    /// Replace with maximum x, y and z
    Vector &vmax(const Vector &v);
    
                    /// Draw OpenGL vertex
    void glVertex() const;
                    /// Draw OpenGL normal
    void glNormal() const;
                    /// Draw OpenGL color
    void glColor() const;
                    /// Draw OpenGL texture co-ordinate
    void glTexCoord() const;
    
    void glLight(GLenum light, GLenum pname) const;
    
                    /// Write vector in Povray format
    std::ostream &writePov(std::ostream &os) const;
    
protected:
    /// Storage for x, y and z components
    real _vector[3];
};

/// (1,0,0)
extern const Vector VectorX;
/// (0,1,0)
extern const Vector VectorY;
/// (0,0,1)
extern const Vector VectorZ;
/// (0,0,0)
extern const Vector Vector0;
/// (1,1,1)
extern const Vector Vector1;

#endif 
