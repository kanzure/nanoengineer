// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_RENDERER_H
#define NX_RENDERER_H

namespace Nanorex {

/* CLASS: NXRenderer */
/**
 * Abstracts the rendering mechanism.
 * Graphics engines that actually render must inherit the Qt class
 * corresponding to the implementation method. For example, engines
 * that render using OpenGL must inherit this class as well as
 * QGLWidget. An implementation using Irrlicht's software rendering,
 * for example, must inherit QWidget (?) instead because it bypasses
 * OpenGL.
 */
class NXRenderer {
public:

    enum EngineID { OPENGL=0 };

    NXRenderer();
    virtual ~NXRenderer();

    // Query type
    bool isOpenGL(void) const { return (getID() == OPENGL); }

    // Derived classes must override to identify themselves
    EngineID getID(void) const = 0;

    virtual void initializePlugins() = 0;
    virtual void cleanupPlugins() = 0;
};


} // Nanorex

#endif // NX_RENDERER_H
