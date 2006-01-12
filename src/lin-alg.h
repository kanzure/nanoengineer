
/* a 3-vector */
struct xyz {
        double x;
        double y;
        double z;
};

extern struct xyz vcon(double x);

extern struct xyz vsum(struct xyz v, struct xyz w);

extern struct xyz vprod(struct xyz v, struct xyz w);

extern struct xyz vprodc(struct xyz v, double w);

extern struct xyz vdif(struct xyz v, struct xyz w);

extern double vlen(struct xyz v);

extern struct xyz uvec(struct xyz v);

extern double vang(struct xyz v, struct xyz w);

extern struct xyz vx(struct xyz v, struct xyz w);

extern void matrixRotateX(double *m, double theta);

extern void matrixRotateY(double *m, double theta);

extern void matrixRotateZ(double *m, double theta);

extern void matrixRotateXYZ(double *rotation, double thetaX, double thetaY, double thetaZ);

extern void matrixMultiply(double *prod, double *a, double *b);

extern void matrixTransform(struct xyz *out, double *m, struct xyz *in);

extern void matrixInverseTransform(struct xyz *out, double *m, struct xyz *in);


/** vector addition (incremental: add src to dest) */
#define vadd(dest,src) dest.x+=src.x; dest.y+=src.y; dest.z+=src.z
/** vector addition (non-incremental) */
#define vadd2(dest,src1,src2) dest.x=src1.x+src2.x; \
    dest.y=src1.y+src2.y; dest.z=src1.z+src2.z
/** vector addition (incremental, with scaling) */
#define vadd2scale(dest,src1,k) dest.x+=src1.x*k; \
    dest.y+=src1.y*k; dest.z+=src1.z*k
/** vector subtraction (incremental: subtract src from dest) */
#define vsub(dest,src) dest.x-=src.x; dest.y-=src.y; dest.z-=src.z
/** vector subtraction (non-incremental) */
#define vsub2(dest,src1,src2) dest.x=src1.x-src2.x; \
    dest.y=src1.y-src2.y; dest.z=src1.z-src2.z
/** */
#define vmul(dest,src) dest.x*=src.x; dest.y*=src.y; dest.z*=src.z
/** */
#define vmul2(dest,src1,src2) dest.x=src1.x*src2.x; \
    dest.y=src1.y*src2.y; dest.z=src1.z*src2.z
/** */
#define vmul2c(dest,src1,src2) dest.x=src1.x*src2; \
    dest.y=src1.y*src2; dest.z=src1.z*src2
/** */
#define vmulc(dest,src) dest.x*=src; dest.y*=src; dest.z*=src

#define vdiv(dest,src) dest.x/=src.x; dest.y/=src.y; dest.z/=src.z
#define vdiv2(dest,src1,src2) dest.x=src1.x/src2.x; \
    dest.y=src1.y/src2.y; dest.z=src1.z/src2.z
#define vdivc(dest,src) dest.x/=src; dest.y/=src; dest.z/=src

/** */
#define vset(dest,src) dest.x=src.x; dest.y=src.y; dest.z=src.z
/** */
#define vsetc(dest,src) dest.x=src; dest.y=src; dest.z=src
/** */
#define vsetn(dest,src) dest.x= -src.x; dest.y= -src.y; dest.z= -src.z

/** */
#define vmin(dest,src) dest.x = min(dest.x,src.x); \
    dest.y = min(dest.y,src.y); dest.z = min(dest.z,src.z);
/** */
#define vmax(dest,src) dest.x = max(dest.x,src.x); \
    dest.y = max(dest.y,src.y); dest.z = max(dest.z,src.z);

/** */
#define vdot(src1,src2) (src1.x*src2.x+src1.y*src2.y+src1.z*src2.z)
// cross product
#define v2x(dest,src1,src2)  dest.x = src1.y * src2.z - src1.z * src2.y;\
	dest.y = src1.z * src2.x - src1.x * src2.z;\
	dest.z = src1.x * src2.y - src1.y * src2.x;
