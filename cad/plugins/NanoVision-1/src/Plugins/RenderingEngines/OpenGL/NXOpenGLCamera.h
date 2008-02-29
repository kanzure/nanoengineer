// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NXOPENGLCAMERA_H
#define NXOPENGLCAMERA_H

#include <glt_vector3.h>
#include <glt_vector4.h>
#include <glt_matrix4.h>
#include <glt_viewport.h>

#include "NXOpenGLCamera_sm.h"

class QGLWidget;

class NXOpenGLCamera
{
public:
    NXOpenGLCamera(QGLWidget *theParent);
    ~NXOpenGLCamera();
    
    void reset(void);
    
    Vector eye(void) const;
    
    Vector unproject(real x, real y, real z=0.0);
    
    void rotateStart(int x, int y);
    void rotate(int x, int y);
    void rotateStop(int x, int y);
    
    void resizeViewport(int w, int h);
    
    void glGet(void);
    void glGetPosition(void);
    void glGetProjection(void);
    void glGetViewport(void) { viewport.get(); }
    
    void glSetPosition(void);
    void glSetProjection(void);
    void glSetViewport(void) { viewport.set(); }
    
    void gluLookAt(real eyeX, real eyeY, real eyeZ,
                   real centerX, real centerY, real centerZ,
                   real upX, real upY, real upZ);
    void glFrustum(real l, real r, real b, real t, real n, real f);
    void gluPerspective(real fovy, real aspect, real n, real f);
    
    void zoom(GLdouble d);
    
    void rotateStartEvent(int x, int y) { fsm.rotateStartEvent(x,y); }
    void rotatingEvent(int x, int y) { fsm.rotatingEvent(x,y); }
    void rotateStopEvent(int x, int y) { fsm.rotateStopEvent(x,y); }
    
private:
    QGLWidget *parent;
    NXOpenGLCameraContext fsm;
    
    Vector translation;
    Vector4 viewingQuaternion;
    GltMatrix modelViewMatrix;
    GltMatrix projectionMatrix;
    GltViewport viewport;
    
    int oldMouseX, oldMouseY;
    Vector4 oldViewingQuaternion;

    
    void parseModelViewMatrix(void);
    void buildModelViewMatrix(void);
};

#endif // NXOPENGLCAMERA_H
