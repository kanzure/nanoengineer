 // Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXOpenGLRendererPlugin.h"
#include <Nanorex/Interface/NXNanoVisionResultCodes.h>
#include "GLT/glt_error.h"
#include <sstream>

using namespace std;

namespace Nanorex {

NXCommandResult NXOpenGLRendererPlugin::_s_commandResult;
NXSGOpenGLRenderable *NXOpenGLRendererPlugin::_s_canonicalSphereNode(NULL);
NXSGOpenGLRenderable *NXOpenGLRendererPlugin::_s_canonicalCylinderNode(NULL);


/// Initializes the plugin by rendering the canonical sphere and cylinder
/// Must be called after the calling engine makes its OpenGL context current
NXCommandResult* NXOpenGLRendererPlugin::initialize(void)
{
    InitializeCanonicalSphereNode();
    InitializeCanonicalCylinderNode();
    
    if(_s_canonicalSphereNode == NULL || _s_canonicalCylinderNode == NULL) {
        // copy static context error to instance
        commandResult = _s_commandResult;
        // deallocate which went through
        if(_s_canonicalSphereNode != NULL) {
            delete _s_canonicalSphereNode;
            _s_canonicalSphereNode = NULL;
        }
        if(_s_canonicalCylinderNode != NULL) {
            delete _s_canonicalCylinderNode;
            _s_canonicalCylinderNode = NULL;
        }
        return &commandResult;
    }
    
    
    // assign a minimum ref count of 1. If all nodes that access these canonical
    // nodes as parents cleanup, then these nodes will be deleted when their
    // ref count becomes zero. This initial increment will ensure that the
    // ref count is at least one if all other nodes behave correctly
    canonicalSphereNodeGuard.addChild(_s_canonicalSphereNode);
    canonicalCylinderNodeGuard.addChild(_s_canonicalCylinderNode);
    
    if(_s_canonicalSphereNode->getRefCount() != 1 ||
       _s_canonicalCylinderNode->getRefCount() != 1)
    {
        SetWarning(commandResult,
                   "Reference-counting error in plugin initialization");
    }
    else {
        commandResult.setResult(NX_CMD_SUCCESS);
    }
    return &commandResult;
}


/// Cleanup
NXCommandResult* NXOpenGLRendererPlugin::cleanup(void)
{
    commandResult.setResult(NX_CMD_SUCCESS);
    vector<QString> message;
    commandResult.setParamVector(message);
    
#if 0
    if(_s_canonicalSphereNode != NULL) {
        if(_s_canonicalSphereNode->getRefCount() != 1) {
            SetWarning(commandResult,
                       "Reference-counting audit failed at plugin cleanup");
        }
        delete _s_canonicalSphereNode;
        _s_canonicalSphereNode = NULL;
    }
    
    if(_s_canonicalCylinderNode != NULL) {
        if(_s_canonicalCylinderNode->getRefCount() != 1) {
            SetWarning(commandResult,
                       "Reference-counting audit failed at plugin cleanup");
        }
        delete _s_canonicalCylinderNode;
        _s_canonicalCylinderNode = NULL;
    }
#endif
    return &commandResult;
}



/*static*/
void NXOpenGLRendererPlugin::InitializeCanonicalSphereNode(void)
{
    // quick return if node is already created
    if(_s_canonicalSphereNode != NULL)
        return;
    
    try {
        _s_canonicalSphereNode = new NXSGOpenGLRenderable;
    }
    catch (...) {
        // fail silently if unable to create for any reason
        _s_canonicalSphereNode = NULL;
    }
    
    if(_s_canonicalSphereNode == NULL)
        return;
    
    
    bool beginRenderOK = _s_canonicalSphereNode->beginRender();
    if(!beginRenderOK) {
        NXCommandResult *scenegraphCtxtError = NXSGOpenGLNode::GetCommandResult();
        _s_commandResult.setResult(NX_PLUGIN_REPORTS_ERROR);
        _s_commandResult.setParamVector(scenegraphCtxtError->getParamVector());
        delete _s_canonicalSphereNode;
        _s_canonicalSphereNode = NULL;
        return;
    }
    
    DrawOpenGLCanonicalSphere();
    
    bool const ok = (_s_commandResult.getResult() == (int) NX_CMD_SUCCESS);
    if(!ok) {
        delete _s_canonicalSphereNode;
        _s_canonicalSphereNode = NULL;
        return;
    }
    
    bool endRenderOK = _s_canonicalSphereNode->endRender();
    if(!endRenderOK) {
        NXCommandResult *scenegraphCtxtError = NXSGOpenGLNode::GetCommandResult();
        _s_commandResult.setResult(NX_PLUGIN_REPORTS_ERROR);
        _s_commandResult.setParamVector(scenegraphCtxtError->getParamVector());
        delete _s_canonicalSphereNode;
        _s_canonicalSphereNode = NULL;
    }

}


/*static*/
void NXOpenGLRendererPlugin::InitializeCanonicalCylinderNode(void)
{
    // quick return if already initialized
    if(_s_canonicalCylinderNode != NULL)
        return;
    
    try {
        _s_canonicalCylinderNode = new NXSGOpenGLRenderable;
    }
    catch (...) {
        // fail silently if unable to create for any reason
        _s_canonicalCylinderNode = NULL;
    }
    
    // extra check for NULL before performing ops on it
    if(_s_canonicalCylinderNode == NULL)
        return;
    
    bool beginRenderOK = _s_canonicalCylinderNode->beginRender();
    if(!beginRenderOK) {
        NXCommandResult *scenegraphCtxtError = NXSGOpenGLNode::GetCommandResult();
        _s_commandResult.setResult(NX_PLUGIN_REPORTS_ERROR);
        _s_commandResult.setParamVector(scenegraphCtxtError->getParamVector());
        delete _s_canonicalCylinderNode;
        _s_canonicalCylinderNode = NULL;
        return;
    }
    
    
    DrawOpenGLCanonicalCylinder();
    
    bool const ok = (_s_commandResult.getResult() == (int) NX_CMD_SUCCESS);
    if(!ok) {
        delete _s_canonicalCylinderNode;
        _s_canonicalCylinderNode = NULL;
        return;
    }
    
    
    bool endRenderOK = _s_canonicalCylinderNode->endRender();
    if(!endRenderOK) {
        NXCommandResult *scenegraphCtxtError = NXSGOpenGLNode::GetCommandResult();
        _s_commandResult.setResult(NX_PLUGIN_REPORTS_ERROR);
        _s_commandResult.setParamVector(scenegraphCtxtError->getParamVector());
        delete _s_canonicalCylinderNode;
        _s_canonicalCylinderNode = NULL;
    }
}


void NXOpenGLRendererPlugin::SetError(NXCommandResult& commandResult,
                                      char const *const errMsg)
{
    commandResult.setResult(NX_PLUGIN_REPORTS_ERROR);
    vector<QString> message;
    message.push_back(QObject::tr(errMsg));
    commandResult.setParamVector(message);
}


void NXOpenGLRendererPlugin::SetWarning(NXCommandResult& commandResult,
                                        char const *const warnMsg)
{
    commandResult.setResult(NX_PLUGIN_REPORTS_WARNING);
    vector<QString> message;
    message.push_back(QObject::tr(warnMsg));
    commandResult.setParamVector(message);
}


/* static */
void NXOpenGLRendererPlugin::DrawOpenGLCanonicalSphere(void)
{
    const double r = 1.0; /* radius */
    double theta, rSinTheta, phi, sinPhi, cosPhi;
    double theta2, rSinTheta2;
    GLint iTheta, iPhi;
    GLdouble x,y,z,z1,z2;

    const int ALPHA = 5;

    /* Automatic normalization of normals */
    glEnable(GL_NORMALIZE);

    /* Top cap - draw triangles instead of quads */
    glBegin(GL_TRIANGLE_FAN);
    /* Top pole */
    glNormal3d(0,0,1);
    glVertex3d(0,0,r);
    theta = ALPHA * M_PI/180.0;
    rSinTheta = r*sin(theta);
    z = r*cos(theta);

    for(iPhi = 0; iPhi <= 360; iPhi += ALPHA) {
        phi = M_PI/180.0 * (GLdouble) iPhi;
        x = rSinTheta*cos(phi);
        y = rSinTheta*sin(phi);
        /* normal to point on sphere is ray from center to point */
        glNormal3d(x, y, z);
        glVertex3d(x, y, z);
    }
    glEnd();

    /* Sphere body - draw quad strips */
    for(iTheta = ALPHA; iTheta <= 180-(2*ALPHA); iTheta += ALPHA) {
        theta = M_PI/180.0 * (double) iTheta;
        theta2 = M_PI/180.0 * (double) (iTheta+10);
        z1 = (GLdouble) (r*cos(theta));
        z2 = (GLdouble) (r*cos(theta2));
        rSinTheta = r*sin(theta);
        rSinTheta2 = r*sin(theta2);
        glBegin(GL_QUAD_STRIP);
        for(iPhi = 0; iPhi <= 360; iPhi += 10) {
            phi = M_PI/180.00 * (double)(iPhi);
            cosPhi = cos(phi);
            sinPhi = sin(phi);
            x = (GLdouble) (rSinTheta*cosPhi);
            y = (GLdouble) (rSinTheta*sinPhi);
            glNormal3d(x, y, z1);
            glVertex3d(x, y, z1);
            x = (GLdouble) (rSinTheta2*cosPhi);
            y = (GLdouble) (rSinTheta2*sinPhi);
            glNormal3d(x, y, z2);
            glVertex3d(x, y, z2);
        }
        glEnd();
    }

    /* Bottom cap - draw triangle fan */
    iTheta = 180-ALPHA;
    theta = M_PI/180.0 * (GLdouble) iTheta;
    z = r*cos(theta);
    rSinTheta = r*sin(theta);
    glBegin(GL_TRIANGLE_FAN);
    /* Bottom pole */
    glNormal3d(0,0,-1);
    glVertex3d(0,0,-r);
    for(iPhi = 0; iPhi <= 360; iPhi += ALPHA) {
        phi = M_PI/180.0 * (GLdouble) iPhi;
        x = rSinTheta*cos(phi);
        y = rSinTheta*sin(phi);
        glNormal3d(x, y, z);
        glVertex3d(x, y, z);
    }
    glEnd();
    
    
    ostringstream errMsgStream;
    GLenum const err = GLERROR(errMsgStream);
    if(err == GL_NO_ERROR) {
        _s_commandResult.setResult(NX_CMD_SUCCESS);
    }
    else {
        SetError(_s_commandResult,
                 ("Error drawing openGL unit sphere"+errMsgStream.str()).c_str());
    }
}


void NXOpenGLRendererPlugin::DrawOpenGLCanonicalCylinder(void)
{
    int const NUM_FACETS = 72;
    const double DELTA_PHI = 360.0 / (double) NUM_FACETS;
    GLdouble vertex[NUM_FACETS][2]; // store (x,y) values
    double x=0.0, y=0.0;
    // GLdouble const z = 0.5;
    
    // generate vertices
    int iFacet = 0; // counter
    double phi = 0.0;
    for(iFacet=0; iFacet<NUM_FACETS; ++iFacet, phi+=DELTA_PHI) {
        double const phi_rad = M_PI/180.0 * phi;
#ifdef _GNU_SOURCE
        sincos(phi_rad, &y, &x);
#else
        x = cos(phi_rad);
        y = sin(phi_rad);
#endif
        vertex[iFacet][0] = (GLdouble)(x);
        vertex[iFacet][1] = (GLdouble)(y);
    }
    
    
    /* Automatic normalization of normals */
    glEnable(GL_NORMALIZE);
    
    /* Fill polygons */
    glShadeModel(GL_SMOOTH);
    glPolygonMode(GL_FRONT, GL_FILL);
    
    /* Top cap - draw triangles instead of quads */
    glBegin(GL_TRIANGLE_FAN);
    glNormal3d(0,0,1);
    glVertex3d(0.0, 0.0, 1.0);
    for(iFacet=0; iFacet<NUM_FACETS; ++iFacet) {
        glVertex3d(vertex[iFacet][0], vertex[iFacet][1], 1.0);
    }
    // close top-cap
    glVertex3d(vertex[0][0], vertex[0][1], 1.0);
    glEnd();
    
    
    /* Cylinder body - draw triangle strips */
    glBegin(GL_TRIANGLE_STRIP);
    for(iFacet=0; iFacet<NUM_FACETS; ++iFacet) {
        glNormal3d(vertex[iFacet][0], vertex[iFacet][1], 0.0);
        glVertex3d(vertex[iFacet][0], vertex[iFacet][1], 1.0);
        glVertex3d(vertex[iFacet][0], vertex[iFacet][1], 0.0);
    }
    // close the side surface
    glNormal3d(vertex[0][0], vertex[0][1], 0.0);
    glVertex3d(vertex[0][0], vertex[0][1], 1.0);
    glVertex3d(vertex[0][0], vertex[0][1], 0.0);
    glEnd();
    
    
    
    /* Bottom cap - draw triangle fan */
    glBegin(GL_TRIANGLE_FAN);
        /* Bottom pole */
    glNormal3d(0,0,-1);
    glVertex3d(0.0, 0.0, 0.0);
    for(iFacet=0; iFacet<NUM_FACETS; ++iFacet) {
        glVertex3d(vertex[iFacet][0], vertex[iFacet][1], 0.0);
    }
    // close bottom-cap
    glVertex3d(vertex[0][0], vertex[0][1], 0.0);
    glEnd();
    
    
    ostringstream errMsgStream;
    GLenum const err = GLERROR(errMsgStream);
    if(err == GL_NO_ERROR) {
        _s_commandResult.setResult(NX_CMD_SUCCESS);
    }
    else {
        SetError(_s_commandResult,
                 ("Error drawing openGL unit cylinder"+errMsgStream.str()).c_str());
    }
}

} // Nanorex

