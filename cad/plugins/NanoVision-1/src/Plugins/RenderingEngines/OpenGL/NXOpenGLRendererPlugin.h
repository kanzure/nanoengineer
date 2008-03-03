// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_OPENGLRENDERERPLUGIN_H
#define NX_OPENGLRENDERERPLUGIN_H

#if defined(__APPLE__)
#include <OpenGL/gl.h>
#else
#include <GL/gl.h>
#endif

#include "Nanorex/Interface/NXRendererPlugin.h"
#include "Nanorex/Interface/NXAtomRenderData.h"
#include "Nanorex/Interface/NXBondRenderData.h"
#include "NXOpenGLSceneGraph.h"

namespace Nanorex {


/* CLASS: NXOpenGLRendererPlugin */
/**
 * Base class for rendering plugins that use OpenGL
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXOpenGLRendererPlugin : public NXRendererPlugin {
public:

    NXOpenGLRendererPlugin() {}
    virtual ~NXOpenGLRendererPlugin() {}
    
    NXCommandResult* initialize(void);
    NXCommandResult* cleanup(void);

    /// Call plugin to render the atom display list and return the scenegraph node.
    /// Must set commandResult to indicate success or failure
    NXSGOpenGLNode* renderAtom(NXAtomRenderData const&);
    
    /// Call plugin to render the bond display list and return the scenegraph node.
    /// Must set commandResult to indicate success or failure
    NXSGOpenGLNode* renderBond(NXBondRenderData const&);
    
    NXCommandResult const& getCommandResult(void) const { return commandResult; }
    
protected:
    
    /// Initialize canonical sphere scenegraph node for atoms
    /// Returns NULL if unsuccessful
    // static NXSGOpenGLRenderable *const GetCanonicalSphereNode(void);
    
    /// Initialize canonical cylinder scenegraph node for bonds
    /// Returns NULL if unsuccessful
    // static NXSGOpenGLRenderable *const GetCanonicalCylinderNode(void);
    
    NXCommandResult commandResult;
    static NXCommandResult _s_commandResult;
    static void SetError(NXCommandResult& cmdResult, char const *const errMsg);
    static void SetWarning(NXCommandResult& cmResult, char const *const warnMsg);
    
    static NXSGOpenGLRenderable *_s_canonicalSphereNode;
    static NXSGOpenGLRenderable *_s_canonicalCylinderNode;
    
private:
    NXSGNode canonicalSphereNodeGuard;
    static void InitializeCanonicalSphereNode(void);
    static void DrawOpenGLCanonicalSphere(void);
    
    NXSGNode canonicalCylinderNodeGuard;
    static void InitializeCanonicalCylinderNode(void);
    static void DrawOpenGLCanonicalCylinder(void);
};

} // Nanorex

#endif // NX_OPENGLRENDERERPLUGIN_H
