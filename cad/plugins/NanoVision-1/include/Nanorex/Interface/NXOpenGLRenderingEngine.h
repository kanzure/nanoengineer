// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_OPENGLRENDERINGENGINE_H
#define NX_OPENGLRENDERINGENGINE_H

#include "NXRenderingEngine.h"
#include "NXSceneGraph.h"
#include "NXOpenGLRendererPlugin.h"

namespace Nanorex {

/* CLASS: NXOpenGLRenderingEngine */
/**
 *  Renders the molecule set using plain OpenGL
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXOpenGLRenderingEngine : public NXRenderingEngine, public QGLWidget {
public:
    
    Q_OBJECT
    
    NXOpenGLRenderingEngine(QWidget *parent = 0)
        : NXRenderingEngine(), QGLWidget(parent), rootSceneGraphNode(NULL) {}
    
    virtual ~NxOpenGLRenderingEngine();

    // override base-class virtual methods
    
    NXRenderingEngine::EngineID getID(void) const { return NXRenderingEngine::OPENGL; }
    
    void initializePlugins(void);
    
    void cleanupPlugins(void);
    
    void setRootMoleculeSet(NXMoleculeSet *const moleculeSet) {
        deleteSceneGraph();
        rootMoleculeSet = moleculeSet;
        createSceneGraph();
    }
    
private:
    
    NXSGNode *rootSceneGraphNode;
    
    typedef std::vector<NXOpenGLRendererPlugin *const> PluginList;
    PluginList pluginList;
    
    void createSceneGraph(void);
    
    void deleteSceneGraph(void) {
        if(rootSceneGraphNode != (NXSGNode*) NULL) {
            rootSceneGraphNode->deleteRecursive();
            delete rootSceneGraphNode;
            rootSceneGraphNode = (NXSGNode*) NULL;
        }
    }
    
    // QGLWidget methods to be overriden
    void initializeGL(void);
    void resizeGL(int width, int height);
    void paintGL(void) { rootSceneGraphNode->applyRecursive(); }
};


} // Nanorex

#endif // NX_OPENGLRENDERINGENGINE_H
