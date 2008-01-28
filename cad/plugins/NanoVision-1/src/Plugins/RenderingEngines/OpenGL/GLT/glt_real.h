#ifndef MATH_REAL_H
#define MATH_REAL_H

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
    \brief   Numerical Constants
	\ingroup Math
*/

#include "glt_config.h"

#include <cfloat>
#include <cmath>

//
// Basic types, constants
// and functions
//

// Constants borrowed from PHP

#define M_PI		3.14159265358979323846
#define M_E			2.7182818284590452354
#define M_LOG2E		1.4426950408889634074
#define M_LOG10E    0.43429448190325182765
#define M_LN2		0.69314718055994530942
#define M_LN10		2.30258509299404568402
#define M_PI_2		1.57079632679489661923
#define M_PI_4		0.78539816339744830962
#define M_1_PI		0.31830988618379067154
#define M_2_PI		0.63661977236758134308

#ifndef M_SQRTPI
#define M_SQRTPI	1.77245385090551602729
#endif

#define M_2_SQRTPI	1.12837916709551257390
#define M_SQRT2		1.41421356237309504880

#ifndef M_SQRT3
#define M_SQRT3		1.73205080756887729352
#endif

#define M_SQRT1_2	0.70710678118654752440
#define M_LNPI		1.14472988584940017414
#define M_EULER		0.57721566490153286061

// Other useful constants

#define M_PI_DEG	(M_PI/180.0)
#define M_DEG_PI	(180.0/M_PI)
#define M_2PI       (2.0*M_PI)

/// Templated square: a^2
template <class A>				A SQ(A a) { return a*a; }

/// 
//template <class A, class B>		A SIGN(A a, B b) { return b<0?  -a: a; }

template <class A> bool SAME_SIGN(A a, A b) { return (a<0 && b<0   ||   a>0 && b>0); }
template <class A> A    CLAMP(const A x, const A min_v, const A max_v) { return x<min_v?  min_v: (x>max_v? max_v: x); }
template <class A> A    LERP(const A &a,const A &b,const double t)     { return a*(1.0-t) + b*t; }

//template <class A> const A &MIN(const A &a,const B &b) { return a<b ? a : b; }
//template <class A> const A &MAX(const A &a,const B &b) { return a>b ? a : b; }

//template <class A> const A &MIN(const A &a,const B &b,const C &c) { return a<b && a<c ? a : MIN(b,c); }
//template <class A> const A &MAX(const A &a,const B &b,const C &c) { return a>b && a>c ? a : MAX(b,c); }

#define MAX(x,y) (((x)>(y)) ? (x) : (y))
#define MIN(x,y) (((x)<(y)) ? (x) : (y))

#endif
