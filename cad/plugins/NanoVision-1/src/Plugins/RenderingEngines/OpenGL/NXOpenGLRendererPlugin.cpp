// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <GL/gl.h>
#include "Nanorex/Interface/NXOpenGLRendererPlugin.h"

namespace Nanorex {


NXSGOpenGLRenderable *NXOpenGLRendererPlugin::canonicalSphereNode(NULL);
NXSGOpenGLRenderable *NXOpenGLRendererPlugin::canonicalCylinderNode(NULL);

NXOpenGLRendererPlugin::NXOpenGLRendererPlugin()
{
    if(canonicalSphereNode == NULL)
        renderCanonicalSphere();
    
    if(canonicalCylinderNode == NULL)
        renderCanonicalCylinder();
    
#if 0
    if(canonicalSphereDisplayListID == 0)
        renderCanonicalSphere();
    
    if(canonicalCylinderDisplayListID == 0)
        renderCanonicalCylinder();
#endif
}


/// Developer should check for canonicalSphereNode == NULL before calling
/*static*/ void NXOpenGLRendererPlugin::renderCanonicalSphere(void)
{
    // canonicalSphereDisplayListID = glGenLists(1);
    try {
        canonicalSphereNode = new NXSGOpenGLRenderable;
    }
    catch (...) {
        // fail silently if unable to create for any reason
        delete canonicalSphereNode;
        canonicalSphereNode = NULL;
        return;
    }
    
    
    NXCommandResult renderResult = canonicalSphereNode->beginRender();
    /// @todo trap results - return if error freeing node and setting ptr to NULL
    
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
    
    renderResult = canonicalSphereNode->endRender();
    /// @todo - trap errors, free node, set to zero and return
    
    
/*    GLenum const err = glGetError();
    if(err != GL_NO_ERROR) {
        canonicalSphereDisplayListID = 0;
        /// @todo set commandResult
    }*/
}


/// Developer should check for canonicalCylinderNode == NULL before calling
/*static*/ void NXOpenGLRendererPlugin::renderCanonicalCylinder(void)
{
    // canonicalCylinderDisplayListID = glGenLists(1);
    try {
        canonicalCylinderNode = new NXSGOpenGLRenderable;
    }
    catch (...) {
        // fail silently if unable to create for any reason
        delete canonicalCylinderNode;
        canonicalCylinderNode = NULL;
        return;
    }
    
    int const NUM_FACETS = 72;
    const double DELTA_PHI = 360.0 / (double) NUM_FACETS;
    GLdouble vertex[NUM_FACETS][2]; // store (x,y) values
    double x=0.0, y=0.0;
    GLdouble const z = 0.5;
    
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
    
    
    NXCommandResult renderResult = canonicalCylinderNode->beginRender();
    /// @todo trap errors, free node, set to NULL, return

    /* Automatic normalization of normals */
    glEnable(GL_NORMALIZE);
    
    /* Fill polygons */
    glShadeModel(GL_SMOOTH);
    glPolygonMode(GL_FRONT, GL_FILL);
    
    /* Top cap - draw triangles instead of quads */
    glBegin(GL_TRIANGLE_FAN);
    glNormal3d(0,0,1);
    glVertex3d(0.0, 0.0, z);
    for(iFacet=0; iFacet<NUM_FACETS; ++iFacet) {
        glVertex3d(vertex[iFacet][0], vertex[iFacet][1], z);
    }
    // close top-cap
    glVertex3d(vertex[0][0], vertex[0][1], z);
    glEnd();
    
    
    /* Cylinder body - draw triangle strips */
    glBegin(GL_TRIANGLE_STRIP);
    for(iFacet=0; iFacet<NUM_FACETS; ++iFacet) {
        glNormal3d(vertex[iFacet][0], vertex[iFacet][1], 0.0);
        glVertex3d(vertex[iFacet][0], vertex[iFacet][1], z);
        glVertex3d(vertex[iFacet][0], vertex[iFacet][1], -z);
    }
    // close the side surface
    glNormal3d(vertex[0][0], vertex[0][1], 0.0);
    glVertex3d(vertex[0][0], vertex[0][1], z);
    glVertex3d(vertex[0][0], vertex[0][1], -z);
    glEnd();
    
    
    
    /* Bottom cap - draw triangle fan */
    glBegin(GL_TRIANGLE_FAN);
        /* Bottom pole */
    glNormal3d(0,0,-1);
    glVertex3d(0.0, 0.0, -z);
    for(iFacet=0; iFacet<NUM_FACETS; ++iFacet) {
        glVertex3d(vertex[iFacet][0], vertex[iFacet][1], -z);
    }
    // close bottom-cap
    glVertex3d(vertex[0][0], vertex[0][1], -z);
    glEnd();
    
    renderResult = canonicalCylinderNode->endRender();
    /// @todo trap errors, free node, set to NULL, return
    
/*    err = glGetError();
    if(err != GL_NO_ERROR) {
        canonicalCylinderDisplayListID = 0;
            /// @todo set commandResult
    }*/
    
}


} // Nanorex

