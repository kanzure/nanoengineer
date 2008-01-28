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

#include <math/real.h>
#include <math/vector3.h>

////////////////////////// Matrix /////////////////////////////////

/*! \class   Matrix 
    \brief   4x4 Matrix
	\ingroup Math
	\author  Nigel Stewart, RMIT (nigels@nigels.com)
	\todo    Nice pictures and explanation for 4x4 transformation matrices.
*/

class UnMatrix;

class Matrix
{
	friend Matrix matrixScale(const double sf);
	friend Matrix matrixScale(const Vector sf);
	friend Matrix matrixTranslate(const Vector trans);
	friend Matrix matrixTranslate(const real x,const real y,const real z);
	friend Matrix matrixRotate(const Vector axis,const double angle);
	friend Matrix matrixRotate(const double azimuth,const double elevation);
	friend Matrix matrixOrient(const Vector &x,const Vector &y,const Vector &z);
	friend Matrix matrixOrient(const Vector &direction,const Vector &up);

	friend std::ostream &operator<<(std::ostream &os,const Matrix &m);
	friend std::istream &operator>>(std::istream &is,      Matrix &m);

public:

	/// Default constructor
	Matrix();
	/// Copy constructor
	Matrix(const Matrix &matrix);
	/// Construct from array 
	Matrix(const float *matrix);
	/// Construct from array 
	Matrix(const double *matrix);
	/// Construct from OpenGL GL_MODELVIEW_MATRIX or GL_PROJECTION_MATRIX
	Matrix(const unsigned int glMatrix);
	/// Construct from string
	Matrix(const std::string &str);

	/// Assignment operator
	Matrix &operator=(const Matrix &);

	/// Matrix multiplication
	Matrix  operator*(const Matrix &) const;
	/// In-place matrix multiplication
	Matrix &operator*=(const Matrix &);

	/// Matrix transformation of 3D vector
	Vector operator*(const Vector &) const;

	/// Reset to identity matrix
	void reset();
	/// Reset to identity matrix
	void identity();

	/// Is this matrix identity?
	bool isIdentity() const;

	/// Access i'th element of matrix
	      double &operator[](const int i);
	/// Access i'th element of matrix
	const double &operator[](const int i) const;

	/// Access as array
	operator double * ();
	/// Access as array
	operator const double * () const;

	/// Equality operator
	bool operator==(const Matrix &) const;
	/// Not-equal operator
	bool operator!=(const Matrix &) const;

	/// Calculate matrix inverse
	Matrix inverse() const;
	/// Calculate matrix transpose
	Matrix transpose() const;
	/// Calculate unmatrix
	UnMatrix unmatrix() const;
	/// Calculate matrix determinant
	double det() const;

	/// Mult current OpenGL matrix 
	void glMultMatrix() const;
	/// Load current OpenGL matrix
	void glLoadMatrix() const;

	/// Write matrix in Povray format
	std::ostream &writePov(std::ostream &os) const;

private:

	double _matrix[16];
	static double _identity[16];

	inline void set(const int col,const int row,const double val) 
	{ 
		_matrix[col*4+row] = val;
	}

	inline double get(const int col,const int row) const
	{
		return _matrix[col*4+row];
	}

	inline double &element(const int col,const int row) 
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
