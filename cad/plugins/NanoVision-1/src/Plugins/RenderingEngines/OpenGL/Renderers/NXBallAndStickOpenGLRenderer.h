// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_BALLANDSTICKOPENGLRENDERER_H
#define NX_BALLANDSTICKOPENGLRENDERER_H

#include <cassert>

extern "C" {
#if defined(__APPLE__)
#include <OpenGL/gl.h>
#else
#include <GL/gl.h>
#endif
}

#include "../NXOpenGLRendererPlugin.h"
#include "Nanorex/Interface/NXAtomRenderData.h"
#include "Nanorex/Interface/NXBondRenderData.h"

namespace Nanorex {


/* CLASS: BallAndStickOpenGLRenderer */
/**
 * Renders atoms and bonds using balls and sticks
 */
class NXBallAndStickOpenGLRenderer : public NXOpenGLRendererPlugin {
public:
    NXBallAndStickOpenGLRenderer() {}
    virtual ~NXBallAndStickOpenGLRenderer() {}

    NXCommandResult* initialize(void);
    NXCommandResult* cleanup(void);
    
    /// Call plugin to render the atom display list and return the scenegraph node.
    /// Must set commandResult to indicate success or failure
    NXSGOpenGLNode* renderAtom(NXAtomRenderData const&);
    
    /// Call plugin to render the atom display list and return the scenegraph node.
    /// Must set commandResult to indicate success or failure
    NXSGOpenGLNode* renderBond(NXBondRenderData const&);
    
    
protected:
    static double const BOND_WIDTH;
    static int const MAX_BONDS = 6;
    static NXSGOpenGLNode *_s_canonicalBondNode[MAX_BONDS];
    
private:
    // the following add the eponymous static pointers above as children so that
    // each initialized instance of NXBallAndStickOpenGLRenderer increments
    // their reference count by 1. So the canonical bond nodes have a min
    // scenegraph count of at least 1 till the last instance is destroyed
    // after which these nodes will be cleaned up
    NXSGNode canonicalBondNodeGuard[MAX_BONDS];
    
    static bool InitializeCanonicalBondNodes(void);
    static void InitializeCanonicalSingleBondNode(void);
    static void InitializeCanonicalDoubleBondNode(void);
    static void InitializeCanonicalTripleBondNode(void);
    static void InitializeCanonicalAromaticBondNode(void);
    static void InitializeCanonicalCarbomericBondNode(void);
    static void InitializeCanonicalGraphiticBondNode(void);
    
    friend class NXBallAndStickOpenGLRendererTest;
};


} // Nanorex

#endif // NX_BALLANDSTICKOPENGLRENDERER_H
