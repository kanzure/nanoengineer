#ifndef _bradg_h_
#define _bradg_h_

#ifdef __cplusplus
extern "C" {
#endif

#include <Python.h>

// Changes here have to be reflected in quux.pyx and vice versa
typedef enum {
    IS_VBO_ENABLED = 1,
} ShapeRendererQuery;

PyObject * shapeRendererInit(void);
void shapeRendererFinishDrawing(void);
void shapeRendererStartDrawing(void);
void shapeRendererSetFrustum(float frustum[6]);
void shapeRendererSetOrtho(float ortho[6]);
void shapeRendererSetViewport(int viewport[4]);
void shapeRendererSetModelView(float modelview[6]);
void shapeRendererUpdateLODEval();
PyObject * shapeRendererDrawSpheres(int count, float center[][3], float radius[], float color[][4], unsigned int *names);
PyObject * shapeRendererDrawCylinders(int count, float pos1[][3], float pos2[][3], float radius[], int capped[], float color[][4], unsigned int *names);
PyObject * shapeRendererDrawSpheresIlvd(int count, float *spheres);
PyObject * shapeRendererDrawCylindersIlvd(int count, float *cylinders);
void shapeRendererSetLODScale(float s);
void shapeRendererSetUseDynamicLOD(int useLOD);
void shapeRendererSetStaticLODLevels(int sphereLOD, int cylinderLOD);
void shapeRendererSetMaterialParameters(float whiteness, float brightness, float shininess);
int shapeRendererGetInteger(int what);

#ifdef __cplusplus
}
#endif

#endif /* _bradg_h_ */
