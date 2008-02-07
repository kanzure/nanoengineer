// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Interface/NXOpenGLSceneGraph.h"

namespace Nanorex {

#if 0 // unused class - commented out
bool NXSGOpenGLGenericTransform::apply(void) const throw ()
{
    glMultMatrixd(matrix);
    GLenum const err = glGetError();
    return (err == GL_NO_ERROR) ? true : false;
}


#endif


/// Pushes the modelview matrix before applying the subscenegraph and
/// restores it afterwards
bool NXSGOpenGLTransform::applyRecursive(void) const throw()
{
    /// @todo Make safer by maintaining stack inaccessible to developer

    // Record OpenGL current-matrix state
    GLenum currentMatrixMode;
    glGetIntegerv(GL_MATRIX_MODE, (GLint*)&currentMatrixMode);
    
    // Save the modelview matrix
    glMatrixMode(GL_MODELVIEW);
    glPushMatrix();
    // trap stack overflow/underflow
    GLenum glError = glGetError();
    bool ok = (glError == GL_NO_ERROR);
    
    if(ok) {
        ok = apply();
        if(ok) {
            ChildrenList::const_iterator child_iter;
            for(child_iter = children.begin();
                child_iter != children.end() && ok;
                ++child_iter)
            {
                ok = (*child_iter)->applyRecursive();
            }
        }
        glPopMatrix();
    }
    // restore the OpenGL matrix mode
    glMatrixMode(currentMatrixMode);
    return ok;
}


bool NXSGOpenGLTranslate::apply(void) const throw ()
{
    glTranslated(x, y, z);
    GLenum const err = glGetError();
    return (err == GL_NO_ERROR) ? true : false;
}



bool NXSGOpenGLRotate::apply(void) const throw ()
{
    glRotated(angle, x, y, z);
    GLenum const err = glGetError();
    return (err == GL_NO_ERROR) ? true : false;
}


bool NXSGOpenGLScale::apply(void) const throw ()
{
    glScaled(x, y, z);
    GLenum const err = glGetError();
    return (err == GL_NO_ERROR) ? true : false;
}


NXSGOpenGLRenderable::NXSGOpenGLRenderable() throw (NXException)
{
    display_list_id = glGenLists(1);
    GLenum const err = glGetError();
    if(err != GL_NO_ERROR || !glIsList(display_list_id))
        throw NXException("Error calling glGenLists");
}


NXSGOpenGLRenderable::~NXSGOpenGLRenderable() throw (NXException)
{
    glDeleteLists(display_list_id, 1);
    GLenum const err = glGetError();
    if(err != GL_NO_ERROR)
        throw NXException("Error calling glDeleteLists");
}


NXCommandResult NXSGOpenGLRenderable::beginRender(void) const throw ()
{
    glNewList(display_list_id, GL_COMPILE);
    NXCommandResult result;
    // GLenum const err = glGetError();
    /// @todo set result based on error
    return result;
}


NXCommandResult NXSGOpenGLRenderable::endRender(void) const throw ()
{
    glEndList();
    NXCommandResult result;
    // GLenum const err = glGetError();
    /// @todo set result based on error
    return result;
}


NXSGOpenGLMaterial& NXSGOpenGLMaterial::operator = (NXOpenGLMaterial const& mat) throw ()
{
    face = mat.face;
    size_t const double4ArraySize = 4 * sizeof(double);
    memcpy((void*)ambient, (void*)mat.ambient, double4ArraySize);
    memcpy((void*)diffuse, (void*)mat.diffuse, double4ArraySize);
    memcpy((void*)specular, (void*)mat.specular, double4ArraySize);
    memcpy((void*)emission, (void*)mat.emission, double4ArraySize);
    shininess = mat.shininess;
    return *this;
}


bool NXSGOpenGLMaterial::apply(void) const throw ()
{
    glMaterialfv(face, GL_AMBIENT, ambient);
    bool const ok_ambient = (glGetError() == GL_NO_ERROR);
    glMaterialfv(face, GL_DIFFUSE, diffuse);
    bool const ok_diffuse = (glGetError() == GL_NO_ERROR);
    glMaterialfv(face, GL_SPECULAR, specular);
    bool const ok_specular= (glGetError() == GL_NO_ERROR);
    glMaterialfv(face, GL_EMISSION, emission);
    bool const ok_emission= (glGetError() == GL_NO_ERROR);
    glMaterialf(face, GL_SHININESS, shininess);
    bool const ok_shininess = (glGetError() == GL_NO_ERROR);
    bool const ok = (ok_ambient  &&
                     ok_diffuse  &&
                     ok_specular &&
                     ok_emission &&
                     ok_shininess);
    return ok;
}


} // Nanorex
