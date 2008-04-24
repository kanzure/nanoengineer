// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_OPENGLRENDERINGENGINE_H
#define NX_OPENGLRENDERINGENGINE_H

#include <set>
#include <list>
#include <vector>
#include <functional>

// #include <QtGui>
#include <QtOpenGL>

#include "GLT/glt_light.h"
#include "GLT/glt_lightm.h"
// #include "glt_material.h"
#include "GLT/glt_vector3.h"
#include "GLT/glt_project.h"
#include "GLT/glt_viewport.h"
#include "GLT/glt_bbox.h"

#include <Nanorex/Interface/NXRenderingEngine.h>
#include <Nanorex/Interface/NXMoleculeSet.h>
#include "Nanorex/Utility/NXRGBColor.h"
#include "NXOpenGLSceneGraph.h"
#include "NXOpenGLRendererPlugin.h"
#include "NXOpenGLCamera.h"


/* CLASS: NXOpenGLRenderingEngine */
/**
  *  Renders the molecule set using plain OpenGL. Can be instantiate for
  *  display of molecules or molecule-sets using the template parameter.
  *
  * \internal This class delegates the actual task of creating scenegraphs
  *  and rendering it to an OpenGL context to the NXOpenGLRenderingEngine_delegate
  *  class. The task of the template parameter is to filter what can be
  *  displayed through this window and much of the rendering part is independent
  *  so maintaining a template-less delegate is better code reuse.
  *
  * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
  */
class NXOpenGLRenderingEngine :
	public QGLWidget,
	public Nanorex::NXRenderingEngine
{
    Q_OBJECT;
	Q_INTERFACES(Nanorex::NXRenderingEngine);

public:
    
    
    NXOpenGLRenderingEngine(QWidget *parent = 0);
    
    virtual ~NXOpenGLRenderingEngine();
    
    // override base-class virtual methods
    
	// RenderingEngineID getID(void) const { return OPENGL; }
    
	QWidget* asQWidget(void) {
		QGLWidget *asQGLWidget = static_cast<QGLWidget*>(this);
		return static_cast<QWidget*>(asQGLWidget);
	}
	
	bool initializePlugins(void);
	
	bool cleanupPlugins(void);
	
	NXRenderingEngine* newInstance(QWidget *parent=0) const;
	
	bool isRendererCompatible(QObject *plugin) const;
	
	// void setCurrentFrame(int frameIdx);
	
	Nanorex::NXRendererPlugin* renderer_cast(QObject *plugin) const;
	
    /// Reset the view based on the atom-bond distribution in the
	/// current frame's molecule-set
	void resetView (void);
	
	void setNamedView(Nanorex::NXNamedView const& view);
	
    // Mouse-event handlers
	void mousePressEvent(QMouseEvent *mouseEvent);
	void mouseReleaseEvent(QMouseEvent *mouseEvent);
	void mouseMoveEvent(QMouseEvent *mouseEvent);
	void wheelEvent(QWheelEvent *event);
    
private:
    
	typedef unsigned int uint;
	
	template<typename T1, typename T2>
		struct PairwiseLess : public binary_function<T1, T2, bool> {
			bool operator () (pair<T1,T2> const& a, pair<T1,T2> const& b) const
			{
				return (a.first < b.first ||
				        (a.first == b.first && a.second < b.second));
			}
		};
    
	NXOpenGLCamera camera;
    
	// bool pluginsInitialized;
    
    // OpenGL settings
	std::vector<GltLight> lights;
	GltLightModel lightModel;
    
    // bool isOrthographicProjection;
    // GltOrtho orthographicProjection;
    // GltFrustum perspectiveProjection;
    // GltViewport viewport;
    
	std::map<uint, Nanorex::NXRGBColor> elementColorMap;
    NXOpenGLMaterial defaultAtomMaterial;
    NXOpenGLMaterial defaultBondMaterial;
	
	typedef set<OBAtom*> RenderedAtomsTableType;
	RenderedAtomsTableType renderedAtoms; // tracks rendered atoms
	
	typedef
		set<pair<OBAtom*,OBAtom*>, PairwiseLess<OBAtom*,OBAtom*> >
		RenderedBondsTableType;
	
	RenderedBondsTableType renderedBonds; // tracks rendered bonds
	
	NXSGOpenGLNode*
		createOpenGLSceneGraph(Nanorex::NXMoleculeSet *const molSetPtr);
	
	NXSGOpenGLNode*
		createOpenGLSceneGraph(OpenBabel::OBMol *const molPtr);
	
	NXSGOpenGLNode*
		createOpenGLSceneGraph(OpenBabel::OBMol *const molPtr,
		                       OpenBabel::OBAtom *const atomPtr,
		                       Vector const& zAxis);
	
#if 0 /// @todo Post-FNANO08
	/// @fixme r1.0.0 hacks
	// -- begin hacks
	/// @todo initialize these in reset()
	bool inDnaGroup, inDnaSegment, inDnaStrand;
	NXMoleculeSet *dnaSegmentMolSetPtr, *dnaStrandMolSetPtr;
	
	NXSGOpenGLNode*
		createOpenGLDnaSegmentSceneGraph(OpenBabel::OBMol *const molPtr);
	
	NXSGOpenGLNode*
		createOpenGLDnaStrandSceneGraph(OpenBabel::OBMol *const molPtr);

	// -- end hacks --
#endif
	
	
	NXSGOpenGLNode* getRotationNode(Vector const& zAxis,
	                                Vector const& newZAxis);
	
    // Implement inherited pure-virtual methods
	Nanorex::NXSGNode*
		createSceneGraph (Nanorex::NXMoleculeSet *const molSetPtr);
	
	bool isRendered(OBAtom *const atomPtr) const;
	bool isRendered(OBBond *const bondPtr) const;
	void markBondRendered(OBBond *const bondPtr);
	
	// NXSGNode* createSceneGraph (OpenBabel::OBMol *const molPtr);
    
    // QGLWidget methods to be overriden
	void initializeGL(void);
	void resizeGL(int width, int height);
	void paintGL(void);
    
	bool initializeElementColorMap(void);
	void initializeDefaultMaterials(void);
	void setupDefaultLights(void);
	void drawSkyBlueBackground(void);
	void drawCompass(void);
	
	// static methods
	BoundingBox GetBoundingBox(Nanorex::NXMoleculeSet *const molSetPtr);
	BoundingBox GetBoundingBox(OpenBabel::OBMol *const molPtr);
	
	friend class NXOpenGLRenderingEngineTest;
	friend class MMPOpenGLRendererTest;
};


inline
Nanorex::NXRenderingEngine*
NXOpenGLRenderingEngine::newInstance(QWidget *parent) const
{
	NXOpenGLRenderingEngine *openGLRenderingEngineInstance =
		new NXOpenGLRenderingEngine(parent);
	return
		static_cast<Nanorex::NXRenderingEngine*>(openGLRenderingEngineInstance);
}


inline
Nanorex::NXRendererPlugin*
NXOpenGLRenderingEngine::renderer_cast(QObject *plugin) const
{
	NXOpenGLRendererPlugin *rendererPlugin =
		qobject_cast<NXOpenGLRendererPlugin*>(plugin);
	return
		static_cast<Nanorex::NXRendererPlugin*>(rendererPlugin);
}

#if 0
inline void NXOpenGLRenderingEngine::setCurrentFrame(int frameIdx)
{
	if(frameIdx < (int)frames.size()) {
		currentFrameIndex = frameIdx;
		resetView();
	}
}
#endif

#endif // NX_OPENGLRENDERINGENGINE_H
