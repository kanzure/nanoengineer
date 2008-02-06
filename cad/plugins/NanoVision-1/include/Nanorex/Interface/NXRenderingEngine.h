// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_RENDERINGENGINE_H
#define NX_RENDERINGENGINE_H

namespace Nanorex {

class NXMoleculeSet;


/* CLASS: NXRenderingEngine */
/**
 * Abstracts the rendering mechanism.
 * Graphics engines that actually render must inherit the Qt class
 * corresponding to the implementation method. For example, engines
 * that render using OpenGL must inherit this class as well as
 * QGLWidget. An implementation using Irrlicht's software rendering,
 * for example, must inherit QWidget (?) instead because it bypasses
 * OpenGL.
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXRenderingEngine {
public:
    
    // integer id for each engine - one per subclass
    enum EngineID { OPENGL=0 };

    NXRenderingEngine() : rootMoleculeSet(NULL) {}
    virtual ~NXRenderingEngine() {}

    // Query type - one per subclass, suitably named
    bool isOpenGL(void) const { return (getID() == OPENGL); }

    // Derived classes must override to identify themselves
    virtual EngineID getID(void) const = 0;

    virtual void initializePlugins() = 0;
    virtual void cleanupPlugins() = 0;
    
    // accessors
    
    NXMoleculeSet *const getRootMoleculeSet(void) { return rootMoleculeSet; }
    virtual void setRootMoleculeSet(NXMoleculeSet *const moleculeSet)
    { rootMoleculeSet = moleculeSet; }
    
protected:
    
    NXMoleculeSet *rootMoleculeSet;
    
};


} // Nanorex

#endif // NX_RENDERINGENGINE_H
