// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.
/**
 * Linear algebra stuff
 */

// XXX This stuff could possibly benefit from inlining.  Need to profile.

#include <math.h>

#include "lin-alg.h"

struct xyz vcon(double x) {
	struct xyz u;
	vsetc(u,x);
	return u;
}

struct xyz vsum(struct xyz v, struct xyz w) {
	struct xyz u;
	vadd2(u,v,w);
	return u;
}

struct xyz vprod(struct xyz v, struct xyz w) {
	struct xyz u;
	vmul2(u,v,w);
	return u;
}

struct xyz vprodc(struct xyz v, double w) {
	struct xyz u;
	vmul2c(u,v,w);
	return u;
}

struct xyz vdif(struct xyz v, struct xyz w) {
	struct xyz u;
	vsub2(u,v,w);
	return u;
}

double vlen(struct xyz v) {	/* length of a vector */
	return sqrt(vdot(v,v));
}

struct xyz uvec(struct xyz v) {	/* unit vector in given direction */
	struct xyz w;
	double rlen;
	rlen=1.0/vlen(v);
	vmul2c(w,v,rlen);
	return w;
}

double vang(struct xyz v, struct xyz w) {
	struct xyz u1, u2;
	u1=uvec(v);
	u2=uvec(w);
	return acos(vdot(u1,u2));
}

struct xyz vx(struct xyz v, struct xyz w) {
	struct xyz u;
	u.x = v.y * w.z - v.z * w.y;
	u.y = v.z * w.x - v.x * w.z;
	u.z = v.x * w.y - v.y * w.x;
	return u;
}
