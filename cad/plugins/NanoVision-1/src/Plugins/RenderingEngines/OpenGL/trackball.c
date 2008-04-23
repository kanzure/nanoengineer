/*
 * (c) Copyright 1993, 1994, Silicon Graphics, Inc.
 * ALL RIGHTS RESERVED
 * Permission to use, copy, modify, and distribute this software for
 * any purpose and without fee is hereby granted, provided that the above
 * copyright notice appear in all copies and that both the copyright notice
 * and this permission notice appear in supporting documentation, and that
 * the name of Silicon Graphics, Inc. not be used in advertising
 * or publicity pertaining to distribution of the software without specific,
 * written prior permission.
 *
 * THE MATERIAL EMBODIED ON THIS SOFTWARE IS PROVIDED TO YOU "AS-IS"
 * AND WITHOUT WARRANTY OF ANY KIND, EXPRESS, IMPLIED OR OTHERWISE,
 * INCLUDING WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY OR
 * FITNESS FOR A PARTICULAR PURPOSE.  IN NO EVENT SHALL SILICON
 * GRAPHICS, INC.  BE LIABLE TO YOU OR ANYONE ELSE FOR ANY DIRECT,
 * SPECIAL, INCIDENTAL, INDIRECT OR CONSEQUENTIAL DAMAGES OF ANY
 * KIND, OR ANY DAMAGES WHATSOEVER, INCLUDING WITHOUT LIMITATION,
 * LOSS OF PROFIT, LOSS OF USE, SAVINGS OR REVENUE, OR THE CLAIMS OF
 * THIRD PARTIES, WHETHER OR NOT SILICON GRAPHICS, INC.  HAS BEEN
 * ADVISED OF THE POSSIBILITY OF SUCH LOSS, HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, ARISING OUT OF OR IN CONNECTION WITH THE
 * POSSESSION, USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 * US Government Users Restricted Rights
 * Use, duplication, or disclosure by the Government is subject to
 * restrictions set forth in FAR 52.227.19(c)(2) or subparagraph
 * (c)(1)(ii) of the Rights in Technical Data and Computer Software
 * clause at DFARS 252.227-7013 and/or in similar or successor
 * clauses in the FAR or the DOD or NASA FAR Supplement.
 * Unpublished-- rights reserved under the copyright laws of the
 * United States.  Contractor/manufacturer is Silicon Graphics,
 * Inc., 2011 N.  Shoreline Blvd., Mountain View, CA 94039-7311.
 *
 * OpenGL(TM) is a trademark of Silicon Graphics, Inc.
 */

/* All float changed to real for GLT compatilibity
 * -- Manoj Rajagopalan, 20 Feb 2008
 */


/*
 * Trackball code:
 *
 * Implementation of a virtual trackball.
 * Implemented by Gavin Bell, lots of ideas from Thant Tessman and
 *   the August '88 issue of Siggraph's "Computer Graphics," pp. 121-129.
 *
 * Vector manip code:
 *
 * Original code from:
 * David M. Ciemiewicz, Mark Grossman, Henry Moreton, and Paul Haeberli
 *
 * Much mucking with by:
 * Gavin Bell
 */
#include <math.h>
#include "trackball.h"

/*
 * This size should really be based on the distance from the center of
 * rotation to the point on the object underneath the mouse.  That
 * point would then track the mouse as closely as possible.  This is a
 * simple example, though, so that is left as an Exercise for the
 * Programmer.
 */
#define TRACKBALLSIZE  (0.8f)

/*
 * Local function prototypes (not defined in trackball.h)
 */
static real tb_project_to_sphere(real, real, real);
static void normalize_quat(real [4]);

void
vzero(real *v)
{
    v[0] = 0.0;
    v[1] = 0.0;
    v[2] = 0.0;
}

void
vset(real *v, real x, real y, real z)
{
    v[0] = x;
    v[1] = y;
    v[2] = z;
}

void
vsub(const real *src1, const real *src2, real *dst)
{
    dst[0] = src1[0] - src2[0];
    dst[1] = src1[1] - src2[1];
    dst[2] = src1[2] - src2[2];
}

void
vcopy(const real *v1, real *v2)
{
    register int i;
    for (i = 0 ; i < 3 ; i++)
        v2[i] = v1[i];
}

void
vcross(const real *v1, const real *v2, real *cross)
{
    real temp[3];

    temp[0] = (v1[1] * v2[2]) - (v1[2] * v2[1]);
    temp[1] = (v1[2] * v2[0]) - (v1[0] * v2[2]);
    temp[2] = (v1[0] * v2[1]) - (v1[1] * v2[0]);
    vcopy(temp, cross);
}

real
vlength(const real *v)
{
    return (real) sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
}

void
vscale(real *v, real div)
{
    v[0] *= div;
    v[1] *= div;
    v[2] *= div;
}

void
vnormal(real *v)
{
    vscale(v, 1.0f/vlength(v));
}

real
vdot(const real *v1, const real *v2)
{
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2];
}

void
vadd(const real *src1, const real *src2, real *dst)
{
    dst[0] = src1[0] + src2[0];
    dst[1] = src1[1] + src2[1];
    dst[2] = src1[2] + src2[2];
}

/*
 * Ok, simulate a track-ball.  Project the points onto the virtual
 * trackball, then figure out the axis of rotation, which is the cross
 * product of P1 P2 and O P1 (O is the center of the ball, 0,0,0)
 * Note:  This is a deformed trackball-- is a trackball in the center,
 * but is deformed into a hyperbolic sheet of rotation away from the
 * center.  This particular function was chosen after trying out
 * several variations.
 *
 * It is assumed that the arguments to this routine are in the range
 * (-1.0 ... 1.0)
 */
void
trackball(real q[4], real p1x, real p1y, real p2x, real p2y)
{
    real a[3]; /* Axis of rotation */
    real phi;  /* how much to rotate about axis */
    real p1[3], p2[3], d[3];
    real t;

    if (p1x == p2x && p1y == p2y) {
        /* Zero rotation */
        vzero(q);
        q[3] = 1.0;
        return;
    }

    /*
     * First, figure out z-coordinates for projection of P1 and P2 to
     * deformed sphere
     */
    vset(p1, p1x, p1y, tb_project_to_sphere(TRACKBALLSIZE, p1x, p1y));
    vset(p2, p2x, p2y, tb_project_to_sphere(TRACKBALLSIZE, p2x, p2y));

    /*
     *  Now, we want the cross product of P1 and P2
     */
    vcross(p2,p1,a);

    /*
     *  Figure out how much to rotate around that axis.
     */
    vsub(p1, p2, d);
    t = vlength(d) / (2.0f*TRACKBALLSIZE);

    /*
     * Avoid problems with out-of-control values...
     */
    if (t > 1.0) t = 1.0;
    if (t < -1.0) t = -1.0;
    phi = (real)2.0f * (real) asin(t);

    axis_to_quat(a,phi,q);
}

/*
 *  Given an axis and angle, compute quaternion.
 */
void
axis_to_quat(real a[3], real phi, real q[4])
{
    vnormal(a);
    vcopy(a, q);
    vscale(q, (real) sin(phi/2.0));
    q[3] = (real) cos(phi/2.0);
}

/*
 * Project an x,y pair onto a sphere of radius r OR a hyperbolic sheet
 * if we are away from the center of the sphere.
 */
static real
tb_project_to_sphere(real r, real x, real y)
{
    real d, t, z;

    d = (real) sqrt(x*x + y*y);
    if (d < r * 0.70710678118654752440) {    /* Inside sphere */
        z = (real) sqrt(r*r - d*d);
    } else {           /* On hyperbola */
        t = r / 1.41421356237309504880f;
        z = t*t / d;
    }
    return z;
}

/*
 * Given two rotations, e1 and e2, expressed as quaternion rotations,
 * figure out the equivalent single rotation and stuff it into dest.
 *
 * This routine also normalizes the result every RENORMCOUNT times it is
 * called, to keep error from creeping in.
 *
 * NOTE: This routine is written so that q1 or q2 may be the same
 * as dest (or each other).
 */

#define RENORMCOUNT 97

void
add_quats(real q1[4], real q2[4], real dest[4])
{
    static int count=0;
    real t1[4], t2[4], t3[4];
    real tf[4];

    vcopy(q1,t1);
    vscale(t1,q2[3]);

    vcopy(q2,t2);
    vscale(t2,q1[3]);

    vcross(q2,q1,t3);
    vadd(t1,t2,tf);
    vadd(t3,tf,tf);
    tf[3] = q1[3] * q2[3] - vdot(q1,q2);

    dest[0] = tf[0];
    dest[1] = tf[1];
    dest[2] = tf[2];
    dest[3] = tf[3];

    if (++count > RENORMCOUNT) {
        count = 0;
        normalize_quat(dest);
    }
}

/*
 * Quaternions always obey:  a^2 + b^2 + c^2 + d^2 = 1.0
 * If they don't add up to 1.0, dividing by their magnitued will
 * renormalize them.
 *
 * Note: See the following for more information on quaternions:
 *
 * - Shoemake, K., Animating rotation with quaternion curves, Computer
 *   Graphics 19, No 3 (Proc. SIGGRAPH'85), 245-254, 1985.
 * - Pletinckx, D., Quaternion calculus as a basic tool in computer
 *   graphics, The Visual Computer 5, 2-13, 1989.
 */
static void
normalize_quat(real q[4])
{
    int i;
    real mag;

    mag = (q[0]*q[0] + q[1]*q[1] + q[2]*q[2] + q[3]*q[3]);
    for (i = 0; i < 4; i++) q[i] /= mag;
}

/*
 * Build a rotation matrix, given a quaternion rotation.
 *
 */
void
build_rotmatrix(real m[16], real q[4])
{
	/*(0,0)*/ m[0] = (real)1.0 - (real)2.0 * (q[1] * q[1] + q[2] * q[2]);
    /*(0,1)*/ m[4] = (real)2.0 * (q[0] * q[1] - q[2] * q[3]);
    /*(0,2)*/ m[8] = (real)2.0 * (q[2] * q[0] + q[1] * q[3]);
    /*(0,3)*/ m[12] = (real)0.0;

    /*(1,0)*/ m[1] = (real)2.0 * (q[0] * q[1] + q[2] * q[3]);
    /*(1,1)*/ m[5]= (real)1.0 - (real)2.0 * (q[2] * q[2] + q[0] * q[0]);
    /*(1,2)*/ m[9] = (real)2.0 * (q[1] * q[2] - q[0] * q[3]);
    /*(1,3)*/ m[13] = (real)0.0;

    /*(2,0)*/ m[2] = (real)2.0 * (q[2] * q[0] - q[1] * q[3]);
    /*(2,1)*/ m[6] = (real)2.0 * (q[1] * q[2] + q[0] * q[3]);
    /*(2,2)*/ m[10] = (real)1.0 - (real)2.0 * (q[1] * q[1] + q[0] * q[0]);
    /*(2,3)*/ m[14] = (real)0.0;

    /*(3,0)*/ m[3] = (real)0.0;
    /*(3,1)*/ m[7] = (real)0.0;
    /*(3,2)*/ m[11] = (real)0.0;
    /*(3,3)*/ m[15] = (real)1.0;
}

