// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_SCENEGRAPH_OPENGL_H
#define NX_SCENEGRAPH_OPENGL_H

// Scenegraph classes for OpenGL

#include "Nanorex/Interface/NXSceneGraph.h"
#include "Nanorex/Interface/NXOpenGLMaterial.h"
#include "Nanorex/Utility/NXUtility.h"
#include "Nanorex/Utility/NXCommandResult.h"


namespace Nanorex {


/* CLASS NXSGOpenGLTranslate */
/**
 * Base class for OpenGL transforms
 * Re-implements the applyRecursive() method so that it pushes the modelview
 * matrix before applying the scenegraph subtree, and pops the modelview
 * matrix afterwards.
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGOpenGLTransform : public NXSGNode {
public:
    NXSGOpenGLTransform() throw () {}
    ~NXSGOpenGLTransform() throw () {}
    bool applyRecursive(void) const throw();
};


/* CLASS NXSGOpenGLTranslate */
/**
 * OpenGL translation node
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGOpenGLTranslate : public NXSGOpenGLTransform {
public:
    NXSGOpenGLTranslate(double const& the_x,
                        double const& the_y,
                        double const& the_z) throw ()
        : x(the_x), y(the_y), z(the_z) {}
    ~NXSGOpenGLTranslate() throw () {}
    bool apply(void) const throw ();
private:
    GLdouble x, y, z;
};



/* CLASS: NXSGOpenGLRotate */
/**
 * Scenegraph rotation node
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGOpenGLRotate : public NXSGOpenGLTransform {
public:
    NXSGOpenGLRotate(double const& the_angle,
                     double const& the_x,
                     double const& the_y,
                     double const& the_z) throw ()
        : angle(the_angle), x(the_x), y(the_y), z(the_z) {}
    ~NXSGOpenGLRotate() throw () {}
    bool apply(void) const throw ();
private:
    GLdouble angle, x, y, z;
};


/* CLASS: NXSGOpenGLScale */
/**
 * Scenegraph scaling node
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGOpenGLScale : public NXSGOpenGLTransform {
public:
    NXSGOpenGLScale(double const& the_x,
                    double const& the_y,
                    double const& the_z) throw ()
        : x(the_x), y(the_y), z(the_z)  {}
    ~NXSGOpenGLScale() throw () {}
    bool apply(void) const throw ();
private:
    GLdouble x, y, z;
};


#if 0 // unused class - commented out
/* CLASS: NXSGOpenGLGenericTransform */
/**
 * Generic OpenGL transform
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGOpenGLGenericTransform : public NXSGOpenGLTransform {

public:
    NXSGOpenGLGenericTransform() throw () {}
    ~NXSGOpenGLGenericTransform() throw () {}

    bool apply(void) const throw();

private:
    GLdouble matrix[16];

    void zero() { for(int i=0; i<16; ++i) matrix[i] = 0.0; }
    void identity() { zero(); matrix[0] = matrix[5] = matrix[10] = matrix[15] =
1.0; }
};
#endif


/* CLASS NXSGOpenGLRenderable */
/*!
 *  Objects that can directly be drawn, as opposed to transforms
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGOpenGLRenderable : public NXSGNode {
    
public:
    NXSGOpenGLRenderable() throw (NXException);
    
    ~NXSGOpenGLRenderable() throw (NXException);
    
    bool apply(void) const throw () {glCallList(display_list_id); return true;}
    
    NXCommandResult beginRender(void) const throw ();
    
    NXCommandResult endRender(void) const throw ();
    
protected:
    GLuint display_list_id;
};


class NXSGOpenGLMaterial : public NXSGNode, public NXOpenGLMaterial {
public:
    NXSGOpenGLMaterial() throw () : NXSGNode() ,NXOpenGLMaterial() {}
    NXSGOpenGLMaterial(NXOpenGLMaterial const& mat) throw()
        : NXSGNode(), NXOpenGLMaterial(mat) {}
    ~NXSGOpenGLMaterial() throw () {}
    /// Copy assignment from GL-material
    NXSGOpenGLMaterial& operator = (NXOpenGLMaterial const& mat) throw ();
    bool apply(void) const throw ();
};

} // Nanorex

#endif // NX_SCENEGRAPH_OPENGL_H
