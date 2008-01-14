// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_SCENEGRAPH_H
#define NX_SCENEGRAPH_H

// SceneGraph classes for OpenGL Renderer
 

namespace Nanorex {

/* CLASS: NXSGNode */
/**
 * Base class for all scenegraph nodes
 */
class NXSGNode {
public:
    NXSGNode() {}
    virtual ~NXSGNode() {}

    void addChild(NXSGNode *const child) { children.push_back(child); }
    
    std::vector<NXSGNode *const> const& getChildren(void) const { return children; }
    std::vector<NXSGNode *const>::size_type getNumChildren(void) const { return children.size(); }
    
    virtual void apply(void) const = 0;
    
    void applyRecursive(void) const {
        apply();
        typedef std::vector<NXSGNode *const>::const_iterator child_iter_type;
        for(child_iter_type child_iter = children.begin();
            child_iter != children.end();
            ++child_iter)
        {
            child_iter->applyRecursive();
        }
    }
    
    bool isLeaf(void) const { return (children.size()==0); }
        
private:
    std::vector<NXSGNode *const> children;
};


/* CLASS: NXSGTransform */
/**
 * Generic transform
 */
class NXSGTransform : public NXSGNode {

public:
    NXSGTransform() {}
    ~NXSGTransform() {}

    void apply(void) const { glMultMatrix(matrix); }

    static NXSGTransform Translate(double const& x, double const& y, double const& z);
    static NXSGTransform Rotate(double const& angle, double const& x, double const& y, double const& z);
    static NXSGTransform Scale(double const& x, double const& y, double const& z);

private:
    GLdouble matrix[16];
    
    void zero() { for(int i=0; i<16; ++i) matrix[i] = 0.0 }
    void identity() { zero(); matrix[0] = matrix[5] = matrix[10] = matrix[15] = 1.0; }
};


/* CLASS NXSGTranslate */
/**
 * Scenegraph translation node
 */
class NXSGTranslate : public NXSGNode {
public:
    NXSGTranslate(double const& the_x, double const& the_y, double const& the_z)
        : x(the_x), y(the_y), z(the_z) {}
    ~NXSGTranslate() {}
    void apply(void) const { glTranslated(x, y, z); }
private:
    GLdouble x, y, z;
};



/* CLASS: NXSGRotate */
/**
 * Scenegraph rotation node
 */
class NXSGRotate : public NXSGNode {
public:
    NXSGRotate(double const& the_angle, double const& the_x, double const& the_y, double const& the_z)
        : angle(the_angle), x(the_x), y(the_y), z(the_z)
    {
    }
    ~NXSGRotate() {}
    void apply(void) const { glRotated(angle, x, y, z); }
private:
    GLdouble angle, x, y, z;
};


/* CLASS: NXSGScale */
/**
 * Scenegraph scaling node
 */
class NXSGScale : public NXSGNode {
public:
    NXSGScale(double const& the_x, double const& the_y, double const& the_z)
        : x(the_x), y(the_y), z(the_z)  {}
    ~NXSGScale() {}
    void apply(void) const { glScaled(x, y, z); }
private:
    GLdouble x, y, z;
};


/* CLASS NXSGRenderable */
/*!
 *  Objects that can directly be drawn, as opposed to transforms
 */
class NXSGRenderable : public NXSGNode {

public:
    /// @todo Check OpenGL state for errors
    NXSGRenderable() {
        display_list_id = glGenLists(1);
    }
    
    /// @todo Check OpenGL state for errors
    ~NXSGRenderable() { glDeleteLists(display_list_id); }

    /// @todo Check OpenGL state for errors
    void apply(void) const { glCallList(display_list_id); }
    
    /// @todo Check OpenGL state for errors
    void beginRender(void) const { glNewList(display_list_id, GL_COMPILE); }
    
    /// @todo Check OpenGL state for errors
    void endRender(void) const { glEndList(); }

protected:
    GLuint display_list_id;
};



#if 0 // commented section
class NXSGAtomRenderer : public NXSGRenderable {
public:
    NXSGAtomRenderer(NXAtom const& a) : atom(a) {}
    ~NXSGAtomRenderer() {}


private:
    NXAtom const& atom;
};



class NXSGBondRenderer : public NXSGRenderable {
public:
    NXSGBondRenderer(NXBond const& b) : bond(b) {}
    ~NXSGBondRenderer() {}

    void render(NXBondRenderInfo const&);

private:
    NXBond const& bond;
};


#endif // commented section


} // Nanorex

#endif // NX_SCENEGRAPH_H
