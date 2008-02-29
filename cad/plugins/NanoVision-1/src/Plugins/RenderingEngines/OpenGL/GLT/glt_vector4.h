#ifndef MATH_VECTOR4_H
#define MATH_VECTOR4_H

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
\brief   4D Vector
\ingroup Math
*/

#include <iosfwd>
#include <string>

#include "glt_config.h"
#include "glt_real.h"

////////////////////////// Vector4 /////////////////////////////////

/*! \class   Vector4 
\brief   4D Vector
\ingroup Math
*/

class Vector4
{
    friend std::ostream &operator<<(std::ostream &os, const Vector4 &x);
    friend std::istream &operator>>(std::istream &is,       Vector4 &x);
    
public:
    /// Default constructor
    Vector4();
    /// Copy constructor
    Vector4(const Vector4 &v);
    /// Constructor
    Vector4(const real x, const real y,const real z,const real w = 0.0);
    /// Constructor
    Vector4(const float  *v);
    /// Constructor
    Vector4(const double *v);
    /// Construct from string
    Vector4(const std::string &str);
    
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
    
    /// w co-ordinate
    real &w();
    /// w co-ordinate
    const real &w() const;
    
    /// i'th co-ordinate
    real &operator[](const int i);
    /// i'th co-ordinate
    const real &operator[](const int i) const;
    
    /// Access as array
    operator real* (void) { return _vector; }
    
    /// Access as array
    const real* data() const { return _vector; }
    
    void glLight(GLenum light, GLenum pname) const;
    
protected:
    /// Storage for x, y and z components
    real _vector[4];
};

#endif 
