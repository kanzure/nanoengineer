// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_BALLANDSTICKOPENGLRENDERER_H
#define NX_BALLANDSTICKOPENGLRENDERER_H

#include "Nanorex/Interface/NXOpenGLRendererPlugin.h"
#include "Nanorex/Interface/NXAtomRenderData.h"
#include "Nanorex/Interface/NXBondRenderData.h"

namespace Nanorex {


/* CLASS: BallAndStickOpenGLRenderer */
/**
 * Renders atoms and bonds using balls and sticks
 */
class BallAndStickOpenGLRenderer : public NXOpenGLRendererPlugin {
public:
    BallAndStickOpenGLRenderer();
    virtual ~BallAndStickOpenGLRenderer() {}

    /// Call plugin to render the atom display list and return the scenegraph node.
    /// Must set commandResult to indicate success or failure
    NXSGNode* renderAtom(NXAtomRenderData const&);
    
    /// Call plugin to render the atom display list and return the scenegraph node.
    /// Must set commandResult to indicate success or failure
    NXSGNode* renderBond(NXBondRenderData const&);
    
private:
    static double const BOND_WIDTH;
};


} // Nanorex

#endif // NX_BALLANDSTICKOPENGLRENDERER_H
