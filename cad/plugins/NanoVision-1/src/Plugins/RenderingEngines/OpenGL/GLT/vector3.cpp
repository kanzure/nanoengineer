#include "glt_vector3.h"

/*! \file 
	\ingroup Math
*/

#include "glt_matrix4.h"

#include "glt_gl.h"
#include "glt_glu.h"
#include "glt_viewport.h"

#include "glt_string.h"
#include <cassert>
#include <cmath>

#include <iostream>
#include <algorithm>
using namespace std;

const Vector VectorX(1.0,0.0,0.0);
const Vector VectorY(0.0,1.0,0.0);
const Vector VectorZ(0.0,0.0,1.0);
const Vector Vector0(0.0,0.0,0.0);
const Vector Vector1(1.0,1.0,1.0);

Vector::Vector()
{
	_vector[0] = _vector[1] = _vector[2] = 0.0;
}

Vector::Vector(const Vector &v)
{
	_vector[0] = v._vector[0];
	_vector[1] = v._vector[1];
	_vector[2] = v._vector[2];
}

Vector::Vector(const real x, const real y, const real z)
{
	_vector[0] = x;
	_vector[1] = y;
	_vector[2] = z;
}

Vector::Vector(const float *v)
{
	_vector[0] = v[0];
	_vector[1] = v[1];
	_vector[2] = v[2];
}

Vector::Vector(const double *v)
{
	_vector[0] = v[0];
	_vector[1] = v[1];
	_vector[2] = v[2];
}

Vector::Vector(const string &str)
{
	#ifndef NDEBUG
	const int n = 
	#endif
		atoc(str,atof,"+-eE.0123456789",_vector+0,_vector+3);
		
	assert(n==3);
}

const real &
Vector::operator[](const int i) const
{
	assert(i>=0 && i<3);
	return _vector[i];
}

real &
Vector::operator[](const int i)
{
	assert(i>=0 && i<3);
	return _vector[i];
}

// Vector::operator real* (void)
// {
// 	return (real *) _vector;
// }

      real &Vector::x()       { return _vector[0]; }
const real &Vector::x() const { return _vector[0]; }
      real &Vector::y()       { return _vector[1]; }
const real &Vector::y() const { return _vector[1]; }
      real &Vector::z()       { return _vector[2]; }
const real &Vector::z() const { return _vector[2]; }

bool
Vector::operator==(const Vector &v) const
{
	return 
		_vector[0] == v[0] &&
		_vector[1] == v[1] &&
		_vector[2] == v[2];
}

bool 
Vector::operator!=(const Vector &v) const
{
	return 
		_vector[0] != v[0] ||
		_vector[1] != v[1] ||
		_vector[2] != v[2];
}

bool
Vector::operator==(const real &a) const
{
	return 
		_vector[0] == a &&
		_vector[1] == a &&
		_vector[2] == a;
}

bool 
Vector::operator< (const Vector &v) const
{
	if (x()!=v.x()) return x()<v.x();
	if (y()!=v.y()) return y()<v.y();
	return z()<v.z();
}

bool 
Vector::operator> (const Vector &v) const
{
	if (x()!=v.x()) return x()>v.x();
	if (y()!=v.y()) return y()>v.y();
	return z()>v.z();
}

ostream &
Vector::writePov(ostream &os) const
{
	os << "< ";
	os << x() << ',';
	os << y() << ',';
	os << z() << " >";

	return os;
}

Vector
Vector::operator-() const
{
	return Vector(-_vector[0], -_vector[1], -_vector[2]);
}

void 
Vector::scale(const real &x)
{
	_vector[0] *= x;
	_vector[1] *= x;
	_vector[2] *= x;
}

void 
Vector::scale(const Vector &x)
{
	_vector[0] *= x._vector[0];
	_vector[1] *= x._vector[1];
	_vector[2] *= x._vector[2];
}

void
Vector::normalize()
{
	const real mag = sqrt(norm());

	if (mag == 0.0)
		return;

	const real magInv = 1.0/mag;

	_vector[0] *= magInv;
	_vector[1] *= magInv;
	_vector[2] *= magInv;
}

void 
Vector::abs()
{
	_vector[0] = fabs(_vector[0]);
	_vector[1] = fabs(_vector[1]);
	_vector[2] = fabs(_vector[2]);
}

int
Vector::dominant() const
{
	const real x = fabs(_vector[0]);
	const real y = fabs(_vector[1]);
	const real z = fabs(_vector[2]);

	if (x>y && x>z)
		return 0;
	else
		if (y>z)
			return 1;
		else
			return 2;
}

real
Vector::norm() const
{
	return ((*this)*(*this));
}

real
Vector::length() const
{
	return sqrt((*this)*(*this));
}

bool
Vector::project(const GltMatrix &model,const GltMatrix &proj,const GltViewport &view)
{
	// TODO - No need to copy from x,y,z if real is GLdouble
	
	GLdouble x,y,z;
	GLint ret = gluProject(_vector[0],_vector[1],_vector[2],model,proj,view,&x,&y,&z);

	_vector[0] = x;
	_vector[1] = y;
	_vector[2] = z;

	return ret==GL_TRUE;
}

Vector &
Vector::operator=(const Vector &x)
{
	_vector[0] = x[0];
	_vector[1] = x[1];
	_vector[2] = x[2];

	return *this;
}

Vector &
Vector::operator=(const float *x)
{
	_vector[0] = x[0];
	_vector[1] = x[1];
	_vector[2] = x[2];

	return *this;
}

Vector &
Vector::operator=(const double *x)
{
	_vector[0] = x[0];
	_vector[1] = x[1];
	_vector[2] = x[2];

	return *this;
}

real
Vector::operator*(const Vector &x) const
{
	return _vector[0]*x[0] + _vector[1]*x[1] + _vector[2]*x[2];
}

Vector & 
Vector::operator+=(const Vector &v)
{
	_vector[0] += v[0];
	_vector[1] += v[1];
	_vector[2] += v[2];

	return *this;
}

Vector & 
Vector::operator-=(const Vector &x)
{
	_vector[0] -= x[0];
	_vector[1] -= x[1];
	_vector[2] -= x[2];

	return *this;
}

Vector &
Vector::operator*=(const real &x)
{
	_vector[0] *= x;
	_vector[1] *= x;
	_vector[2] *= x;

	return *this;
}

Vector &
Vector::operator*=(const GltMatrix &m)
{
	return operator=(m*(*this));
}

real
Vector::dist(const Vector &x) const
{
	return ((*this)-x).norm();
}

Vector &
Vector::vmin(const Vector &v)
{
	_vector[0] = MIN(_vector[0],v[0]);
	_vector[1] = MIN(_vector[1],v[1]);
	_vector[2] = MIN(_vector[2],v[2]);
	return *this;
}

Vector &
Vector::vmax(const Vector &v)
{
	_vector[0] = MAX(_vector[0],v[0]);
	_vector[1] = MAX(_vector[1],v[1]);
	_vector[2] = MAX(_vector[2],v[2]);
	return *this;
}

/////////////////////////
//
// OpenGL

#include "glt_gl.h"

void
Vector::glVertex() const
{
	#ifdef GLT_FAST_FLOAT
	glVertex3fv(_vector);
	#else
	glVertex3dv(_vector);
	#endif
}

void
Vector::glNormal() const
{
	#ifdef GLT_FAST_FLOAT
	glNormal3fv(_vector);
	#else
	glNormal3dv(_vector);
	#endif
}

void
Vector::glColor() const
{
	#ifdef GLT_FAST_FLOAT
	glColor3fv(_vector);
	#else
	glColor3dv(_vector);
	#endif
}

void
Vector::glTexCoord() const
{
	#ifdef GLT_FAST_FLOAT
	glTexCoord3fv(_vector);
	#else
	glTexCoord3dv(_vector);
	#endif
}

void
Vector::glLight(GLenum light, GLenum pname) const
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
operator<<(ostream &os, const Vector &x)
{
	os << x[0] << '\t';
	os << x[1] << '\t';
	os << x[2];

	return os;
}

/*!
	\brief Input vector from stream
	\ingroup Math
*/

istream &
operator>>(istream &is, Vector &x)
{
	is >> x[0];
	is >> x[1];
	is >> x[2];

	return is;
}

/*!
	\brief Vector scale
	\ingroup Math
*/

Vector
operator*(const real x, const Vector &v)
{
	return v*x;
}

/*!
	\brief Vector scale
	\ingroup Math
*/

Vector
operator*(const Vector &v, const real x)
{
	return Vector( x*v._vector[0], x*v._vector[1], x*v._vector[2]);
}

/*!
	\brief Vector inverse scale
	\ingroup Math
*/

Vector
operator/(const Vector &v, const real x)
{
	assert(x != 0.0);
	const real inv = 1.0/x;
	return v*inv;
}

/*!
	\brief Vector addition
	\ingroup Math
*/

Vector
operator+(const Vector &v1, const Vector &v2)
{
	return Vector(v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]);
}

/*!
	\brief Vector difference
	\ingroup Math
*/

Vector
operator-(const Vector &v1, const Vector &v2)
{
	return Vector(v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]);
}

/*!
	\brief Vector cross product
	\ingroup Math
*/

Vector 
xProduct(const Vector &v1, const Vector &v2)
{
	return Vector(v1[1]*v2[2] - v1[2]*v2[1],
				  v1[2]*v2[0] - v1[0]*v2[2],
				  v1[0]*v2[1] - v1[1]*v2[0]);
}

/*!
	\brief Calculate normal from three points in plane
	\ingroup Math
*/

Vector 
planeNormal(const Vector &v1, const Vector &v2,const Vector &v3)
{
	return xProduct(v2-v1,v3-v1);
}

/*!
	\brief Location on unit sphere
	\ingroup Math
*/

Vector 
polar(const real lat,const real longitude)
{
	return 
		Vector(
			cos(lat*M_PI_DEG) * cos(longitude*M_PI_DEG),
			sin(lat*M_PI_DEG),
			cos(lat*M_PI_DEG) * sin(longitude*M_PI_DEG)
		);
}

/*!
	\brief Create orthogonal co-ordinate system, based on a
	\ingroup Math
*/

void orthogonalSystem(Vector &a,Vector &b,Vector &c)
{
	a.normalize();

	if (fabs(a.z())>0.8)
	{
		b = xProduct(a,VectorY);
		c = xProduct(a,b);
	}
	else
	{
		b = xProduct(a,VectorZ);
		c = xProduct(a,b);
	}
	
	b.normalize();
	c.normalize();
}



