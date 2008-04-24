// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXOpenGLCamera.h"
extern "C" {
#include "trackball.h"
}

#include <iostream>
#include <QGLWidget>

using namespace std;
using namespace Nanorex;

NXOpenGLCamera::NXOpenGLCamera(QGLWidget *theParent)
: parent(theParent), fsm(*this),
/*translation(),*/ namedView(), viewingQuaternion(),
// modelViewMatrix(), projectionMatrix(),
isPerspectiveProjection(true),
// orthographicProjection(), perspectiveProjection(),
viewport(),
// oldMouseX(0), oldMouseY(0),
oldViewingQuaternion(),
trackball(),
panInitialWpt()
{
    reset();
}

NXOpenGLCamera::~NXOpenGLCamera()
{
}


/// Resets the camera (position, projection and viewport)
void NXOpenGLCamera::reset(void)
{
	// modelViewMatrix.identity();
	// orthographicProjection.glReset();
	// isPerspectiveProjection = false;
    viewport.resize(0, 0, parent->width(), parent->height());
	trackball.resize(parent->width(), parent->height());
}


/// @note Rendering-engine must make camera context current before calling
void NXOpenGLCamera::setNamedView(NXNamedView const& view)
{
	namedView = view;
	glSetPosition();
}


/// Position of the eye in world-space
Vector NXOpenGLCamera::eye(void) const
{
    Vector eyePos;
//     eyePos[0] = -modelViewMatrix[12];
//     eyePos[1] = -modelViewMatrix[13];
//     eyePos[2] = -modelViewMatrix[14];
	/// @todo
    return eyePos;
}


/// Records the mouse-position at the start of drag for trackball rotation
void NXOpenGLCamera::rotateStart(int x, int y)
{
	// cerr << "dragStart @(" << x << ',' << y << ')' << endl;
//     oldMouseX = x;
//     oldMouseY = y;
	trackball.start(x,y);
	oldViewingQuaternion = namedView.getQuat() /*viewingQuaternion*/;
}


/// Updates camera's position when mouse is dragged to (x,y) to rotate the scene
void NXOpenGLCamera::rotate(int x, int y)
{
	trackball.update(x,y);
#if 0
    real oldx = 2.0 * real(oldMouseX) / real(viewport.width()) - 1.0;
    real oldy = 1.0 - 2.0 * real(oldMouseY) / real(viewport.height());

    real newx = 2.0 * real(x) / real(viewport.width()) - 1.0;
    real newy = 1.0 - 2.0 * real(y) / real(viewport.height());
#endif
	
	// cerr << "drag @(" << newx << ',' << newy << ')' << endl;
    
    /*Vector4*/ NXQuaternion<double> dragRotationQuat;
	// trackball(dragRotationQuat, newx, newy, oldx, oldy);
	dragRotationQuat = trackball.getRotationQuat();
	// add_quats(oldViewingQuaternion, dragRotationQuat, viewingQuaternion);
	/*viewingQuaternion =*/ namedView.setQuat(oldViewingQuaternion + dragRotationQuat);
	// buildModelViewMatrix();
	
}


/// Marks the end of mouse-dragging for rotation
void NXOpenGLCamera::rotateStop(int x, int y)
{
	// cerr << "dragStop @(" << x << ',' << y << ')' << endl;
}


void NXOpenGLCamera::panStart(int x, int y)
{
	// cerr << "panStart @(" << x << ',' << y << ')' << endl;
    panInitialWpt = unproject(x,parent->height()-y);
}


void NXOpenGLCamera::pan(int x, int y)
{
	// cerr << "pan @(" << x << ',' << y << ')' << endl;
    NXVector3d panCurrentWpt = unproject(x,parent->height()-y);
    NXVector3d delta = panCurrentWpt - panInitialWpt;
	// translation += delta;
	NXVectorRef3d POV = namedView.getPOV();
	NXVector3d newPOV =  POV + delta;
	namedView.setPOV(newPOV);
	// modelViewMatrix(0,3) = translation[0];
	// modelViewMatrix(1,3) = translation[1];
	// modelViewMatrix(2,3) = translation[2];
	// cerr << "translate by" << delta.x() << ',' << delta.y() << ','
	//     << delta.z() << ')' << endl;
}


void NXOpenGLCamera::panStop(int x, int y)
{
	// cerr << "panStop @(" << x << ',' << y << ')' << endl;
}


void NXOpenGLCamera::advance(int numSteps)
{
	double const& POVDistance = namedView.getPOVDistanceFromEye();
	
	// assuming mouse wheel to have 24 steps per cycle
	// http://doc.trolltech.com/4.2/qwheelevent.html
	// int QWheelEvent::delta () const
	
	double const distanceToAdvance = double(numSteps)/24.0 * POVDistance;
	NXVector3d zDir(0.0, 0.0, 1.0);
	NXQuaternion<double>& quat = namedView.getQuat();
	NXVector3d advanceDirection = quat.unrot(zDir);
	advanceDirection.normalizeSelf();
	NXVector3d advanceVector = distanceToAdvance * advanceDirection;
	NXVectorRef3d POV = namedView.getPOV();
	NXVector3d newPOV = POV - advanceVector;
	namedView.setPOV(newPOV);
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

#if 0
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
//     viewingQuaternion[3] = qw;
//     viewingQuaternion[0] = qx;
//     viewingQuaternion[1] = qy;
//     viewingQuaternion[2] = qz;

	viewingQuaternion = NXQuaternion<double>(qw, qx, qy, qz);
	
    translation[0] = m(0,3);
    translation[1] = m(1,3);
    translation[2] = m(2,3);
}
#endif

#if 0
/// Builds the model-view matrix from translation and rotation info
void NXOpenGLCamera::buildModelViewMatrix(void)
{
	// build_rotmatrix(modelViewMatrix, viewingQuaternion);
	NXMatrix44d tempModelViewMatrix;
	viewingQuaternion.buildMatrix(tempModelViewMatrix);
	NXVectorRef<real,16> modelViewMatrixRef(modelViewMatrix);
	NXVectorRef<double,16> tempModelViewMatrixRef(tempModelViewMatrix.data());
	modelViewMatrixRef.copy(tempModelViewMatrixRef);
    modelViewMatrix(0,3) = translation[0];
    modelViewMatrix(1,3) = translation[1];
    modelViewMatrix(2,3) = translation[2];
}
#endif

/// Applies the camera's world-location and orientation settings to OpenGL
void NXOpenGLCamera::glSetPosition(void)
{
	// modelViewMatrix.glSet(GL_MODELVIEW);
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();
	glTranslated(0.0, 0.0, -namedView.getPOVDistanceFromEye());
	NXQuaternion<double> q = namedView.getQuat();
	double const angle = q.getAngle();
	NXVector<double,3> axis = q.getAxisDirection();
	glRotated(angle * 180.0 / M_PI, axis[0], axis[1], axis[2]);
	NXVectorRef3d POV(namedView.getPOV());
	glTranslated(POV[0], POV[1], POV[2]);
}


/// Applies the camera's projection-settings to OpenGL
/// @note Rendering engine must make context current before calling
void NXOpenGLCamera::glSetProjection(void)
{
//     if(isPerspectiveProjection)
//         perspectiveProjection.glSet();
//     else
//         orthographicProjection.glSet();
	
	double const aspect = double(viewport.width()) / double(viewport.height());
	double const& scale = namedView.getScale();
	double const& vdist = namedView.getPOVDistanceFromEye();
	double const near = NXNamedView::GetNear();
	double const far = NXNamedView::GetFar();
	
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	
	if(isPerspectiveProjection) {
		glFrustum( - scale * near * aspect, scale * near * aspect,
		           - scale * near,          scale * near,
		           vdist * near, vdist * far);
	}
	else {
		glOrtho( - scale * aspect, scale * aspect,
		         - scale,          scale,
		         vdist * near, vdist * far );
	}
}


/// Resizes the camera's viewport and adjusts the projection matrix accordingly
void NXOpenGLCamera::resizeViewport(int w, int h)
{
    viewport.set(0, 0, w, h);
	trackball.resize(w,h);
	// real const aspectRatio = (real)w / (real)h;
    
    // adjust projection matrix
//     if(isPerspectiveProjection) {
//         // projectionMatrix(1,1) = projectionMatrix(0,0) / aspectRatio;
//         perspectiveProjection.aspect = aspectRatio;
//     }
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


#if 0
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
#endif

#if 0
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
#endif

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

#if 0
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
#endif

/// Sets the camera's viewport info and applies it to OpenGL
void NXOpenGLCamera::glViewport(int x, int y, int w, int h)
{
    ::glViewport((GLint) x, (GLint) y, (GLsizei) w, (GLsizei) h);
    viewport = GltViewport(x, y, w, h);
	trackball.resize(w,h);
}


/// To be called from within a current OpenGL context
double NXOpenGLCamera::getPixelDepth(int x, int y)
{
	GLfloat depth;
	glReadPixels((GLint) x, (GLint) y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, &depth);
	return static_cast<double>(depth);
}


/// Unprojects the given (x,y,z), usually mouse coords with z=0, to a
/// world-space point and returns it
NXVector3d NXOpenGLCamera::unproject(int x, int y/*, real z*/)
{
	// real z = getPixelDepth(x,y);
    GLdouble worldX, worldY, worldZ;
    GLdouble temp_projectionMatrix[16];
    glGetDoublev(GL_PROJECTION_MATRIX, temp_projectionMatrix);
	GLdouble temp_modelViewMatrix[16];
	glGetDoublev(GL_MODELVIEW_MATRIX, temp_modelViewMatrix);
	
	gluUnProject(x, y, 0.0,
	             temp_modelViewMatrix,
	             temp_projectionMatrix,
	             viewport,
	             &worldX, &worldY, &worldZ);
	
#ifdef GLT_SINGLE_PRECISION
    // Create temporary store to catch differences in precision
//     GLdouble temp_modelViewMatrix[16];
//     for(int i=0; i<16; ++i) {
//         temp_modelViewMatrix[i] = modelViewMatrix[i];
//     }
//     gluUnProject(x, y, z,
//                  temp_modelViewMatrix,
//                  temp_projectionMatrix,
//                  viewport,
//                  &worldX, &worldY, &worldZ);
#else
//     gluUnProject(x, y, z,
//                  modelViewMatrix,
//                  temp_projectionMatrix,
//                  viewport,
//                  &worldX, &worldY, &worldZ);
#endif
    
    NXVector3d wpt(worldX, worldY, worldZ);
    return wpt;
}
