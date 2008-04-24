// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_SCENEGRAPH_OPENGL_H
#define NX_SCENEGRAPH_OPENGL_H

// Scenegraph classes for OpenGL

#if defined(__APPLE__)
#include <OpenGL/gl.h>
#else
#include <GL/gl.h>
#endif
#include <GL/gle.h>

#include <cstring>

#include "Nanorex/Interface/NXSceneGraph.h"
#include "Nanorex/Utility/NXUtility.h"
#include "Nanorex/Utility/NXCommandResult.h"
#include "NXOpenGLMaterial.h"


/* CLASS: NXSGOpenGLNode */
/**
 * Base-class for all OpenGL scenegraph nodes. Helps to maintain debug checks
 * for OpenGL state like matrix-stack depth etc.
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGOpenGLNode : public Nanorex::NXSGNode {
public:
    NXSGOpenGLNode() : modelViewStackDepth(0) {}
    ~NXSGOpenGLNode() {}
    
    // Override virtual methods
    bool initializeContext(void);
    bool cleanupContext(void);
    
    /// Prevent addition of generic nodes so that children are OpenGL
    /// scenegraph nodes. Required to be able to propagate context checks
    bool addChild(NXSGNode *const child);
    
    /// Add child if OpenGL state limits are not exceeded
    virtual bool addChild(NXSGOpenGLNode *const child);
    
    int getModelViewStackDepth(void) { return modelViewStackDepth; }
    
    /// @todo - making this protected created compilation errors - gcc bug?
    /// Called by parent when its stack depth is updated to recursively
    /// propagate this info to leaves
    virtual bool newParentModelViewStackDepth(int newMVStackDepth);
    
    // static members
    
    static GLint const& GetMaxModelViewStackDepth(void)
    { return _s_maxModelViewStackDepth; }
    
#ifdef NX_DEBUG
    std::string const getName(void) const;
#endif
    
protected:
    /// Maximum model-view stack depth in reaching this node from root
    int modelViewStackDepth;
    
    // -- OpenGL context -- 
    
    /// model-view stack-size limit
    static GLint _s_maxModelViewStackDepth;
    
    /// Assess OpenGL context limits.
    /// Must be called after the OpenGL context is made current and
    /// before OpenGL scenegraph module is used
    bool InitializeContext(void);
    
};


/* CLASS: NXSGOpenGLTransform */
/**
 * Base class for OpenGL transforms
 * Re-implements the applyRecursive() method so that it pushes the modelview
 * matrix before applying the scenegraph subtree, and pops the modelview
 * matrix afterwards.
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGOpenGLTransform : public NXSGOpenGLNode {
public:
    NXSGOpenGLTransform() throw () {}
    ~NXSGOpenGLTransform() throw () {};
#ifdef NX_DEBUG
    std::string const getName(void) const;
#endif
    
    
};


/* CLASS: NXSGOpenGLModelViewTransform */
/**
 * Base class for OpenGL transforms that affect the modelview matrix
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGOpenGLModelViewTransform : public NXSGOpenGLTransform {
public:
    NXSGOpenGLModelViewTransform() throw()
    { ++modelViewStackDepth; /* must be >= 1 */ }
    
    ~NXSGOpenGLModelViewTransform() throw() {}
    
    // bool addChild(NXSGOpenGLNode *child);
    
    bool applyRecursive(void) const throw();
    
    /// Re-implement base-class method because this class increments
    /// model-view stack-depth
    bool newParentModelViewStackDepth(int parentMVStackDepth);
    
#ifdef NX_DEBUG
    std::string const getName(void) const;
#endif
};


/* CLASS NXSGOpenGLTranslate */
/**
 * OpenGL translation node
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGOpenGLTranslate : public NXSGOpenGLModelViewTransform {
public:
    NXSGOpenGLTranslate(double const& the_x,
                        double const& the_y,
                        double const& the_z) throw ()
        : x(the_x), y(the_y), z(the_z) {}
    ~NXSGOpenGLTranslate() throw () {}
    bool apply(void) const throw ();
#ifdef NX_DEBUG
    std::string const getName(void) const;
#endif
    
    
private:
    GLdouble x, y, z;
};



/* CLASS: NXSGOpenGLRotate */
/**
 * Scenegraph rotation node
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGOpenGLRotate : public NXSGOpenGLModelViewTransform {
public:
    NXSGOpenGLRotate(double const& the_angle,
                     double const& the_x,
                     double const& the_y,
                     double const& the_z) throw ()
        : angle(the_angle), x(the_x), y(the_y), z(the_z) {}
    ~NXSGOpenGLRotate() throw () {}
    bool apply(void) const throw ();
#ifdef NX_DEBUG
    std::string const getName(void) const;
#endif
    
    
private:
    GLdouble angle, x, y, z;
};


/* CLASS: NXSGOpenGLScale */
/**
 * Scenegraph scaling node
 *
 * @ingroup NanorexInterface, PluginArchitecture, GraphicsArchitecture
 */
class NXSGOpenGLScale : public NXSGOpenGLModelViewTransform {
public:
    NXSGOpenGLScale(double const& the_x,
                    double const& the_y,
                    double const& the_z) throw ()
        : x(the_x), y(the_y), z(the_z)  {}
    ~NXSGOpenGLScale() throw () {}
    bool apply(void) const throw ();
#ifdef NX_DEBUG
    std::string const getName(void) const;
#endif
    
    
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
class NXSGOpenGLRenderable : public NXSGOpenGLNode {
    
public:
	NXSGOpenGLRenderable() throw (Nanorex::NXException);
    
	~NXSGOpenGLRenderable() throw (Nanorex::NXException);
    
	bool apply(void) const throw ();
    
    /// Calls glNewList(). Call the plugin's render-method after this so that
    /// what the plugin draws using OpenGL becomes part of this display list
    bool beginRender(void) const throw ();
    
    /// Calls glEndList(). Call after the plugin does its OpenGL rendering.
    bool endRender(void) const throw ();
    
#ifdef NX_DEBUG
    GLuint getDisplayListID(void) const { return display_list_id; }
    std::string const getName(void) const;
#endif
    
    
protected:
    GLuint display_list_id;
};


class NXSGOpenGLMaterial : public NXSGOpenGLNode, public NXOpenGLMaterial {
public:
    NXSGOpenGLMaterial() throw () : NXSGOpenGLNode() ,NXOpenGLMaterial() {}
    NXSGOpenGLMaterial(NXOpenGLMaterial const& mat) throw()
        : NXSGOpenGLNode(), NXOpenGLMaterial(mat) {}
	~NXSGOpenGLMaterial() throw () {}
    /// Copy assignment from GL-material
    // NXSGOpenGLMaterial& operator = (NXOpenGLMaterial const& mat) throw ();
    bool apply(void) const throw ();
#ifdef NX_DEBUG
    std::string const getName(void) const;
#endif    
};


class NXSGGleSetJoinStyle : public NXSGOpenGLNode {
public:
	NXSGGleSetJoinStyle(int _style=0) throw() : style(_style) {}
	~NXSGGleSetJoinStyle() {}
	bool apply(void) const throw() { gleSetJoinStyle(style); return true; }
	int style;
#ifdef NX_DEBUG
	std::string const getName(void) const;
#endif
};


class NXSGGlePolyCone : public NXSGOpenGLNode {
public:
	/// GLE prototype-based constructor
	NXSGGlePolyCone(int npoints,
	                gleDouble point_array[][3],
	                float color_array[][3],
	                gleDouble radius_array[]);
	NXSGGlePolyCone(int npoints);
	~NXSGGlePolyCone();
	
	bool apply(void) const throw() { glePolyCone(n, points, colors, radii); return true; }
	
	int n;
	gleDouble (*points)[3];
	float (*colors)[3];
	gleDouble *radii;
#ifdef NX_DEBUG
	std::string const getName(void) const;
#endif
	
private:
	void allocate(void);
	void deallocate(void);
};

#endif // NX_SCENEGRAPH_OPENGL_H
