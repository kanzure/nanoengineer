// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_OPENGLRENDERERPLUGIN_H
#define NX_OPENGLRENDERERPLUGIN_H

#if defined(__APPLE__)
#include <OpenGL/gl.h>
#else
#include <GL/gl.h>
#endif

#include "Nanorex/Interface/NXRendererPlugin.h"
#include "Nanorex/Interface/NXAtomData.h"
#include "Nanorex/Interface/NXBondData.h"
#include "Nanorex/Utility/NXCommandResult.h"
#include "NXOpenGLSceneGraph.h"

class NXOpenGLRenderingEngine;

/* CLASS: NXOpenGLRendererPlugin */
/**
 * Base class for rendering plugins that use OpenGL
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXOpenGLRendererPlugin
: public QObject, public Nanorex::NXRendererPlugin
{
	Q_OBJECT;
	Q_INTERFACES(Nanorex::NXRendererPlugin);
	
public:

	NXOpenGLRendererPlugin(Nanorex::NXRenderingEngine *parent = NULL);
	virtual ~NXOpenGLRendererPlugin() {}
    
	/// Derived classes must implement.
    /// Call to render the atom display list and return the scenegraph node.
	/// Must set commandResult to indicate success or failure.
	virtual NXSGOpenGLNode* renderAtom(Nanorex::NXAtomData const&) = 0;
    
	/// Derived classes must implement.
    /// Call to render the bond display list and return the scenegraph node.
    /// Must set commandResult to indicate success or failure.
	virtual NXSGOpenGLNode* renderBond(Nanorex::NXBondData const&) = 0;
	
#if 0 /// @todo Post-FNANO08
	/// @fixme r1.0.0 hacks
	// -- begin hacks --
	virtual NXSGOpenGLNode* renderDnaSegment(/*TODO*/) = 0;
	virtual NXSGOpenGLNode* renderDnaStrand(/*TODO*/) = 0;
	// -- end hacks --
#endif
};

// .............................................................................

/* CONSTRUCTOR */
inline
NXOpenGLRendererPlugin::
NXOpenGLRendererPlugin(Nanorex::NXRenderingEngine *parentEngine)
: QObject(),
Nanorex::NXRendererPlugin(parentEngine)
{
}


Q_DECLARE_INTERFACE(NXOpenGLRendererPlugin,
                    "com.Nanorex.Plugins.RenderingEngines.OpenGL."
                    "NXOpenGLRendererPlugin/0.1.0")

#endif // NX_OPENGLRENDERERPLUGIN_H
