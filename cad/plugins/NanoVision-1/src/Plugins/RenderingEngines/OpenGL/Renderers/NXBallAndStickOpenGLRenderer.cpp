// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

extern "C" {
#include <GL/gl.h>
}
#include "NXBallAndStickOpenGLRenderer.h"

namespace Nanorex {


double const NXBallAndStickOpenGLRenderer::BOND_WIDTH = 0.1;


NXSGNode* NXBallAndStickOpenGLRenderer::renderAtom(NXAtomRenderData const& info)
{
    std::vector<void const*> const& paramVec = info.getSupplementalData();
    NXOpenGLMaterial const& defaultMaterial =
        *static_cast<NXOpenGLMaterial const*>(paramVec[0]);
    NXSGOpenGLMaterial *atomNode = NULL;
    try { atomNode = new NXSGOpenGLMaterial(defaultMaterial); }
    catch (...) { return NULL; } // fail silently
    
    atomNode->addChild(canonicalSphereNode);
    return atomNode;
    
#if 0 // OpenGL calls, not required
    double theta, rSinTheta, phi, sinPhi, cosPhi;
    double theta2, rSinTheta2;
    GLint iTheta, iPhi;
    GLdouble x,y,z,z1,z2;
    
    const int ALPHA = 5;
    
    GLenum err;
    
    /* Automatic normalization of normals */
    glEnable(GL_NORMALIZE);
    
    /* Top cap - draw triangles instead of quads */
    glBegin(GL_TRIANGLE_FAN);
    /* Top pole */
    glNormal3d(0,0,1);
    glVertex3d(0,0,1);
    theta = ALPHA * M_PI/180.0;
    rSinTheta = sin(theta);
    z = cos(theta);
    
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
        z1 = (GLdouble) (cos(theta));
        z2 = (GLdouble) (cos(theta2));
        rSinTheta = sin(theta);
        rSinTheta2 = sin(theta2);
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
    z = cos(theta);
    rSinTheta = sin(theta);
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
    
#endif
}


NXSGNode* NXBallAndStickOpenGLRenderer::renderBond(NXBondRenderData const& info)
{
    std::vector<void const*> const& paramVec = info.getSupplementalData();
    NXOpenGLMaterial const& defaultMaterial =
        *static_cast<NXOpenGLMaterial const*>(paramVec[0]);
    NXSGOpenGLMaterial *bondNode = NULL;
    try { bondNode = new NXSGOpenGLMaterial(defaultMaterial); }
    catch (...) { return NULL; } // fail silently
    
    bondNode->addChild(canonicalCylinderNode);
    return bondNode;
    
#if 0 // OpenGL calls, already implemented in superclass
    int const NUM_FACETS = 72;
    const int DELTA_PHI = 360.0 / (double) NUM_FACETS;
    GLdouble vertex[NUM_FACETS][2]; // store (x,y) values
    double x=0.0, y=0.0;
    GLdouble const z = 0.5;
    
    // generate vertices
    int iFacet = 0; // counter
    int iPhi = 0;
    double phi = 0.0;
    for(iFacet=0; iFacet<NUM_FACETS; ++iFacet, iPhi+=DELTA_PHI) {
        phi = M_PI/180.0 * (double) iPhi;
#ifdef _GNU_SOURCE
        sincos(phi, &y, &x);
#else
        x = cos(phi);
        y = sin(phi);
#endif
        vertex[iFacet][0] = (GLdouble)(x);
        vertex[iFacet][1] = (GLdouble)(y);
    }
    
    
    NXCommandResult renderResult = bond_node->beginRender();
    /// @todo trap errors - set commandResult
    
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
    
#endif
}

} // Nanorex
