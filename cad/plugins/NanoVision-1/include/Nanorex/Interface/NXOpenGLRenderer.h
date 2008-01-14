// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_OPENGLGRAPHICSENGINE_H
#define NX_OPENGLGRAPHICSENGINE_H

#include "NXRenderer.h"
#include "NXSceneGraph.h"

namespace Nanorex {

/* CLASS: NXOpenGLRenderer */
/**
 *  Renders the molecule set using plain OpenGL
 */
class NXOpenGLRenderer : public NXRenderer, public QGLWidget {
public:
    
    Q_OBJECT
    
    NXOpenGLRenderer();
    virtual ~NxOpenGLRenderer();

    // override base-class virtual methods
    
    NXRenderer::EngineID getID(void) const { return NXRenderer::OPENGL; }
    void initializePlugins(void);
    void cleanupPlugins(void);
    
    NXMoleculeSet *const getRootMoleculeSet(void);
    void setRootMoleculeSet(NXMoleculeSet *const moleculeSet);
    
    
private:
    
    NXMoleculeSet *rootMoleculeSet;
    NXSGNode *rootSceneGraphNode;
    
    std::vector<NXRenderingPlugin *const> pluginList;
    
    void createSceneGraph(void);

    // QGLWidget methods to be overriden
    void initializeGL(void);
    void resizeGL(void);
    void paintGL(void) { rootSceneGraphNode->applyRecursive(); }
};


} // Nanorex

#endif // NX_OPENGLGRAPHICSENGINE_H
