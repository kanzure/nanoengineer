// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_RENDERINGENGINE_H
#define NX_RENDERINGENGINE_H

#include <Nanorex/Utility/NXCommandResult.h>
#include <Nanorex/Interface/NXSceneGraph.h>
#include <Nanorex/Interface/NXMoleculeSet.h>
#include <Nanorex/Interface/NXNamedView.h>
#include <Nanorex/Interface/NXNanoVisionResultCodes.h>
#include <openbabel/mol.h>
#include <vector>
#include <map>
#include <string>
#include <iostream>
#include <cassert>

#include <QtPlugin>
#include <QtGui>

class QWidget;

namespace Nanorex {

class NXGraphicsManager;
class NXRendererPlugin;

/*
/// integer id for each subclass the completes an implementation
enum RenderingEngineID {
	OPENGL=0 // NXOpenGLRenderingEngine
};
*/


/* CLASS: NXRenderingEngine */
/**
 * Abstracts the rendering mechanism.
 * Graphics engines that actually render must inherit the Qt class
 * corresponding to the implementation method. For example, engines
 * that render using OpenGL must inherit this class as well as
 * QGLWidget. An implementation using Irrlicht's software rendering,
 * for example, must inherit QWidget instead because it bypasses
 * OpenGL.
 *
 * Forms designed using Qt Designer have placeholder widgets for
 * the rendering engines. At instantiation, they will be deleted and a dynamically
 * allocated rendering-engine instance will replace them. At that time, because
 * layout calculations are performed, the rendering-engine class must have the
 * characteristics of a QWidget. Because all rendering-engine instances will be
 * accessed through this interface, we must allow for this interface to appear
 * as a QWidget. Suppose we make QWidget a base class for this interface. Then
 * in cases like the OpenGL engine where QGLWidget must be inherited
 * instead of QWidget an additional subclassing of QGLWidget will only lead to
 * two QWidget subobjects instead of 1 in the derived class. The Qt meta-object
 * compiler then has difficulty handling two QObject subobjects of our derived
 * class. Therefore, derived classes must implement the pure virtual method
 * asQWidget() based on whichever subclass of QWidget they inherit, and must
 * perform the appropriate static_cast
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXRenderingEngine
{
public:
	
	NXRenderingEngine();
	virtual ~NXRenderingEngine();
	
	// --- pure virtual methods ---
	
	/// Derived classes must implement after inheriting an appropriate
	/// subclass of QWidget and after performing an appropriate type-cast
	virtual QWidget* asQWidget(void) = 0;
	
	// /// Derived classes must override to identify themselves
	// virtual RenderingEngineID getID(void) const = 0;
	
	/// Derived classes must override to initialize plugins and set
	/// pluginsInitialized to true if successful. A valid graphics-manager
	/// must be set with setGraphicsManager() before calling this.
	/// importRendererPluginsFromGraphicsManager() may be called to create
	/// new instances of the plugins for various render-styles but the
	/// developer may opt to bypass that perform custom plugin instance creation
	/// here.
	virtual bool initializePlugins() = 0;
	
	/// Derived classes must override to cleanup plugins
	virtual bool cleanupPlugins() = 0;
	
	/// Fully-implemented derived classes have enough information to create a
	/// functioning engine and must return an instance created using the 'new'
	/// operator
	virtual NXRenderingEngine* newInstance(QWidget *parent=0) const = 0;
	
	/// Derived classes must implement and return the result of the qobject_cast
	/// to a compatible plugin-type. If the cast fails then the result is a NULL
	/// pointer which must be checked as failure-condition.
	virtual NXRendererPlugin* renderer_cast(QObject *plugin) const = 0;
	
	// @TODO: consume the events in the following default implementations
	virtual void mousePressEvent(QMouseEvent *mouseEvent) { }
	virtual void mouseReleaseEvent(QMouseEvent *mouseEvent) { }
	virtual void mouseMoveEvent(QMouseEvent *mouseEvent) { }

	// --- regular methods ---
	
	void setGraphicsManager(NXGraphicsManager *const gm) {
		graphicsManager = gm;
	}
	NXGraphicsManager *const getGraphicsManager(void) {
		return graphicsManager;
	}
	
	void setRenderer(std::string const& renderStyleCode,
	                 NXRendererPlugin *const rendererPlugin)
	{
		renderStyleMap[renderStyleCode] = rendererPlugin;
	}
	
	/// Create new instances of plugins local to this context from those in the
	/// graphics-manager. Returns true if successful, false if at least one
	/// plugin instantiation failed.
// 	virtual bool importRendererPluginsFromGraphicsManager(void);
	
	/// Access chemical entity at index idx - returns NULL if not found
	/// which happens if index is out of bounds
	NXMoleculeSet *const getFrame(int idx);
	
	/// Append a molecule-set to the list of frames
	NXCommandResult const *const addFrame(NXMoleculeSet *const molSetPtr);
	
	/// Set the current frame for display - fails silently if out of bounds
	virtual void setCurrentFrame(int frameIdx);
	
	/// Number of frames capable of being displayed
	int getFrameCount(void) const { return frames.size(); }
	
	/// Clear all frame info
	void clearFrames(void) { deleteFrames(); moleculeSets.clear(); }
	
	/// Derived classes can implement to adjust view based on current frame's
	/// molecule-set
	virtual void resetView(void) { }
	
	virtual void setNamedView(NXNamedView const& view) { }
	// virtual NXNamedView const& getNamedView(void) const { }
	
	/// Result of the last command
	NXCommandResult const* getCommandResult(void) const
	{ return &commandResult; }
	
#ifdef NX_DEBUG
	void writeDotGraph(std::ostream& o);
#endif
	
protected:
	
	/// Track renderer-plugins initialized in local context and delete in
	/// destructor
	// std::vector<NXRendererPlugin*> rendererSet;
	
	/// Local map render-style to plugin
	typedef std::map<std::string, NXRendererPlugin*> RenderStyleMap;
	RenderStyleMap renderStyleMap;
	
	NXGraphicsManager *graphicsManager;
	
	// for structure- and trajectory-graphics
	std::vector<NXMoleculeSet*> moleculeSets;
	// for trajectory-graphics
	std::vector<NXSGNode*> frames;
	
	/// Current-frame indexer, initialized to -1
	int currentFrameIndex;
	bool pluginsInitialized;
	
	// NXNamedView namedView; /// @note does this have to be stored?
	
	/// Result of the last public method call
	NXCommandResult commandResult;
	
	/// Derived classes must override to create a scenegraph within local
	/// (graphics) context
	virtual NXSGNode* createSceneGraph(NXMoleculeSet *const molSetPtr) = 0;
	
	void deleteFrames(void);
	
	static void SetResult(NXCommandResult& cmdResult,
	                      int errCode, std::string const& errMsg);
	static void ClearResult(NXCommandResult& cmdResult);
	
	
	/// @todo remove following unused, commented from older drafts
	
#if 0
	/// Access molecule-set at index idx - returns NULL if not found which
	/// happens if index is out of bounds or the engine is rendering single
	/// molecules as indicated by the inSingleMoleculeMode property.
	NXMoleculeSet *const getMoleculeSet(int idx);

	/// Append a molecule-set to the list if !inSingleMoleculeMode
	NXCommandResult* addMoleculeSet(NXMoleculeSet *const molSetPtr);

	/// Access molecule at index idx - returns NULL if not found which
	/// happens if index is out of bounds or the engine is rendering single
	/// molecule-sets as indicated by the !inSingleMoleculeMode property.
	OpenBabel::OBMol *const getMolecule(int idx);

	/// Append a molecule to the list if inSingleMoleculeMode
		NXCommandResult* addMolecule(OpenBabel::OBMol *const molPtr);
#endif	
	
    // NXMoleculeSet *const getRootMoleculeSet(void) { return rootMoleculeSet; }
    // virtual bool setRootMoleculeSet(NXMoleculeSet *const moleculeSet)
    // { rootMoleculeSet = moleculeSet; return true; }
	
    // OpenBabel::OBMol*const getRootMolecule(void) { return rootMolecule; }
    // virtual bool setRootMolecule(OpenBabel::OBMol *const molecule)
    // { rootMolecule = molecule; return true; }
	
};


inline void NXRenderingEngine::deleteFrames(void) {
	std::vector<NXSGNode*>::iterator frameIter;
	for(frameIter=frames.begin(); frameIter!=frames.end(); ++frameIter) {
		NXSGNode *frameTopLevelNode = *frameIter;
		assert(frameTopLevelNode->getRefCount() == 0);
		delete frameTopLevelNode;
	}
	frames.clear();
}

#ifdef NX_DEBUG
inline void NXRenderingEngine::writeDotGraph(std::ostream& o)
{
	vector<NXSGNode*>::const_iterator frameIter;
	for(frameIter = frames.begin(); frameIter != frames.end(); ++frameIter)
		(*frameIter)->writeDotGraph(o);
}
#endif

} // Nanorex

Q_DECLARE_INTERFACE(Nanorex::NXRenderingEngine,
                    "com.Nanorex.Interface.NXRenderingEngine/0.1.0")

#endif // NX_RENDERINGENGINE_H
