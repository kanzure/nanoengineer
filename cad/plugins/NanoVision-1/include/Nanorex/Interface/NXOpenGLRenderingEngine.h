// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_OPENGLRENDERINGENGINE_H
#define NX_OPENGLRENDERINGENGINE_H

#include "NXRenderingEngine.h"
#include "NXSceneGraph.h"

namespace Nanorex {

/* CLASS: NXOpenGLRenderingEngine */
/**
 *  Renders the molecule set using plain OpenGL
 */
class NXOpenGLRenderingEngine : public NXRenderingEngine, public QGLWidget {
public:
    
    Q_OBJECT
    
    NXOpenGLRenderingEngine();
    virtual ~NxOpenGLRenderingEngine();

    // override base-class virtual methods
    
    NXRenderingEngine::EngineID getID(void) const { return NXRenderingEngine::OPENGL; }
    void initializePlugins(void);
    void cleanupPlugins(void);
    
    // accessors
    
    NXMoleculeSet *const getRootMoleculeSet(void);
    void setRootMoleculeSet(NXMoleculeSet *const moleculeSet);
    
    
private:
    
    NXMoleculeSet *rootMoleculeSet;
    NXSGNode *rootSceneGraphNode;
    
    std::vector<NXRendererPlugin *const> pluginList;
    
    void createSceneGraph(void);

    // QGLWidget methods to be overriden
    void initializeGL(void);
    void resizeGL(int width, int height);
    void paintGL(void) { rootSceneGraphNode->applyRecursive(); }
};


} // Nanorex

#endif // NX_OPENGLRENDERINGENGINE_H
