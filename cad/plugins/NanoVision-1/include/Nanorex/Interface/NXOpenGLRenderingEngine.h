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
#include "Nanorex/Interface/NXRGBColor.h"
#include "Nanorex/Interface/NXSceneGraph.h"
#include "Nanorex/Interface/NXOpenGLRendererPlugin.h"

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
public:
    
    Q_OBJECT
        
        NXOpenGLRenderingEngine ( QWidget *parent = 0 );
    
    virtual ~NXOpenGLRenderingEngine();
    
            // override base-class virtual methods
    
    NXRenderingEngine::EngineID getID ( void ) const
    { return NXRenderingEngine::OPENGL; }
    
    void initializePlugins ( void );
    
    void cleanupPlugins ( void );
    
    void setRootMoleculeSet ( NXMoleculeSet *const moleculeSet )
    {
        deleteSceneGraph();
        rootMoleculeSet = moleculeSet;
        rootSceneGraphNode = createSceneGraph ( rootMoleculeSet );
    }
    
            /// Reset the view based on the atom-bond distribution in the
            /// molecule-set
    void resetView ( void );
    
#ifdef NX_DEBUG
    void setPlugin ( NXOpenGLRendererPlugin *const plugin )
    {
        pluginList.push_back ( plugin );
        currentPluginIter = pluginList.rbegin();
    }
#endif
    
private:
    
    typedef unsigned int uint;
    
    NXMoleculeSet *rootMoleculeSet;
    NXSGNode *rootSceneGraphNode;
    
    typedef std::list<NXOpenGLRendererPlugin*> PluginList;
    PluginList pluginList;
    PluginList::iterator currentPluginIter;
    
            // OpenGL settings
    std::vector<GltLight> lights;
    GltLightModel lightModel;
    
    bool isOrthographicProjection;
    GltOrtho orthographicProjection;
    GltFrustum perspectiveProjection;
    GltViewport viewport;
    
    std::map<uint, NXRGBColor> elementColorMap;
    NXOpenGLMaterial defaultAtomMaterial;
    NXOpenGLMaterial defaultBondMaterial;
    
    NXSGNode* createSceneGraph ( NXMoleculeSet *const molSetPtr );
    
    NXSGNode* createSceneGraph ( OpenBabel::OBMol *const molPtr );
    
    NXSGNode* createSceneGraph ( OpenBabel::OBMol *const molPtr,
                                 OpenBabel::OBAtom *const atomPtr,
                                 std::set<OpenBabel::OBAtom*>& renderedAtoms,
                                 Vector const& zAxis );
    
    void deleteSceneGraph ( void )
    {
        if ( rootSceneGraphNode != ( NXSGNode* ) NULL )
        {
            rootSceneGraphNode->deleteRecursive();
            delete rootSceneGraphNode;
            rootSceneGraphNode = ( NXSGNode* ) NULL;
        }
    }
    
            // QGLWidget methods to be overriden
    void initializeGL ( void );
    void resizeGL ( int width, int height );
    void paintGL ( void );
    
    bool initializeElementColorMap();
    void initializeDefaultMaterials();
    void setupDefaultLights ( void );
    void drawSkyBlueBackground ( void );
    
    static BoundingBox
        GetMoleculeSetBoundingBox ( NXMoleculeSet *const molSetPtr );
    static BoundingBox GetMoleculeBoundingBox ( OpenBabel::OBMol *molPtr );
    
};


} // Nanorex


#endif // NX_OPENGLRENDERINGENGINE_H
