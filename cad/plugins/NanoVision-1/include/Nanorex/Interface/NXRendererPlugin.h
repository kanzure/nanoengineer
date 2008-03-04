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

    /// Initialize the plugin, for example when its rendering context is ready
    virtual NXCommandResult* initialize() = 0;
    
    /// Cleanup the plugin. Must be called before deleting the object.
    /// Implements a cleanup mechanism in parallel to the destructor.
    /// This is necessary because the ability to cleanup may depend on external
    /// circumstances, like the availability of a certain resource like a
    /// rendering/drawing context. Subclasses must call <baseclass>::cleanup()
    virtual NXCommandResult* cleanup() = 0;
};


} // Nanorex


#endif // NX_RENDERERPLUGIN_H
