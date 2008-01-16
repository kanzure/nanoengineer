// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_RENDERINGENGINE_H
#define NX_RENDERINGENGINE_H

namespace Nanorex {

/* CLASS: NXRenderingEngine */
/**
 * Abstracts the rendering mechanism.
 * Graphics engines that actually render must inherit the Qt class
 * corresponding to the implementation method. For example, engines
 * that render using OpenGL must inherit this class as well as
 * QGLWidget. An implementation using Irrlicht's software rendering,
 * for example, must inherit QWidget (?) instead because it bypasses
 * OpenGL.
 */
class NXRenderingEngine {
public:
    
    // integer id for each engine - one per subclass
    enum EngineID { OPENGL=0 };

    NXRenderingEngine();
    virtual ~NXRenderingEngine();

    // Query type - one per subclass, suitably named
    bool isOpenGL(void) const { return (getID() == OPENGL); }

    // Derived classes must override to identify themselves
    EngineID getID(void) const = 0;

    virtual void initializePlugins() = 0;
    virtual void cleanupPlugins() = 0;
};


} // Nanorex

#endif // NX_RENDERINGENGINE_H
