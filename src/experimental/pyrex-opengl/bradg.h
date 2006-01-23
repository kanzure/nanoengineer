/*
 * Brad's stuff
 */

extern void shapeRendererInit(void);

extern void shapeRendererSetFrustum(float frustum[6]);
extern void shapeRendererSetViewport(int viewport[4]);
extern void shapeRendererSetModelView(float modelview[6]);
extern void shapeRendererUpdateLODEval(void);
extern void shapeRendererSetLODScale(float s);

extern void shapeRendererDrawSpheres(int count, float center[][3],
				     float radius[], float color[][4]);
extern void shapeRendererDrawCylinders(int count, float pos1[][3],
				       float pos2[][3], float radius[],
				       float color[][4]);
