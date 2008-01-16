// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_BALLANDSTICKOPENGLRENDERER_H
#define NX_BALLANDSTICKOPENGLRENDERER_H

#include "Nanorex/Interface/NXOpenGLRendererPlugin.h"

namespace Nanorex {

/* CLASS: BallAndStickOpenGLRenderer */
/**
 * Renders atoms and bonds using balls and sticks
 */
class BallAndStickOpenGLRenderer : public NXOpenGLRendererPlugin {
public:
    BallAndStickOpenGLRenderer();
    virtual ~BallAndStickOpenGLRenderer() {}

    void renderAtom(NXAtomRenderData const&);
    void renderBond(NXBondRenderData const&);
};


} // Nanorex

#endif // NX_BALLANDSTICKOPENGLRENDERER_H
