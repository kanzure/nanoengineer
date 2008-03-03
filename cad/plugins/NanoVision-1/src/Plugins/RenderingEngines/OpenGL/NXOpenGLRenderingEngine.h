// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_OPENGLRENDERINGENGINE_H
#define NX_OPENGLRENDERINGENGINE_H

#include <set>
#include <list>
#include <vector>

#include <QtGui>
#include <QtOpenGL>

#include "glt_light.h"
#include "glt_lightm.h"
// #include "glt_material.h"
#include "glt_vector3.h"
#include "glt_project.h"
#include "glt_viewport.h"

#include "Nanorex/Interface/NXRenderingEngine.h"
#include "Nanorex/Utility/NXRGBColor.h"
#include "NXOpenGLSceneGraph.h"
#include "NXOpenGLRendererPlugin.h"
#include "NXOpenGLCamera.h"

#include <openbabel/mol.h>


namespace Nanorex
{

// fwd decls from NV-1
class NXMoleculeSet;

/* CLASS: NXOpenGLRenderingEngine */
/**
  *  Renders the molecule set using plain OpenGL
  *
  * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
  */
class NXOpenGLRenderingEngine : public QGLWidget, public NXRenderingEngine
{
    Q_OBJECT;
public:
    
    
    NXOpenGLRenderingEngine ( QWidget *parent = 0 );
    
    virtual ~NXOpenGLRenderingEngine();
    
            // override base-class virtual methods
    
    NXRenderingEngine::EngineID getID ( void ) const
    { return NXRenderingEngine::OPENGL; }
    
    bool initializePlugins(void);
    
    bool cleanupPlugins(void);
    
    void setRootMoleculeSet ( NXMoleculeSet *const moleculeSet );
    void setMolecule ( OpenBabel::OBMol *mol );
    
    // Mouse-event handlers
    void mousePressEvent(QMouseEvent *mouseEvent);
    void mouseReleaseEvent(QMouseEvent *mouseEvent);
    void mouseMoveEvent(QMouseEvent *mouseEvent);
    
    bool setRenderer(NXOpenGLRendererPlugin *const plugin);
    
private:
    
    typedef unsigned int uint;
    
    NXOpenGLCamera camera;
    
    NXMoleculeSet *rootMoleculeSet;
    OpenBabel::OBMol *mol;
    bool isSingleMolecule;
    NXSGOpenGLNode *rootSceneGraphNode;
    
/*    typedef std::list<NXOpenGLRendererPlugin*> PluginList;
    PluginList pluginList;
    PluginList::iterator currentPluginIter;*/
    
    NXOpenGLRendererPlugin *renderer;
    bool rendererInitialized;
    
    // OpenGL settings
    std::vector<GltLight> lights;
    GltLightModel lightModel;
    
    // bool isOrthographicProjection;
    // GltOrtho orthographicProjection;
    // GltFrustum perspectiveProjection;
    // GltViewport viewport;
    
    std::map<uint, NXRGBColor> elementColorMap;
    NXOpenGLMaterial defaultAtomMaterial;
    NXOpenGLMaterial defaultBondMaterial;
    
    NXCommandResult commandResult;
    static void SetResult(NXCommandResult cmdResult,
                          int errCode, std::string const& errMsg);
    
    
    
    NXSGOpenGLNode* createSceneGraph ( NXMoleculeSet *const molSetPtr );
    
    NXSGOpenGLNode* createSceneGraph ( OpenBabel::OBMol *const molPtr );
    
    NXSGOpenGLNode* createSceneGraph ( OpenBabel::OBMol *const molPtr,
                                       OpenBabel::OBAtom *const atomPtr,
                                       std::set<OpenBabel::OBAtom*>& renderedAtoms,
                                       Vector const& zAxis );
    
    void deleteSceneGraph ( void )
    {
        if ( rootSceneGraphNode != ( NXSGOpenGLNode* ) NULL )
        {
            rootSceneGraphNode->deleteRecursive();
            delete rootSceneGraphNode;
            rootSceneGraphNode = ( NXSGOpenGLNode* ) NULL;
        }
    }
    
    // QGLWidget methods to be overriden
    void initializeGL(void);
    void resizeGL(int width, int height);
    void paintGL(void);
    
    /// Reset the view based on the atom-bond distribution in the molecule-set
    void resetView (void);
    
    bool initializeElementColorMap(void);
    void initializeDefaultMaterials(void);
    void setupDefaultLights(void);
    void drawSkyBlueBackground(void);
    
    static BoundingBox GetMoleculeSetBoundingBox(NXMoleculeSet *const molSetPtr);
    static BoundingBox GetMoleculeBoundingBox(OpenBabel::OBMol *molPtr);
    
};


} // Nanorex


#endif // NX_OPENGLRENDERINGENGINE_H
