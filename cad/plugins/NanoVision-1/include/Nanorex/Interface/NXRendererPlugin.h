// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_RENDERERPLUGIN_H
#define NX_RENDERERPLUGIN_H

#include <Nanorex/Utility/NXCommandResult.h>

namespace Nanorex {

/* CLASS: NXRendererPlugin */
/**
 * Base class for all rendering plugins
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXRendererPlugin {
public:
    NXRendererPlugin() {}
    virtual ~NXRendererPlugin() {}

    virtual NXCommandResult* initialize() = 0;
    virtual NXCommandResult* cleanup() = 0;
    
    // virtual void renderAtom(NXRenderAtomInfo const&) = 0;
    // virtual void renderBond(NXRenderBondInfo const&) = 0;
};


} // Nanorex


#endif // NX_RENDERERPLUGIN_H
