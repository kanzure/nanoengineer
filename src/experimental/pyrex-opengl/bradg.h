#ifndef _bradg_h_
#define _bradg_h_

#ifdef __cplusplus
extern "C" {
#endif

PyObject * shapeRendererInit();
void shapeRendererSetFrustum(float frustum[6]);
void shapeRendererSetOrtho(float ortho[6]);
void shapeRendererSetViewport(int viewport[4]);
void shapeRendererSetModelView(float modelview[6]);
void shapeRendererUpdateLODEval();
PyObject * shapeRendererDrawSpheres(int count, float center[][3], float radius[], float color[][4]);
PyObject * shapeRendererDrawCylinders(int count, float pos1[][3], float pos2[][3], float radius[], int capped[], float color[][4]);
void shapeRendererSetLODScale(float s);
void shapeRendererSetUseLOD(int useLOD);
void shapeRendererSetMaterialParameters(float whiteness, float brightness, float shininess);

#ifdef __cplusplus
}
#endif

#endif /* _bradg_h_ */
