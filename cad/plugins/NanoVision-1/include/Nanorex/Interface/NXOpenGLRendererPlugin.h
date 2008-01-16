// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_OPENGLRENDERERPLUGIN_H
#define NX_OPENGLRENDERERPLUGIN_H

#include "Nanorex/Interface/NXSceneGraph.h"

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

    /// @todo Declare the NXRenderAtomInfo class
    virtual NXSGNode* renderAtom(NXRenderAtomInfo const&) = 0;

    /// @todo Declare the NXRenderBondInfo class
    virtual NXSGNode* renderBond(NXRenderBondInfo const&) = 0;
};

} // Nanorex

#endif // NX_OPENGLRENDERERPLUGIN_H
