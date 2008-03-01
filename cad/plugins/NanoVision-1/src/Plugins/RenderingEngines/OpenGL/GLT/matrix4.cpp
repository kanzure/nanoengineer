#include "glt_matrix4.h"

/*! \file 
	\ingroup Math
*/

#include <cmath>
#include <cassert>
#include <string>
#include <iostream>
#include <iomanip>
using namespace std;

#include "glt_gl.h"

#include "glt_string.h"
#include "glt_umatrix.h"

double GltMatrix::_identity[16] = 
{
   1.0, 0.0, 0.0, 0.0,
   0.0, 1.0, 0.0, 0.0,
   0.0, 0.0, 1.0, 0.0,
   0.0, 0.0, 0.0, 1.0
};

GltMatrix::GltMatrix()
{
	reset();
}

GltMatrix::GltMatrix(const GltMatrix &matrix)
{
	(*this) = matrix;
}

GltMatrix::GltMatrix(const float *matrix)
{
	      real  *i = _matrix;
	const float *j =  matrix;
	for (int k=0; k<16; i++,j++,k++)
        *i = (real) *j;
}

GltMatrix::GltMatrix(const double *matrix)
{
	      real   *i = _matrix;
	const double *j =  matrix;
	for (int k=0; k<16; i++,j++,k++)
        *i = (real) *j;
}

GltMatrix::GltMatrix(GLenum glMatrixMode)
{
    glGet(glMatrixMode);
}

GltMatrix::GltMatrix(const string &str)
{
	#ifndef NDEBUG
	const int n = 
	#endif
		atoc(str,atof,"+-eE.0123456789",_matrix+0,_matrix+16);
		
	assert(n==16);
}

GltMatrix &
GltMatrix::operator=(const GltMatrix &m)
{
	memcpy(_matrix,m._matrix,sizeof(_matrix));

	return *this;
}

GltMatrix 
GltMatrix::operator *(const GltMatrix &m) const
{
	GltMatrix prod;

	for (int c=0;c<4;c++)
		for (int r=0;r<4;r++)
			prod.set(c,r,
				get(c,0)*m.get(0,r) +
				get(c,1)*m.get(1,r) +
				get(c,2)*m.get(2,r) +
				get(c,3)*m.get(3,r));

	return prod;
}

GltMatrix &
GltMatrix::operator*=(const GltMatrix &m)
{
	// Potential optimisation here to
	// skip a temporary copy

	return (*this) = (*this)*m;
}

Vector    
GltMatrix::operator*(const Vector &v) const
{
	double prod[4] = { 0,0,0,0 };

	for (int r=0;r<4;r++)
	{
		for (int c=0;c<3;c++)
			prod[r] += v[c]*get(c,r);

		prod[r] += get(3,r);
	}

	double div = 1.0 / prod[3];

	return Vector(prod[0]*div,prod[1]*div,prod[2]*div);
}

void 
GltMatrix::reset()
{
	memcpy(_matrix,_identity,16*sizeof(double));
}

void 
GltMatrix::identity()
{
	reset();
}

bool 
GltMatrix::isIdentity() const
{
	return !memcmp(_matrix,_identity,sizeof(_matrix));
}

const double & 
GltMatrix::operator[](const int i) const
{
	assert(i>=0 && i<16);
	return _matrix[i];
}

double & 
GltMatrix::operator[](const int i)
{
	assert(i>=0 && i<16);
	return _matrix[i];
}

bool 
GltMatrix::operator==(const GltMatrix &m) const
{
	return !memcmp(_matrix,m._matrix,sizeof(_matrix));
}

bool 
GltMatrix::operator!=(const GltMatrix &m) const
{
	return memcmp(_matrix,m._matrix,sizeof(_matrix))!=0;
}

GltMatrix::operator real *()
{
	return _matrix;
}

GltMatrix::operator const real *() const
{
	return _matrix;
}

void
GltMatrix::glMultMatrix() const
{
    switch(sizeof(real)) {
    case sizeof(GLfloat): glMultMatrixf((GLfloat*)_matrix); break;
    case sizeof(GLdouble): glMultMatrixd((GLdouble*)_matrix); break;
    }
}

void 
GltMatrix::glLoadMatrix() const
{
    switch(sizeof(real)) {
    case sizeof(GLfloat): glLoadMatrixf((GLfloat*)_matrix); break;
    case sizeof(GLdouble): glLoadMatrixd((GLdouble*)_matrix); break;
    }
}


void GltMatrix::glGet(GLenum matrixMode)
{
    switch (matrixMode)
    {
    case GL_MODELVIEW:
        if(sizeof(real)==sizeof(GLfloat))
            glGetFloatv(GL_MODELVIEW_MATRIX, (GLfloat*)_matrix);
        else if(sizeof(real)==sizeof(GLdouble))
            glGetDoublev(GL_MODELVIEW_MATRIX, (GLdouble*)_matrix);
        break;
    case GL_PROJECTION:
        if(sizeof(real)==sizeof(GLfloat))
            glGetFloatv(GL_PROJECTION_MATRIX, (GLfloat*)_matrix);
        else if(sizeof(real)==sizeof(GLdouble))
            glGetDoublev(GL_PROJECTION_MATRIX, (GLdouble*)_matrix);
        break;
    }
}


void GltMatrix::glSet(GLenum matrixMode)
{
    switch(matrixMode) {
    case GL_MODELVIEW:
    case GL_PROJECTION:
        glMatrixMode(matrixMode);
        if(sizeof(real)==sizeof(GLfloat))
            glLoadMatrixf((GLfloat*)_matrix);
        else if(sizeof(real)==sizeof(GLdouble))
            glLoadMatrixd((GLdouble*)_matrix);
        break;
    default:
        break;
    }
}


bool GltMatrix::isOrtho() const
{
    bool diagonalsNonZero = (_matrix[0] != 0.0 &&
                             _matrix[5] != 0.0 &&
                             _matrix[10] != 0.0 &&
                             _matrix[15] == 1.0);
    bool offDiagonals3x3Zero = (_matrix[1] == 0.0 &&
                                _matrix[2] == 0.0 &&
                                _matrix[3] == 0.0 &&
                                _matrix[4] == 0.0 &&
                                _matrix[6] == 0.0 &&
                                _matrix[7] == 0.0 &&
                                _matrix[8] == 0.0 &&
                                _matrix[9] == 0.0 &&
                                _matrix[11] == 0.0);
    bool lastColumn3NonZero = (_matrix[12] != 0.0 &&
                               _matrix[13] != 0.0 &&
                               _matrix[14] != 0.0);
    bool result = diagonalsNonZero && offDiagonals3x3Zero && lastColumn3NonZero;
    return result;
}


bool GltMatrix::isPerspective() const
{
    bool col0 = (_matrix[0] != 0.0 &&
                 _matrix[1] == 0.0 &&
                 _matrix[2] == 0.0 &&
                 _matrix[3] == 0.0);
    bool col1 = (_matrix[4] == 0.0 &&
                 _matrix[5] != 0.0 &&
                 _matrix[6] == 0.0 &&
                 _matrix[7] == 0.0);
    bool col2 = (_matrix[8] != 0.0 &&
                 _matrix[9] != 0.0 &&
                 _matrix[10] != 0.0 &&
                 _matrix[11] == -1.0);
    bool col3 = (_matrix[12] == 0.0 &&
                 _matrix[13] == 0.0 &&
                 _matrix[14] != 0.0 &&
                 _matrix[15] == 0.0);
    bool result = col0 && col1 && col2 && col3;
    return result;
}


#if 0
double const *
GltMatrix::row(const unsigned int row) const
{
	static double r[4];

	for (int c=0;c<4;c++)
		r[c] = _matrix[c*4+row];
	
	return r;
}

double const *
GltMatrix::column(const unsigned int column) const
{
	return _matrix+column*4;
}

#endif

ostream &
GltMatrix::writePov(ostream &os) const
{
	GltUnMatrix um = unmatrix();

	os << "scale < ";
	  os << um[U_SCALEX] << ',';
	  os << um[U_SCALEY] << ',';
	  os << um[U_SCALEZ] << " > ";

  	os << "rotate < ";
	  os << um[U_ROTATEX]/M_PI_DEG << ',';
	  os << um[U_ROTATEY]/M_PI_DEG << ',';
	  os << um[U_ROTATEZ]/M_PI_DEG << " > ";

  	os << "translate < ";
	  os << um[U_TRANSX] << ',';
	  os << um[U_TRANSY] << ',';
	  os << um[U_TRANSZ] << " > ";

	return os;
}

/*! 
	\brief		Uniform scale transformation matrix
	\ingroup	Math
*/

GltMatrix matrixScale(const double sf)
{
	GltMatrix scale;

	scale.set(0,0,sf);
	scale.set(1,1,sf);
	scale.set(2,2,sf);
	
	return scale;
}

/*! 
	\brief		Non-uniform scale transformation matrix
	\ingroup	Math
*/

GltMatrix matrixScale(const Vector sf)
{
	GltMatrix scale;

	scale.set(0,0,sf[0]);
	scale.set(1,1,sf[1]);
	scale.set(2,2,sf[2]);
	
	return scale;
}

/*! 
	\brief		Translation transformation matrix
	\ingroup	Math
*/

GltMatrix matrixTranslate(const Vector trans)
{
	GltMatrix translate;

	translate.set(3,0,trans[0]);
	translate.set(3,1,trans[1]);
	translate.set(3,2,trans[2]);

	return translate;
}

/*! 
	\brief		Translation transformation matrix
	\ingroup	Math
*/

GltMatrix matrixTranslate(const real x,const real y,const real z)
{
	GltMatrix translate;

	translate.set(3,0,x);
	translate.set(3,1,y);
	translate.set(3,2,z);

	return translate;
}

/*! 
	\brief		Axis rotation transformation matrix
	\ingroup	Math
	\param      axis	Axis of rotation
	\param		angle	Angle in degrees
*/

GltMatrix matrixRotate(const Vector axis, const double angle)
{
	GltMatrix rotate;

	// Page 466, Graphics Gems

	double s = sin(angle*M_PI_DEG);
	double c = cos(angle*M_PI_DEG);
	double t = 1 - c;

	Vector ax = axis/sqrt(axis.norm());

	double x = ax[0];
	double y = ax[1];
	double z = ax[2];

	rotate.set(0,0,t*x*x+c);
	rotate.set(1,0,t*y*x+s*z);
	rotate.set(2,0,t*z*x-s*y);

	rotate.set(0,1,t*x*y-s*z);
	rotate.set(1,1,t*y*y+c);
	rotate.set(2,1,t*z*y+s*x);

	rotate.set(0,2,t*x*z+s*y);
	rotate.set(1,2,t*y*z-s*x);
	rotate.set(2,2,t*z*z+c);

	return rotate;
}

/*! 
	\brief		Rotation transformation matrix
	\ingroup	Math
	\param      azimuth		East-West degrees
	\param		elevation	North-South degrees
*/

GltMatrix matrixRotate(const double azimuth, const double elevation)
{
	GltMatrix rotate;

	double ca = cos(azimuth*M_PI_DEG);
	double sa = sin(azimuth*M_PI_DEG);
	double cb = cos(elevation*M_PI_DEG);
	double sb = sin(elevation*M_PI_DEG);

	rotate.set(0,0,cb);
	rotate.set(1,0,0);
	rotate.set(2,0,-sb);

	rotate.set(0,1,-sa*sb);
	rotate.set(1,1,ca);
	rotate.set(2,1,-sa*cb);

	rotate.set(0,2,ca*sb);
	rotate.set(1,2,sa);
	rotate.set(2,2,ca*cb);

	return rotate;
}

/*! 
	\brief		Orientation transformation matrix
	\ingroup	Math
	\param      x	New orientation for +x
	\param		y	New orientation for +y
	\param		z	New orientation for +z
*/

GltMatrix matrixOrient(const Vector &x,const Vector &y,const Vector &z)
{
	GltMatrix orient;

	orient.set(0,0,x.x());
	orient.set(0,1,x.y());
	orient.set(0,2,x.z());

	orient.set(1,0,y.x());
	orient.set(1,1,y.y());
	orient.set(1,2,y.z());

	orient.set(2,0,z.x());
	orient.set(2,1,z.y());
	orient.set(2,2,z.z());

	return orient;
}

/*! 
	\brief		Orientation transformation matrix
	\ingroup	Math
	\param      direction	New orientation for +z
	\param      up          New orientation for +y
*/

GltMatrix matrixOrient(const Vector &direction,const Vector &up)
{
	assert(direction.norm()>0.0);
	assert(up.norm()>0.0);

	Vector d(direction);
	d.normalize();

	Vector u(up);
	u.normalize();

	return matrixOrient(xProduct(u,d),u,d);
}

/*! 
	\brief		Write a matrix to a text output stream
	\ingroup	Math
*/

std::ostream &
operator<<(std::ostream &os,const GltMatrix &m)
{
	for (int r=0;r<4;r++)
		for (int c=0;c<4;c++)
			os << setw(10) << setfill(' ') << m.get(c,r) << ( c==3 ? '\n' : '\t');

	return os;
}

/*! 
	\brief		Read a matrix from a text output stream
	\ingroup	Math
*/

std::istream &
operator>>(std::istream &is,GltMatrix &m)
{
	for (int r=0;r<4;r++)
		for (int c=0;c<4;c++)
		{
			double tmp;
			is >> tmp;
			m.set(c,r,tmp);
		}

	return is;
}

GltMatrix 
GltMatrix::inverse() const
{
	GltMatrix inv;
	invertMatrix(_matrix,inv._matrix);
	return inv;
}

GltMatrix 
GltMatrix::transpose() const
{
	GltMatrix tmp;
	
	for (int i=0;i<4;i++)
		for (int j=0;j<4;j++)
			tmp.set(j,i,get(i,j));
	
	return tmp;
}

//
// From Mesa-2.2\src\glu\project.c
//

//
// Compute the inverse of a 4x4 matrix.  Contributed by scotter@lafn.org
//

void 
GltMatrix::invertMatrixGeneral( const double *m, double *out )
{

/* NB. OpenGL Matrices are COLUMN major. */
#define MAT(m,r,c) (m)[(c)*4+(r)]

/* Here's some shorthand converting standard (row,column) to index. */
#define m11 MAT(m,0,0)
#define m12 MAT(m,0,1)
#define m13 MAT(m,0,2)
#define m14 MAT(m,0,3)
#define m21 MAT(m,1,0)
#define m22 MAT(m,1,1)
#define m23 MAT(m,1,2)
#define m24 MAT(m,1,3)
#define m31 MAT(m,2,0)
#define m32 MAT(m,2,1)
#define m33 MAT(m,2,2)
#define m34 MAT(m,2,3)
#define m41 MAT(m,3,0)
#define m42 MAT(m,3,1)
#define m43 MAT(m,3,2)
#define m44 MAT(m,3,3)

   double det;
   double d12, d13, d23, d24, d34, d41;
   double tmp[16]; /* Allow out == in. */

   /* Inverse = adjoint / det. (See linear algebra texts.)*/

   /* pre-compute 2x2 dets for last two rows when computing */
   /* cofactors of first two rows. */
   d12 = (m31*m42-m41*m32);
   d13 = (m31*m43-m41*m33);
   d23 = (m32*m43-m42*m33);
   d24 = (m32*m44-m42*m34);
   d34 = (m33*m44-m43*m34);
   d41 = (m34*m41-m44*m31);

   tmp[0] =  (m22 * d34 - m23 * d24 + m24 * d23);
   tmp[1] = -(m21 * d34 + m23 * d41 + m24 * d13);
   tmp[2] =  (m21 * d24 + m22 * d41 + m24 * d12);
   tmp[3] = -(m21 * d23 - m22 * d13 + m23 * d12);

   /* Compute determinant as early as possible using these cofactors. */
   det = m11 * tmp[0] + m12 * tmp[1] + m13 * tmp[2] + m14 * tmp[3];

   /* Run singularity test. */
   if (det == 0.0) {
      /* printf("invert_matrix: Warning: Singular matrix.\n"); */
	  memcpy(out,_identity,16*sizeof(double));
   }
   else {
      double invDet = 1.0 / det;
      /* Compute rest of inverse. */
      tmp[0] *= invDet;
      tmp[1] *= invDet;
      tmp[2] *= invDet;
      tmp[3] *= invDet;

      tmp[4] = -(m12 * d34 - m13 * d24 + m14 * d23) * invDet;
      tmp[5] =  (m11 * d34 + m13 * d41 + m14 * d13) * invDet;
      tmp[6] = -(m11 * d24 + m12 * d41 + m14 * d12) * invDet;
      tmp[7] =  (m11 * d23 - m12 * d13 + m13 * d12) * invDet;

      /* Pre-compute 2x2 dets for first two rows when computing */
      /* cofactors of last two rows. */
      d12 = m11*m22-m21*m12;
      d13 = m11*m23-m21*m13;
      d23 = m12*m23-m22*m13;
      d24 = m12*m24-m22*m14;
      d34 = m13*m24-m23*m14;
      d41 = m14*m21-m24*m11;

      tmp[8] =  (m42 * d34 - m43 * d24 + m44 * d23) * invDet;
      tmp[9] = -(m41 * d34 + m43 * d41 + m44 * d13) * invDet;
      tmp[10] =  (m41 * d24 + m42 * d41 + m44 * d12) * invDet;
      tmp[11] = -(m41 * d23 - m42 * d13 + m43 * d12) * invDet;
      tmp[12] = -(m32 * d34 - m33 * d24 + m34 * d23) * invDet;
      tmp[13] =  (m31 * d34 + m33 * d41 + m34 * d13) * invDet;
      tmp[14] = -(m31 * d24 + m32 * d41 + m34 * d12) * invDet;
      tmp[15] =  (m31 * d23 - m32 * d13 + m33 * d12) * invDet;

      memcpy(out, tmp, 16*sizeof(double));
   }

#undef m11
#undef m12
#undef m13
#undef m14
#undef m21
#undef m22
#undef m23
#undef m24
#undef m31
#undef m32
#undef m33
#undef m34
#undef m41
#undef m42
#undef m43
#undef m44
#undef MAT
}


//
// Invert matrix m.  This algorithm contributed by Stephane Rehel
// <rehel@worldnet.fr>
//

void 
GltMatrix::invertMatrix( const double *m, double *out )
{
/* NB. OpenGL Matrices are COLUMN major. */
#define MAT(m,r,c) (m)[(c)*4+(r)]

/* Here's some shorthand converting standard (row,column) to index. */
#define m11 MAT(m,0,0)
#define m12 MAT(m,0,1)
#define m13 MAT(m,0,2)
#define m14 MAT(m,0,3)
#define m21 MAT(m,1,0)
#define m22 MAT(m,1,1)
#define m23 MAT(m,1,2)
#define m24 MAT(m,1,3)
#define m31 MAT(m,2,0)
#define m32 MAT(m,2,1)
#define m33 MAT(m,2,2)
#define m34 MAT(m,2,3)
#define m41 MAT(m,3,0)
#define m42 MAT(m,3,1)
#define m43 MAT(m,3,2)
#define m44 MAT(m,3,3)

   register double det;
   double tmp[16]; /* Allow out == in. */

   if( m41 != 0. || m42 != 0. || m43 != 0. || m44 != 1. ) {
      invertMatrixGeneral(m, out);
      return;
   }

   /* Inverse = adjoint / det. (See linear algebra texts.)*/

   tmp[0]= m22 * m33 - m23 * m32;
   tmp[1]= m23 * m31 - m21 * m33;
   tmp[2]= m21 * m32 - m22 * m31;

   /* Compute determinant as early as possible using these cofactors. */
   det= m11 * tmp[0] + m12 * tmp[1] + m13 * tmp[2];

   /* Run singularity test. */
   if (det == 0.0) {
      /* printf("invert_matrix: Warning: Singular matrix.\n"); */
      memcpy( out, _identity, 16*sizeof(double) );
   }
   else {
      double d12, d13, d23, d24, d34, d41;
      register double im11, im12, im13, im14;

      det= 1. / det;

      /* Compute rest of inverse. */
      tmp[0] *= det;
      tmp[1] *= det;
      tmp[2] *= det;
      tmp[3]  = 0.;

      im11= m11 * det;
      im12= m12 * det;
      im13= m13 * det;
      im14= m14 * det;
      tmp[4] = im13 * m32 - im12 * m33;
      tmp[5] = im11 * m33 - im13 * m31;
      tmp[6] = im12 * m31 - im11 * m32;
      tmp[7] = 0.;

      /* Pre-compute 2x2 dets for first two rows when computing */
      /* cofactors of last two rows. */
      d12 = im11*m22 - m21*im12;
      d13 = im11*m23 - m21*im13;
      d23 = im12*m23 - m22*im13;
      d24 = im12*m24 - m22*im14;
      d34 = im13*m24 - m23*im14;
      d41 = im14*m21 - m24*im11;

      tmp[8] =  d23;
      tmp[9] = -d13;
      tmp[10] = d12;
      tmp[11] = 0.;

      tmp[12] = -(m32 * d34 - m33 * d24 + m34 * d23);
      tmp[13] =  (m31 * d34 + m33 * d41 + m34 * d13);
      tmp[14] = -(m31 * d24 + m32 * d41 + m34 * d12);
      tmp[15] =  1.;

      memcpy(out, tmp, 16*sizeof(double));
  }

#undef m11
#undef m12
#undef m13
#undef m14
#undef m21
#undef m22
#undef m23
#undef m24
#undef m31
#undef m32
#undef m33
#undef m34
#undef m41
#undef m42
#undef m43
#undef m44
#undef MAT
}
