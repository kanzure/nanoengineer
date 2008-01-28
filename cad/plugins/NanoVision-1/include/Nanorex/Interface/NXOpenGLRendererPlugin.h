// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_OPENGLRENDERERPLUGIN_H
#define NX_OPENGLRENDERERPLUGIN_H

#include "Nanorex/Interface/NXRendererPlugin.h"
#include "Nanorex/Interface/NXAtomRenderData.h"
#include "Nanorex/Interface/NXBondRenderData.h"
#include "Nanorex/Interface/NXOpenGLSceneGraph.h"

namespace Nanorex {


/* CLASS: NXOpenGLRendererPlugin */
/**
 * Base class for rendering plugins that use OpenGL
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXOpenGLRendererPlugin : public NXRendererPlugin {
public:

    NXOpenGLRendererPlugin();
    virtual ~NXOpenGLRendererPlugin();

    /// Call plugin to render the atom display list and return the scenegraph node.
    /// Must set commandResult to indicate success or failure
    virtual NXSGNode* renderAtom(NXAtomRenderData const&) = 0;
    
    /// Call plugin to render the bond display list and return the scenegraph node.
    /// Must set commandResult to indicate success or failure
    virtual NXSGNode* renderBond(NXBondRenderData const&) = 0;
    
    NXCommandResult const& getCommandResult(void) const { return commandResult; }
    
    // /// Get the OpenGL "name" of the display list for the canonical sphere - 0 if not sphere not created
    // static GLuint const& getCanonicalSphereDisplayListID(void) { return canonicalSphereDisplayListID; }
    
    // /// Get the OpenGL "name" of the display list for the canonical cylinder - 0 if not sphere not created
    // static GLuint const& getCanonicalCylinderDisplayListID(void) { return canonicalCylinderDisplayListID; }
    
protected:
    NXCommandResult commandResult;
    /// @todo should these be NXSGRenderable* instead?
    // static GLuint canonicalSphereDisplayListID = 0;
    // static GLuint canonicalCylinderDisplayListID = 0;
    
    static NXSGOpenGLRenderable *canonicalSphereNode;
    static NXSGOpenGLRenderable *canonicalCylinderNode;
/*    static NXSGRotate* GetVectorAlignmentNode(double const& x1,
                                              double const& y1,
                                              double const& z1,
                                              double const& x2,
                                              double const& y2,
                                              double const& z2);*/
                                              
    /// Initialize canonical sphere scenegraph node for atoms
    static void renderCanonicalSphere(void);
    
    /// Initialize canonical cylinder scenegraph node for bonds
    static void renderCanonicalCylinder(void);
    
};

} // Nanorex

#endif // NX_OPENGLRENDERERPLUGIN_H
