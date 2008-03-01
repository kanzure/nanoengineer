// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NXOPENGLCAMERA_H
#define NXOPENGLCAMERA_H

#if defined(__APPLE__)
#include <OpenGL/gl.h>
#include <OpenGL/glu.h>
#else
#include <GL/gl.h>
#include <GL/glu.h>
#endif
#include <glt_vector3.h>
#include <glt_vector4.h>
#include <glt_matrix4.h>
#include <glt_viewport.h>

#include "NXOpenGLCamera_sm.h"

class QGLWidget;

struct Projection {
    Projection() {}
    ~Projection() {}
    void glReset(void) { glMatrixMode(GL_PROJECTION); glLoadIdentity(); }
};

struct OrthographicProjection : public Projection {
    real l, r, b, t, n, f;
    OrthographicProjection() : l(0), r(0), b(0), t(0), n(0), f(0) {}
    OrthographicProjection(real const& _l, real const& _r,
                           real const& _b, real const& _t,
                           real const& _n, real const& _f)
        : l(_l), r(_r), b(_b), t(_t), n(_n), f(_f) {}
    ~OrthographicProjection() {}
    void glSet(void) { glReset(); glOrtho(l, r, b, t, n, f); }
};


struct PerspectiveProjection : public Projection {
    real fovy_deg, aspect, n, f;
    PerspectiveProjection() : fovy_deg(0), aspect(0), n(0), f(0) {}
    PerspectiveProjection(real const& _fovy_deg, real const& _aspect, 
                          real const& _n, real const& _f)
        : fovy_deg(_fovy_deg), aspect(_aspect), n(_n), f(_f) {}
    ~PerspectiveProjection() {}
    void glSet(void) { glReset(); gluPerspective(fovy_deg, aspect, n, f); }
};

/* CLASS: NXOpenGLCamera */
class NXOpenGLCamera
{
public:
    NXOpenGLCamera(QGLWidget *theParent);
    ~NXOpenGLCamera();
    
    void reset(void);
    
    Vector eye(void) const;
    
    Vector unproject(real x, real y, real z=0.0);
    
    // mouse-input effectors
    void rotateStart(int x, int y);
    void rotate(int x, int y);
    void rotateStop(int x, int y);
    
    void translateStart(int x, int y);
    void translate(int x, int y);
    void translateStop(int x, int y);
    
    void resizeViewport(int w, int h);
    
    // void glGet(void);
    // void glGetPosition(void);
    // void glGetProjection(void);
    // void glGetViewport(void) { viewport.get(); }
    
    void glSetPosition(void);
    void glSetProjection(void);
    void glSetViewport(void) { viewport.set(); }
    
    void gluLookAt(real eyeX, real eyeY, real eyeZ,
                   real centerX, real centerY, real centerZ,
                   real upX, real upY, real upZ);
    void glOrtho(real l, real r, real b, real t, real n, real f);
    // void glFrustum(real l, real r, real b, real t, real n, real f);
    void gluPerspective(real fovy, real aspect, real n, real f);
    void glViewport(int x, int y, int w, int h);
    void zoom(GLdouble d);
    
    void rotateStartEvent(int x, int y) { fsm.rotateStartEvent(x,y); }
    void rotatingEvent(int x, int y) { fsm.rotatingEvent(x,y); }
    void rotateStopEvent(int x, int y) { fsm.rotateStopEvent(x,y); }
    
    void translateStartEvent(int x, int y) { fsm.translateStartEvent(x,y); }
    void translatingEvent(int x, int y) { fsm.translatingEvent(x,y); }
    void translateStopEvent(int x, int y) { fsm.translateStopEvent(x,y); }
    
private:
    QGLWidget *parent;
    NXOpenGLCameraContext fsm;
    
    Vector translation;
    Vector4 viewingQuaternion;
    GltMatrix modelViewMatrix;
    // GltMatrix projectionMatrix;
    bool isPerspectiveProjection;
    OrthographicProjection orthographicProjection;
    PerspectiveProjection perspectiveProjection;
    GltViewport viewport;
    
    // for mouse-rotations
    int oldMouseX, oldMouseY;
    Vector4 oldViewingQuaternion;

    // for mouse-translations
    Vector translationInitialWpt;
    
    void parseModelViewMatrix(void);
    void buildModelViewMatrix(void);
};

#endif // NXOPENGLCAMERA_H
