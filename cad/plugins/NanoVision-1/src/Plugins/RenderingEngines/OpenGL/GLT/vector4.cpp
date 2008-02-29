#include "glt_vector4.h"

/*! \file 
	\ingroup Math
*/

#include "glt_string.h"

#include <cassert>
#include <cmath>

#include <iostream>
#include <algorithm>
using namespace std;

Vector4::Vector4()
{
	_vector[0] = _vector[1] = _vector[2] = _vector[3] = 0.0;
}

Vector4::Vector4(const Vector4 &v)
{
	_vector[0] = v._vector[0];
	_vector[1] = v._vector[1];
	_vector[2] = v._vector[2];
	_vector[3] = v._vector[3];
}

Vector4::Vector4(const real x, const real y, const real z,const real w)
{
	_vector[0] = x;
	_vector[1] = y;
	_vector[2] = z;
	_vector[3] = w;
}

Vector4::Vector4(const float *v)
{
	_vector[0] = v[0];
	_vector[1] = v[1];
	_vector[2] = v[2];
	_vector[3] = v[3];
}

Vector4::Vector4(const double *v)
{
	_vector[0] = v[0];
	_vector[1] = v[1];
	_vector[2] = v[2];
	_vector[3] = v[3];
}

Vector4::Vector4(const string &str)
{
	#ifndef NDEBUG
	const int n = 
	#endif
		atoc(str,atof,"+-eE.0123456789",_vector+0,_vector+4);
		
	assert(n==4);
}

const real &
Vector4::operator[](const int i) const
{
	assert(i>=0 && i<4);
	return _vector[i];
}

real &
Vector4::operator[](const int i)
{
	assert(i>=0 && i<4);
	return _vector[i];
}

// Vector4::operator real*  (void)
// {
// 	return (real *) _vector;
// }

      real &Vector4::x()       { return _vector[0]; }
const real &Vector4::x() const { return _vector[0]; }
      real &Vector4::y()       { return _vector[1]; }
const real &Vector4::y() const { return _vector[1]; }
      real &Vector4::z()       { return _vector[2]; }
const real &Vector4::z() const { return _vector[2]; }
      real &Vector4::w()       { return _vector[3]; }
const real &Vector4::w() const { return _vector[3]; }


void
Vector4::glLight(GLenum light, GLenum pname) const
{
#ifdef GLT_FAST_FLOAT
    glLightfv(light, pname, _vector);
#else
    GLfloat params[4];
    params[0] = _vector[0];
    params[1] = _vector[1];
    params[2] = _vector[2];
    params[3] = _vector[3];
    glLightfv(light, pname, params);
#endif
}

////////////////////////// F R I E N D S

/*!
	\brief Output vector to stream
	\ingroup Math
*/

ostream &
operator<<(ostream &os, const Vector4 &x)
{
	os << x[0] << '\t';
	os << x[1] << '\t';
	os << x[2] << '\t';
	os << x[3];

	return os;
}

/*!
	\brief Input vector from stream
	\ingroup Math
*/

istream &
operator>>(istream &is, Vector4 &x)
{
	is >> x[0];
	is >> x[1];
	is >> x[2];
	is >> x[3];

	return is;
}

