#ifndef MATH_MATRIX4_H
#define MATH_MATRIX4_H

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
    \brief   4x4 Matrix 
	\ingroup Math
*/

#include <iosfwd>

#if defined(__APPLE__)
#include <OpenGL/gl.h>
#else
#include <GL/gl.h>
#endif

#include "glt_real.h"
#include "glt_vector3.h"

////////////////////////// GltMatrix /////////////////////////////////

/*! \class   GltMatrix 
    \brief   4x4 Matrix
	\ingroup Math
	\author  Nigel Stewart, RMIT (nigels@nigels.com)
	\todo    Nice pictures and explanation for 4x4 transformation matrices.
*/

class GltUnMatrix;

class GltMatrix
{
	friend GltMatrix matrixScale(const double sf);
	friend GltMatrix matrixScale(const Vector sf);
	friend GltMatrix matrixTranslate(const Vector trans);
	friend GltMatrix matrixTranslate(const real x,const real y,const real z);
	friend GltMatrix matrixRotate(const Vector axis,const double angle);
	friend GltMatrix matrixRotate(const double azimuth,const double elevation);
	friend GltMatrix matrixOrient(const Vector &x,const Vector &y,const Vector &z);
	friend GltMatrix matrixOrient(const Vector &direction,const Vector &up);

	friend std::ostream &operator<<(std::ostream &os,const GltMatrix &m);
	friend std::istream &operator>>(std::istream &is,      GltMatrix &m);

public:

	/// Default constructor
	GltMatrix();
	/// Copy constructor
	GltMatrix(const GltMatrix &matrix);
	/// Construct from array 
	GltMatrix(const GLfloat *matrix);
	/// Construct from array 
	GltMatrix(const real *matrix);
	/// Construct from OpenGL GL_MODELVIEW_MATRIX or GL_PROJECTION_MATRIX
	GltMatrix(const unsigned int glMatrix);
	/// Construct from string
	GltMatrix(const std::string &str);
#if defined(__APPLE__)
	GltMatrix(GLenum glMatrixMode);
#endif

	/// Assignment operator
	GltMatrix &operator=(const GltMatrix &);

	/// GltMatrix multiplication
	GltMatrix  operator*(const GltMatrix &) const;
	/// In-place matrix multiplication
	GltMatrix &operator*=(const GltMatrix &);

	/// GltMatrix transformation of 3D vector
	Vector operator*(const Vector &) const;

	/// Reset to identity matrix
	void reset();
	/// Reset to identity matrix
	void identity();

	/// Is this matrix identity?
	bool isIdentity() const;

    /// Access i'th row, j'th column element
    real& operator () (int i, int j) { return element(j, i); }
    real const& operator () (int i, int j) const { return get(j, i); }
    
	/// Access i'th element of matrix
	real &operator[](const int i);
	/// Access i'th element of matrix
	const real &operator[](const int i) const;

	/// Access as array
	operator real * ();
	/// Access as array
	operator const double * () const;

	/// Equality operator
	bool operator==(const GltMatrix &) const;
	/// Not-equal operator
	bool operator!=(const GltMatrix &) const;

	/// Calculate matrix inverse
	GltMatrix inverse() const;
	/// Calculate matrix transpose
	GltMatrix transpose() const;
	/// Calculate unmatrix
	GltUnMatrix unmatrix() const;
	/// Calculate matrix determinant
	double det() const;

	/// Mult current OpenGL matrix 
	void glMultMatrix() const;
	/// Load current OpenGL matrix
	void glLoadMatrix() const;

    /// set to current model-view or projection matrix
    void glGet(GLenum glMatrixMode);
    
    /// set current modelview or projection matrix
    void glSet(GLenum glMatrixMode);
    
    /// Is this an orthographic projection matrix?
    bool isOrtho() const;
    
    /// Is this a perspective projection matrix?
    bool isPerspective() const;
    
    /// Write matrix in Povray format
	std::ostream &writePov(std::ostream &os) const;

private:

	real _matrix[16];
	static real _identity[16];

	inline void set(const int col,const int row,const real& val) 
	{ 
		_matrix[col*4+row] = val;
	}

	inline real const& get(const int col,const int row) const
	{
		return _matrix[col*4+row];
	}

	inline real& element(const int col,const int row) 
	{
		return _matrix[col*4+row];
	}

	// From Mesa-2.2\src\glu\project.c

	static void invertMatrixGeneral( const double *m, double *out );
	static void invertMatrix( const double *m, double *out );

	// From Graphics Gems GEMSI\MATINV.C

	double 
	det3x3
	( 
		const double a1, 
		const double a2, 
		const double a3, 
		const double b1, 
		const double b2, 
		const double b3, 
		const double c1, 
		const double c2, 
		const double c3 
	) const;

	double
	det2x2
	( 
		const double a, 
		const double b, 
		const double c, 
		const double d
	) const;
};

#endif
