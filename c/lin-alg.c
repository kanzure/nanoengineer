/**
 * Linear algebra stuff
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "mol.h"

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

/*
 * Local Variables:
 * c-basic-offset: 8
 * tab-width: 8
 * End:
 */
