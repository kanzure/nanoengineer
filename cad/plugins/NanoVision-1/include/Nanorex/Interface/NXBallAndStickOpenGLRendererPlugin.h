// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_BALLANDSTICKOPENGLRENDERERPLUGIN_H
#define NX_BALLANDSTICKOPENGLRENDERERPLUGIN_H

namespace Nanorex {

/* CLASS: BallAndStickOpenGLRendererPlugin */
/**
 * Renders atoms and bonds using balls and sticks
 */
class BallAndStickOpenGLRendererPlugin : public NXOpenGLRendererPlugin {
public:
    BallAndStickOpenGLRendererPlugin();
    virtual ~BallAndStickOpenGLRendererPlugin() {}

    void renderAtom(NXRenderAtomInfo const&);
    void renderBond(NXRenderBondInfo const&);
};


} // Nanorex

#endif // NX_BALLANDSTICKOPENGLRENDERERPLUGIN_H
