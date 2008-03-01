// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXOpenGLCamera.h"
extern "C" {
#include "trackball.h"
}

#include <iostream>
#include <QGLWidget>

using namespace std;

NXOpenGLCamera::NXOpenGLCamera(QGLWidget *theParent)
: parent(theParent), fsm(*this),
translation(), viewingQuaternion(),
modelViewMatrix(), //projectionMatrix(),
isPerspectiveProjection(false),
orthographicProjection(), perspectiveProjection(),
viewport(),
oldMouseX(0), oldMouseY(0),
oldViewingQuaternion()
{
    reset();
}

NXOpenGLCamera::~NXOpenGLCamera()
{
}


/// Resets the camera (position, projection and viewport)
void NXOpenGLCamera::reset(void)
{
    modelViewMatrix.identity();
    orthographicProjection.glReset();
    isPerspectiveProjection = false;
    viewport.resize(0, 0, parent->width(), parent->height());
}


/// Position of the eye in world-space
Vector NXOpenGLCamera::eye(void) const
{
    Vector eyePos;
    eyePos[0] = -modelViewMatrix[12];
    eyePos[1] = -modelViewMatrix[13];
    eyePos[2] = -modelViewMatrix[14];
    return eyePos;
}


/// Records the mouse-position at the start of drag for trackball rotation
void NXOpenGLCamera::rotateStart(int x, int y)
{
    // cerr << "dragStart @(" << x << ',' << y << ')' << endl;
    oldMouseX = x;
    oldMouseY = y;
    oldViewingQuaternion = viewingQuaternion;
}


/// Updates camera's position when mouse is dragged to (x,y) to rotate the scene
void NXOpenGLCamera::rotate(int x, int y)
{
    real oldx = 2.0 * real(oldMouseX) / real(viewport.width()) - 1.0;
    real oldy = 1.0 - 2.0 * real(oldMouseY) / real(viewport.height());

    real newx = 2.0 * real(x) / real(viewport.width()) - 1.0;
    real newy = 1.0 - 2.0 * real(y) / real(viewport.height());
    
    // cerr << "drag @(" << newx << ',' << newy << ')' << endl;
    
    Vector4 dragRotationQuat;
    trackball(dragRotationQuat, newx, newy, oldx, oldy);
    add_quats(oldViewingQuaternion, dragRotationQuat, viewingQuaternion);
    buildModelViewMatrix();
}


/// Marks the end of mouse-dragging for rotation
void NXOpenGLCamera::rotateStop(int x, int y)
{
    // cerr << "dragStop @(" << x << ',' << y << ')' << endl;
}


void NXOpenGLCamera::translateStart(int x, int y)
{
    cerr << "translateStart @(" << x << ',' << y << ')' << endl;
    translationInitialWpt = unproject(x,parent->height()-y);
}


void NXOpenGLCamera::translate(int x, int y)
{
    cerr << "translate @(" << x << ',' << y << ')' << endl;
    Vector translationCurrentWpt = unproject(x,parent->height()-y);
    Vector delta = translationCurrentWpt - translationInitialWpt;
    translation += delta;
    modelViewMatrix(0,3) = translation[0];
    modelViewMatrix(1,3) = translation[1];
    modelViewMatrix(2,3) = translation[2];
    cerr << "translate by" << delta.x() << ',' << delta.y() << ','
        << delta.z() << ')' << endl;
}


void NXOpenGLCamera::translateStop(int x, int y)
{
    cerr << "translateStop @(" << x << ',' << y << ')' << endl;
    /// @todo
}


#if 0
/// Reads the location-orientation, projection and viewport settings
/// info from OpenGL
void NXOpenGLCamera::glGet(void)
{
    glGetPosition();
    glGetProjection();
    glGetViewport();
}


/// Reads the position and orientation of the camera from OpenGL
void NXOpenGLCamera::glGetPosition(void)
{
    modelViewMatrix.glGet(GL_MODELVIEW);
    parseModelViewMatrix();
}


/// Reads the projection settings for the camera from OpenGL
void NXOpenGLCamera::glGetProjection(void)
{
    projectionMatrix.glGet(GL_PROJECTION);
    perspectiveProjection = projectionMatrix.isPerspective();
}
#endif

/// Figure out camera's translation and rotation from model-view matrix
/// Assumes the model-view matrix has an orthonormal rotational component
/// and a translational component in it. No scaling
void NXOpenGLCamera::parseModelViewMatrix(void)
{
    // formulae from
    // http://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToQuaternion/index.htm
    GltMatrix const& m = modelViewMatrix;
    real const qw = (real) sqrt(1.0 + m(0,0) + m(1,1) + m(2,2)) / 2.0;
    real const four_qw = 4.0 * qw;
    real const qx = (m(2,1) - m(1,2)) / four_qw;
    real const qy = (m(0,2) - m(2,0)) / four_qw;
    real const qz = (m(1,0) - m(0,1)) / four_qw;
    viewingQuaternion[3] = qw;
    viewingQuaternion[0] = qx;
    viewingQuaternion[1] = qy;
    viewingQuaternion[2] = qz;

    translation[0] = m(0,3);
    translation[1] = m(1,3);
    translation[2] = m(2,3);
}


/// Builds the model-view matrix from translation and rotation info
void NXOpenGLCamera::buildModelViewMatrix(void)
{
    build_rotmatrix(modelViewMatrix, viewingQuaternion);
    modelViewMatrix(0,3) = translation[0];
    modelViewMatrix(1,3) = translation[1];
    modelViewMatrix(2,3) = translation[2];
}


/// Applies the camera's world-location and orientation settings to OpenGL
void NXOpenGLCamera::glSetPosition(void)
{
    modelViewMatrix.glSet(GL_MODELVIEW);
}


/// Applies the camera's projection-settings to OpenGL
void NXOpenGLCamera::glSetProjection(void)
{
    if(isPerspectiveProjection)
        perspectiveProjection.glSet();
    else
        orthographicProjection.glSet();
}


/// Resizes the camera's viewport and adjusts the projection matrix accordingly
void NXOpenGLCamera::resizeViewport(int w, int h)
{
    viewport.resize(0, 0, w, h);
    real const aspectRatio = (real)w / (real)h;
    
    // adjust projection matrix
    if(isPerspectiveProjection) {
        // projectionMatrix(1,1) = projectionMatrix(0,0) / aspectRatio;
        perspectiveProjection.aspect = aspectRatio;
    }
#if 0
    else {
        real const oldAspectRatio = projectionMatrix(1,1)/projectionMatrix(0,0);
        real const aspectRatioFactor = aspectRatio / oldAspectRatio;
        if(aspectRatioFactor < 1.0) {
            // width has reduced in comparison to height - maintain y
            projectionMatrix(0,0) /= aspectRatioFactor;
        }
        else {
            // height has reduced in comparison to width - maintain x
            projectionMatrix(1,1) *= aspectRatioFactor;
        }
    }
#endif
}


/// Sets the camera's location and orientation info to that given and
/// immediately applies it to OpenGL
void NXOpenGLCamera::gluLookAt(real eyeX, real eyeY, real eyeZ,
                               real centerX, real centerY, real centerZ,
                               real upX, real upY, real upZ)
{
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    ::gluLookAt(eyeX, eyeY, eyeZ, centerX, centerY, centerZ, upX, upY, upZ);
    modelViewMatrix.glGet(GL_MODELVIEW);
    parseModelViewMatrix();
}


/// Sets the camera's projection to the orthographic with the given bounding
/// planes and applies it to OpenGL
void NXOpenGLCamera::glOrtho(real l, real r, real b, real t, real n, real f)
{
    // glMatrixMode(GL_PROJECTION);
    // glLoadIdentity();
    // ::glOrtho(l, r, b, t, n, f);
    // projectionMatrix.glGet(GL_PROJECTION);
    isPerspectiveProjection = false;
    orthographicProjection = OrthographicProjection(l, r, b, t, n, f);
    orthographicProjection.glSet();
}


#if 0
/// Sets the camera's projection to the given frustum and applies it to OpenGL
void NXOpenGLCamera::glFrustum(real l, real r, real b, real t, real n, real f)
{
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    ::glFrustum(l, r, b, t, n, f);
    projectionMatrix.glGet(GL_PROJECTION);
    perspectiveProjection = true;
}
#endif

/// Sets the camera's projection info to that given and applies it to OpenGL
void NXOpenGLCamera::gluPerspective(real fovy, real aspect, real n, real f)
{
    // glMatrixMode(GL_PROJECTION);
    // glLoadIdentity();
    // ::gluPerspective(fovy, aspect, n, f);
    // projectionMatrix.glGet(GL_PROJECTION);
    isPerspectiveProjection = true;
    perspectiveProjection = PerspectiveProjection(fovy, aspect, n, f);
    perspectiveProjection.glSet();
}


/// Sets the camera's viewport info and applies it to OpenGL
void NXOpenGLCamera::glViewport(int x, int y, int w, int h)
{
    ::glViewport((GLint) x, (GLint) y, (GLsizei) w, (GLsizei) h);
    viewport = GltViewport(x, y, w, h);
}


/// Unprojects the given (x,y,z), usually mouse coords with z=0, to a
/// world-space point and returns it
Vector NXOpenGLCamera::unproject(real x, real y, real z)
{
    GLdouble worldX, worldY, worldZ;
    GLdouble temp_projectionMatrix[16];
    glGetDoublev(GL_PROJECTION_MATRIX, temp_projectionMatrix);
    
#ifdef GLT_SINGLE_PRECISION
    // Create temporary store to catch differences in precision
    GLdouble temp_modelViewMatrix[16];
    for(int i=0; i<16; ++i) {
        temp_modelViewMatrix[i] = modelViewMatrix[i];
    }
    gluUnProject(x, y, z,
                 temp_modelViewMatrix,
                 temp_projectionMatrix,
                 viewport,
                 &worldX, &worldY, &worldZ);
#else
    gluUnProject(x, y, z,
                 modelViewMatrix,
                 temp_projectionMatrix,
                 viewport,
                 &worldX, &worldY, &worldZ);
#endif
    
    Vector wpt(worldX, worldY, worldZ);
    return wpt;
}
