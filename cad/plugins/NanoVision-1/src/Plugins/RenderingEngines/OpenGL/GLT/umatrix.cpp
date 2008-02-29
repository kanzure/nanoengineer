#include "glt_umatrix.h"

/*! \file 
	\ingroup Math
*/

#include <iostream>
using namespace std;

#include "glt_gl.h"

#include "glt_matrix4.h"

//
// From Graphics Gems II - Decomposing a matrix into simple transformations. Pg. 320
//

// unmatrix.c - given a 4x4 matrix, decompose it into standard operations.
//
// Author:	Spencer W. Thomas
//          University of Michigan
//

// unmatrix - Decompose a non-degenerate 4x4 transformation matrix into
// the sequence of transformations that produced it.
// [Sx][Sy][Sz][Shearx/y][Sx/z][Sz/y][Rx][Ry][Rz][Tx][Ty][Tz][P(x,y,z,w)]
//
// The coefficient of each transformation is returned in the corresponding
// element of the vector tran.
//
// Returns true upon success, false if the matrix is singular.
//

GltUnMatrix::GltUnMatrix()
{
	memset(_tran,0,sizeof(_tran));
}

GltUnMatrix::GltUnMatrix(const GltUnMatrix &umatrix)
{
	memcpy(_tran,umatrix._tran,sizeof(_tran));
}

GltUnMatrix::GltUnMatrix(const GltMatrix &matrix)
{
	GltUnMatrix umatrix = matrix.unmatrix();
	memcpy(_tran,umatrix._tran,sizeof(_tran));
}

GltUnMatrix::~GltUnMatrix()
{
}

static char *UnMatrixFieldDescription[] =
{
 	"U_SCALEX",
 	"U_SCALEY",
 	"U_SCALEZ",
 	"U_SHEARXY",
 	"U_SHEARXZ",
 	"U_SHEARYZ",
 	"U_ROTATEX",
 	"U_ROTATEY",
 	"U_ROTATEZ",
 	"U_TRANSX",
 	"U_TRANSY",
 	"U_TRANSZ",
 	"U_PERSPX",
 	"U_PERSPY",
 	"U_PERSPZ",
 	"U_PERSPW"
};

/*! 
	\brief		GltUnMatrix difference
	\ingroup	Math
*/

GltUnMatrix 
operator-(const GltUnMatrix &b,const GltUnMatrix &a)
{
	GltUnMatrix um;

	um[U_SCALEX]  = b._tran[U_SCALEX] - a._tran[U_SCALEX];
	um[U_SCALEY]  = b._tran[U_SCALEY] - a._tran[U_SCALEY];
	um[U_SCALEZ]  = b._tran[U_SCALEZ] - a._tran[U_SCALEZ];

	um[U_ROTATEX] = b._tran[U_ROTATEX] - a._tran[U_ROTATEX];
	um[U_ROTATEY] = b._tran[U_ROTATEY] - a._tran[U_ROTATEY];
	um[U_ROTATEZ] = b._tran[U_ROTATEZ] - a._tran[U_ROTATEZ];

	um[U_TRANSX]  = b._tran[U_TRANSX] - a._tran[U_TRANSX];
	um[U_TRANSY]  = b._tran[U_TRANSY] - a._tran[U_TRANSY];
	um[U_TRANSZ]  = b._tran[U_TRANSZ] - a._tran[U_TRANSZ];

	return um;
}

/*! 
	\brief		GltUnMatrix scaling
	\ingroup	Math
*/

GltUnMatrix 
operator*(const GltUnMatrix &a,const double scaleFactor)
{
	GltUnMatrix um = a;

	um[U_SCALEX]  *= scaleFactor;
	um[U_SCALEY]  *= scaleFactor;
	um[U_SCALEZ]  *= scaleFactor;

	um[U_ROTATEX] *= scaleFactor;
	um[U_ROTATEY] *= scaleFactor;
	um[U_ROTATEZ] *= scaleFactor;

	um[U_TRANSX]  *= scaleFactor;
	um[U_TRANSY]  *= scaleFactor;
	um[U_TRANSZ]  *= scaleFactor;

	return um;
}

/*! 
	\brief		GltUnMatrix addition
	\ingroup	Math
*/

GltUnMatrix 
operator+(const GltUnMatrix &a,const GltUnMatrix &b)
{
	GltUnMatrix um;

	um[U_SCALEX]  = b._tran[U_SCALEX] + a._tran[U_SCALEX];
	um[U_SCALEY]  = b._tran[U_SCALEY] + a._tran[U_SCALEY];
	um[U_SCALEZ]  = b._tran[U_SCALEZ] + a._tran[U_SCALEZ];

	um[U_ROTATEX] = b._tran[U_ROTATEX] + a._tran[U_ROTATEX];
	um[U_ROTATEY] = b._tran[U_ROTATEY] + a._tran[U_ROTATEY];
	um[U_ROTATEZ] = b._tran[U_ROTATEZ] + a._tran[U_ROTATEZ];

	um[U_TRANSX]  = b._tran[U_TRANSX] + a._tran[U_TRANSX];
	um[U_TRANSY]  = b._tran[U_TRANSY] + a._tran[U_TRANSY];
	um[U_TRANSZ]  = b._tran[U_TRANSZ] + a._tran[U_TRANSZ];

	return um;
}


/*! 
	\brief		Output an GltUnMatrix field description to a text stream
	\ingroup	Math
*/

std::ostream &
operator<<(std::ostream &os,const UnMatrixField &field)
{
	if (field>=U_SCALEX && field<=U_PERSPW)
		os << UnMatrixFieldDescription[field];
	else
		os << "Unknown";

	return os;
}

/*! 
	\brief		Read an GltUnMatrix field from a text stream
	\ingroup	Math
*/

istream &
operator>>(istream &is,UnMatrixField &field)
{
	char buffer[128];

	is >> buffer;

	for (int f=0;f<16;f++)
		if (!strcmp(buffer,UnMatrixFieldDescription[f]))
		{
			field = (UnMatrixField) f;
			break;
		}

	return is;
}

/*! 
	\brief		Write an GltUnMatrix to a text stream
	\ingroup	Math
*/

std::ostream &
operator<<(std::ostream &os,const GltUnMatrix &unMatrix)
{
	for (int f=0;f<16;f++)
		os << (UnMatrixField) f << ' ' << unMatrix._tran[f] << endl;

	return os;
}

/*! 
	\brief		Read an GltUnMatrix from a text stream
	\ingroup	Math
*/

istream &
operator>>(istream &is,GltUnMatrix &unMatrix)
{
	for (int f=0;f<16;f++)
	{
		UnMatrixField field;
		double value;

		is >> field;
		is >> value;

		if (!is.eof()) unMatrix[field] = value;
	}

	return is;
}

typedef struct {
	double x,y,z,w;
} Vector4;

GltUnMatrix
GltMatrix::unmatrix() const
{
	GltUnMatrix tran;

 	GltMatrix locmat = (*this);

	if (locmat.element(3,3)==0.0)
		return tran;

 	register int i, j;

	for ( i=0; i<4;i++ )
 		for ( j=0; j<4; j++ )
 			locmat.element(i,j) /= locmat.element(3,3);

 	/* pmat is used to solve for perspective, but it also provides
 	 * an easy way to test for singularity of the upper 3x3 component.
 	 */

 	GltMatrix pmat = locmat;

 	for ( i=0; i<3; i++ )
 		pmat.set(i,3,0.0);

 	pmat.set(3,3,1.0);

 	if ( pmat.det() == 0.0 )
 		return tran;

 	/* First, isolate perspective.  This is the messiest. */

 	if 
	( 
		locmat.element(0,3) != 0.0 || 
		locmat.element(1,3) != 0.0 ||
 		locmat.element(2,3) != 0.0 
	) 
	{
		Vector4 prhs, psol;

 		/* prhs is the right hand side of the equation. */
 
		prhs.x = locmat.element(0,3);
 		prhs.y = locmat.element(1,3);
 		prhs.z = locmat.element(2,3);
 		prhs.w = locmat.element(3,3);

 		/* Solve the equation by inverting pmat and multiplying
 		 * prhs by the inverse.  (This is the easiest way, not
 		 * necessarily the best.)
 		 * inverse function (and det4x4, above) from the GltMatrix
 		 * Inversion gem in the first volume.
 		 */

//		GltMatrix invpmat = pmat.inverse();
//		GltMatrix tinvpmat = invpmat.transpose();
// 		V4MulPointByMatrix(&prhs, &tinvpmat, &psol);    // REVISIT
 
		psol.x = 0.0;
		psol.y = 0.0;
		psol.z = 0.0;
		psol.w = 0.0;

 		/* Stuff the answer away. */
 		tran[U_PERSPX] = psol.x;
 		tran[U_PERSPY] = psol.y;
 		tran[U_PERSPZ] = psol.z;
 		tran[U_PERSPW] = psol.w;

 		/* Clear the perspective partition. */
 		locmat.element(0,3) = locmat.element(1,3) =	locmat.element(2,3) = 0.0;
 		locmat.element(3,3) = 1.0;

 	} else		/* No perspective. */
		tran[U_PERSPX] = tran[U_PERSPY] = tran[U_PERSPZ] = tran[U_PERSPW] = 0;

 	/* Next take care of translation (easy). */
 	for ( i=0; i<3; i++ ) 
	{
 		tran[(UnMatrixField) (U_TRANSX + i)] = locmat.element(3,i);
 		locmat.set(3,i,0.0);
 	}

 	Vector  row[3];

 	/* Now get scale and shear. */
 	for ( i=0; i<3; i++ ) 
	{
 		row[i][0] = locmat.get(i,0);
 		row[i][1] = locmat.get(i,1);
 		row[i][2] = locmat.get(i,2);
 	}

 	/* Compute X scale factor and normalize first row. */

 	tran[U_SCALEX] = sqrt(row[0].norm());
 	row[0].normalize();

 	/* Compute XY shear factor and make 2nd row orthogonal to 1st. */
 	tran[U_SHEARXY] = row[0] * row[1];
	row[1] = row[1] - row[0] * tran[U_SHEARXY];

 	/* Now, compute Y scale and normalize 2nd row. */
 	tran[U_SCALEY] = sqrt(row[1].norm());
 	row[1].normalize();
 	tran[U_SHEARXY] /= tran[U_SCALEY];

 	/* Compute XZ and YZ shears, orthogonalize 3rd row. */
 	tran[U_SHEARXZ] = row[0] * row[2];
 	row[2] = row[2] - row[0] * tran[U_SHEARXZ];

 	tran[U_SHEARYZ] = row[1] * row[2];
	row[2] = row[2] - row[1] * tran[U_SHEARYZ];

 	/* Next, get Z scale and normalize 3rd row. */
 	tran[U_SCALEZ] = sqrt(row[2].norm());
 	row[2].normalize();

 	tran[U_SHEARXZ] /= tran[U_SCALEZ];
 	tran[U_SHEARYZ] /= tran[U_SCALEZ];
 
 	/* At this point, the matrix (in rows[]) is orthonormal.
 	 * Check for a coordinate system flip.  If the determinant
 	 * is -1, then negate the matrix and the scaling factors.
 	 */
 	if ( row[0] * xProduct(row[1],row[2]) < 0.0 )
 		for ( i = 0; i < 3; i++ ) 
		{
 			tran[(UnMatrixField) (U_SCALEX+i)] *= -1;
 			row[i] = row[i] * -1.0;
 		}
 
 	/* Now, get the rotations out, as described in the gem. */
 	tran[U_ROTATEY] = asin(-row[0][2]);

 	if ( cos(tran[U_ROTATEY]) != 0 ) 
	{
 		tran[U_ROTATEX] = atan2(row[1][2], row[2][2]);
 		tran[U_ROTATEZ] = atan2(row[0][1], row[0][0]);
 	} 
	else 
	{
 		tran[U_ROTATEX] = atan2(row[1][0], row[1][1]);
 		tran[U_ROTATEZ] = 0;
 	}

	return tran;
}

//
// From Graphics Gems GEMSI\MATINV.C
//

//
// Calculate the determinant of a 4x4 matrix.
//

double
GltMatrix::det() const
{
    double ans;
    double a1, a2, a3, a4, b1, b2, b3, b4, c1, c2, c3, c4, d1, d2, d3, d4;

    /* assign to individual variable names to aid selecting */
	/*  correct elements */

	a1 = get(0,0); b1 = get(0,1); 
	c1 = get(0,2); d1 = get(0,3);

	a2 = get(1,0); b2 = get(1,1); 
	c2 = get(1,2); d2 = get(1,3);

	a3 = get(2,0); b3 = get(2,1); 
	c3 = get(2,2); d3 = get(2,3);

	a4 = get(3,0); b4 = get(3,1); 
	c4 = get(3,2); d4 = get(3,3);

    ans = a1 * det3x3( b2, b3, b4, c2, c3, c4, d2, d3, d4)
        - b1 * det3x3( a2, a3, a4, c2, c3, c4, d2, d3, d4)
        + c1 * det3x3( a2, a3, a4, b2, b3, b4, d2, d3, d4)
        - d1 * det3x3( a2, a3, a4, b2, b3, b4, c2, c3, c4);
    return ans;
}

// 
// Calculate the determinant of a 3x3 matrix
// in the form
//
//     | a1,  b1,  c1 |
//     | a2,  b2,  c2 |
//     | a3,  b3,  c3 |
//

double 
GltMatrix::det3x3
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
) const
{
    return 
		a1 * det2x2( b2, b3, c2, c3 )
        - b1 * det2x2( a2, a3, c2, c3 )
        + c1 * det2x2( a2, a3, b2, b3 );
}

// Calculate the determinant of a 2x2 matrix.

double
GltMatrix::det2x2
( 
	const double a, 
	const double b, 
	const double c, 
	const double d
) const
{
	return a * d - b * c;
}


bool 
GltUnMatrix::uniformScale(const double tol) const
{
	if (fabs(_tran[U_SCALEX]-_tran[U_SCALEY])>tol) return false;
	if (fabs(_tran[U_SCALEX]-_tran[U_SCALEZ])>tol) return false;
	if (fabs(_tran[U_SCALEY]-_tran[U_SCALEZ])>tol) return false;
	return true;
}

bool 
GltUnMatrix::noRotation(const double tol) const
{
	if (fabs(_tran[U_ROTATEX])>tol) return false;
	if (fabs(_tran[U_ROTATEY])>tol) return false;
	if (fabs(_tran[U_ROTATEZ])>tol) return false;
	return true;
}

bool 
GltUnMatrix::noShear(const double tol) const
{
	if (fabs(_tran[U_SHEARXY])>tol) return false;
	if (fabs(_tran[U_SHEARXZ])>tol) return false;
	if (fabs(_tran[U_SHEARYZ])>tol) return false;
	return true;
}

bool 
GltUnMatrix::noPerspective(const double tol) const
{
	if (fabs(_tran[U_PERSPX])>tol) return false;
	if (fabs(_tran[U_PERSPY])>tol) return false;
	if (fabs(_tran[U_PERSPZ])>tol) return false;
	if (fabs(_tran[U_PERSPW])>tol) return false;
	return true;
}

