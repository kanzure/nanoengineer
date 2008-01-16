// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include <cassert>
#include "Nanorex/Interface/NXOpenGLRenderingEngine.h"

namespace Nanorex {


void NXOpenGLRenderingEngine::createSceneGraph(void)
{
    assert(rootSceneGraphNode == (NXSGNode*) NULL);
    /// @todo

    // Iterate through the whole molecule
    // For each atom
    // - render atom
    // - look up and render neighbours
    // - build scenegraph
    // Likewise for bonds
}


} // Nanorex
