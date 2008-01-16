// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_RENDERERPLUGIN_H
#define NX_RENDERERPLUGIN_H


namespace Nanorex {

/* CLASS: NXRendererPlugin */
/**
 * Base class for all rendering plugins
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXRendererPlugin {
public:
    NXRendererPlugin();
    ~NXRendererPlugin();

    // virtual void renderAtom(NXRenderAtomInfo const&) = 0;
    // virtual void renderBond(NXRenderBondInfo const&) = 0;
};


} // Nanorex


#endif // NX_RENDERERPLUGIN_H
