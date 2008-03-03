// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXOpenGLSceneGraph.h"
#include <Nanorex/Interface/NXNanoVisionResultCodes.h>

using namespace std;

namespace Nanorex {

// OpenGL Scenegraph context - only one per application
bool NXSGOpenGLNode::InitializeContext(void)
{
    bool success = true;
    
    // Read model-view stack max-depth
    glGetIntegerv(GL_MAX_MODELVIEW_STACK_DEPTH, &_s_maxModelViewStackDepth);
    if(glGetError() != GL_NO_ERROR) {
        SetError(NX_INITIALIZATION_ERROR,
                 "Error initializing OpenGL Scenegraph context probably because"
                 " glGet was called between glBegin and glEnd");
        success = false;
    }
    return success;
}


void NXSGOpenGLNode::SetError(int errCode, char const *const errMsg)
{
    commandResult.setResult(errCode);
    vector<QString> message;
    message.push_back(QObject::tr(errMsg));
    commandResult.setParamVector(message);
}


#if 0 // unused class - commented out
bool NXSGOpenGLGenericTransform::apply(void) const throw ()
{
    glMultMatrixd(matrix);
    GLenum const err = glGetError();
    return (err == GL_NO_ERROR) ? true : false;
}


#endif


bool NXSGOpenGLNode::addChild(NXSGNode *const /*child*/)
{
    SetError(NX_INTERNAL_ERROR,
             "OpenGL scenegraph nodes do not admit generic children");
    return false;
}


bool NXSGOpenGLNode::addChild(NXSGOpenGLNode *const child)
{
    bool included = NXSGNode::addChild(static_cast<NXSGNode*>(child));
    if(included) {
        child->newParentModelViewStackDepth(modelViewStackDepth);
    }
    else {
        SetError(NX_INTERNAL_ERROR,
                 "Could not include child node possibly because of lack of memory");
    }
    return included;
}


bool NXSGOpenGLNode::newParentModelViewStackDepth(int parentMVStackDepth)
{
    bool success = true;
    
    if(parentMVStackDepth > modelViewStackDepth) {
        modelViewStackDepth = parentMVStackDepth;
        ChildrenList::iterator childIter;
        for(childIter = children.begin();
            childIter != children.end() && success;
            ++childIter)
        {
            // children are guaranteed to be OpenGL scenegraph nodes
            NXSGOpenGLNode *openGLChildNode =
                dynamic_cast<NXSGOpenGLNode*>(*childIter);
            success =
                openGLChildNode->newParentModelViewStackDepth(modelViewStackDepth);
        }
    }
    
    return success;
}


/// Each model-view transform will push itself onto the matrix stack before
/// calling its children. Therefore it requires one more slot in the stack than
/// the parent with maximum model-view stack-depth. Note that a failure in the
/// interior of the tree will leave the scenegraph in a partially incorrect
/// state - those nodes which still respected the stack limit will show updated
/// depths. There is no point in undoing this because the whole scenegraph will
/// need to be redone anyway so that all leaves respect the limit.
bool
NXSGOpenGLModelViewTransform::newParentModelViewStackDepth(int parentMVStackDepth)
{
    bool success = true;
    if(parentMVStackDepth >= modelViewStackDepth) {
        // update local MV stack-depth
        if(parentMVStackDepth >= _s_maxModelViewStackDepth) {
            success = false;
            SetError(NX_INTERNAL_ERROR, "Maximum model-view stack-depth exceeded");
        }
        else {
            modelViewStackDepth = parentMVStackDepth + 1;
        }
        
        // propagate updated value to children
        ChildrenList::iterator childIter;
        for(childIter = children.begin();
            childIter != children.end() && success;
            ++childIter)
        {
            // children are guaranteed to be OpenGL scenegraph nodes
            NXSGOpenGLNode *openGLChildNode =
                dynamic_cast<NXSGOpenGLNode*>(*childIter);
            success =
                openGLChildNode->newParentModelViewStackDepth(modelViewStackDepth);
        }
    }
    return success;
}


/// Pushes the modelview matrix before applying the subscenegraph and
/// restores it afterwards
bool NXSGOpenGLModelViewTransform::applyRecursive(void) const throw()
{
    // Record OpenGL current-matrix state
    // GLenum currentMatrixMode;
    // glGetIntegerv(GL_MATRIX_MODE, (GLint*)&currentMatrixMode);
    
    // Save the modelview matrix
    glMatrixMode(GL_MODELVIEW);
    glPushMatrix();
    // trap stack overflow/underflow
    GLenum glError = glGetError();
    bool ok = (glError == GL_NO_ERROR);
    bool childrenOK = true;
    
    if(ok) {
        ok = apply();
        if(ok) {
            ChildrenList::const_iterator child_iter;
            for(child_iter = children.begin();
                child_iter != children.end() && childrenOK;
                ++child_iter)
            {
                childrenOK = (*child_iter)->applyRecursive();
            }
        }
        glPopMatrix();
    }
    
    // Setup error info if this node caused the failure
    if(!ok) {
        SetError(NX_INTERNAL_ERROR,
                 "Failure applying model-view transform in OpenGL scenegraph "
                 "context");
    }
    
    ok = ok && childrenOK;
    // restore the OpenGL matrix mode
    // glMatrixMode(currentMatrixMode);
    return ok;
}


bool NXSGOpenGLTranslate::apply(void) const throw ()
{
    glTranslated(x, y, z);
    GLenum const err = glGetError();
    bool ok = (err == GL_NO_ERROR);
    if(!ok) {
        SetError(NX_INTERNAL_ERROR,
                 "Failure applying OpenGL scenegraph translation");
    }
    return ok;
}



bool NXSGOpenGLRotate::apply(void) const throw ()
{
    glRotated(angle, x, y, z);
    GLenum const err = glGetError();
    bool ok = (err == GL_NO_ERROR);
    if(!ok) {
        SetError(NX_INTERNAL_ERROR,
                 "Failure applying OpenGL scenegraph rotation");
    }
    return ok;
}


bool NXSGOpenGLScale::apply(void) const throw ()
{
    glScaled(x, y, z);
    GLenum const err = glGetError();
    bool ok = (err == GL_NO_ERROR);
    if(!ok) {
        SetError(NX_INTERNAL_ERROR,
                 "Failure applying OpenGL scenegraph scaling");
    }
    return ok;
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


bool NXSGOpenGLRenderable::beginRender(void) const throw ()
{
    glNewList(display_list_id, GL_COMPILE);
    GLenum const err = glGetError();
    bool ok = (err == GL_NO_ERROR);
    if(!ok) {
#ifdef NX_DEBUG
        switch(err) {
        case GL_INVALID_VALUE:
            SetError(NX_INTERNAL_ERROR, "Begin-render with  display list id = 0");
            break;
        case GL_INVALID_OPERATION:
            SetError(NX_INTERNAL_ERROR, "Invalid begin-render operation");
            break;
        case GL_OUT_OF_MEMORY:
            SetError(NX_INTERNAL_ERROR, "Insufficient memory for begin-render op");
            break;
        default:
            SetError(NX_INTERNAL_ERROR, "Unknown error in begin-render");
            break;
        }
#else
        SetError(NX_INTERNAL_ERROR,
                 "Failure creating new OpenGL scenegraph display list");
#endif
    }
    return ok;
}


bool NXSGOpenGLRenderable::endRender(void) const throw ()
{
    glEndList();
    GLenum const err = glGetError();
    bool ok = (err == GL_NO_ERROR);
    if(!ok) {
#ifdef NX_DEBUG
        switch(err) {
        case GL_INVALID_VALUE:
            SetError(NX_INTERNAL_ERROR, "Begin-render with  display list id = 0");
            break;
        case GL_INVALID_OPERATION:
            SetError(NX_INTERNAL_ERROR, "Invalid begin-render operation");
            break;
        case GL_OUT_OF_MEMORY:
            SetError(NX_INTERNAL_ERROR, "Insufficient memory for begin-render op");
            break;
        default:
            SetError(NX_INTERNAL_ERROR, "Unknown error in begin-render");
            break;
        }
#else
        SetError(NX_INTERNAL_ERROR,
                 "Failure creating new OpenGL scenegraph display list");
#endif
    }
    return ok;
}

#if 0
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
#endif

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
    if(!ok) {
        SetError(NX_INTERNAL_ERROR,
                 "Error applying OpenGL material in scenegraph context");
    }
    return ok;
    
}


} // Nanorex
