// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_GRAPHICSPLUGIN_H
#define NX_GRAPHICSPLUGIN_H


namespace Nanorex {


class NXRendererPlugin {
public:
    NXRendererPlugin();
    ~NXRendererPlugin();

    void renderAtom(NXRenderAtomInfo const&) = 0;
    void renderBond(NXRenderBondInfo const&) = 0;

};


}


#endif // NX_GRAPHICSPLUGINBASE_H
