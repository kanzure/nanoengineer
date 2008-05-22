// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXOpenGLSceneGraph.h"
#include <Nanorex/Interface/NXNanoVisionResultCodes.h>
#include <Nanorex/Utility/NXUtility.h>
#include "GLT/guarded_gl_ops.h"
#include "GLT/glt_error.h"
#include <sstream>
#include <cassert>

using namespace std;
using namespace Nanorex;

// utility functions
template<typename T>
inline void guarded_delete_array(T* &ptr)
{
	if(ptr != (T*) NULL)
		delete[] ptr;
	ptr = (T*) NULL;
}


// static data
GLint NXSGOpenGLNode::_s_maxModelViewStackDepth;

// .............................................................................

// OpenGL Scenegraph context - only one per application
bool NXSGOpenGLNode::InitializeContext(void)
{
    /// @todo Mutex locks
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

// .............................................................................

bool NXSGOpenGLNode::initializeContext(void)
{
    bool const baseClassContextInitialized = NXSGNode::initializeContext();
    bool const thisClassContextInitialized = InitializeContext();
    bool const ok = baseClassContextInitialized && thisClassContextInitialized;
    return ok;
}

// .............................................................................

bool NXSGOpenGLNode::cleanupContext(void)
{
    bool const baseClassContextCleanedUp = NXSGNode::cleanupContext();
    return baseClassContextCleanedUp;
}

// .............................................................................

bool NXSGOpenGLNode::addChild(NXSGNode *const /*child*/)
{
    SetError(NX_INTERNAL_ERROR,
             "OpenGL scenegraph nodes do not admit generic children");
    return false;
}

// .............................................................................

bool NXSGOpenGLNode::addChild(NXSGOpenGLNode *const child)
{
    bool included = NXSGNode::addChild(child);
    if(included) {
        child->newParentModelViewStackDepth(modelViewStackDepth);
    }
    return included;
}

// .............................................................................

bool NXSGOpenGLNode::newParentModelViewStackDepth(int parentMVStackDepth)
{
    bool success = true;
    
    if(parentMVStackDepth > modelViewStackDepth) {
        modelViewStackDepth = parentMVStackDepth;
        ChildrenList::iterator childIter;
        for(childIter = children.begin();
            (childIter != children.end()) && success;
            ++childIter)
        {
            // children are guaranteed to be OpenGL scenegraph nodes
	        NXSGNode *childNode = *childIter;
            NXSGOpenGLNode *openGLChildNode =
                dynamic_cast<NXSGOpenGLNode*>(childNode);
	        assert(openGLChildNode != NULL);
            success =
                openGLChildNode->newParentModelViewStackDepth(modelViewStackDepth);
        }
    }
    
    return success;
}

// .............................................................................

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

// .............................................................................

/// Pushes the modelview matrix before applying the subscenegraph and
/// restores it afterwards
bool NXSGOpenGLModelViewTransform::applyRecursive(void) const throw()
{
    // Save the modelview matrix
	GUARDED_GL_OP(glMatrixMode(GL_MODELVIEW));
	glPushMatrix();
	
	// trap stack overflow/underflow
    GLenum glError = glGetError();
    bool ok = (glError == GL_NO_ERROR);
    if(!ok) {
        SetError(NX_INTERNAL_ERROR,
                 "OpenGL modelview stack overflow or invalid operation");
        return false;
    }
    
    // apply transform and quit if error
    bool appliedOK = apply();
	if(appliedOK) {
		bool childrenOK = true;
		ChildrenList::const_iterator child_iter;
		for(child_iter = children.begin();
		    child_iter != children.end() && childrenOK;
		    ++child_iter)
		{
			childrenOK = (*child_iter)->applyRecursive();
		}
		appliedOK = childrenOK;
	}
	
    // Restore model-view matrix
	GUARDED_GL_OP(glPopMatrix());
    
    return appliedOK;
}

// .............................................................................

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


// .............................................................................

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

// .............................................................................

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

// .............................................................................

NXSGOpenGLRenderable::NXSGOpenGLRenderable() throw (NXException)
{
	GLenum err = GL_NO_ERROR;
	ostringstream errStream;
	GUARDED_GL_OP_WITH_GLERROR(display_list_id = glGenLists(1),
	                           err, errStream);
	if(err != GL_NO_ERROR || !glIsList(display_list_id))
		throw NXException("Error calling glGenLists");
}

// .............................................................................

NXSGOpenGLRenderable::~NXSGOpenGLRenderable() throw (NXException)
{
	GLenum err = GL_NO_ERROR;
	ostringstream errStream;
	GUARDED_GL_OP_WITH_GLERROR(glDeleteLists(display_list_id, 1),
	                           err, errStream);
	if(err != GL_NO_ERROR)
		throw NXException("Error calling glDeleteLists");
}

// .............................................................................

bool NXSGOpenGLRenderable::apply(void) const throw () {
	GUARDED_GL_OP(glCallList(display_list_id));
	return true;
}

// .............................................................................

bool NXSGOpenGLRenderable::beginRender(void) const throw ()
{
	GLenum err = GL_NO_ERROR;
	ostringstream errStream;
	GUARDED_GL_OP_WITH_GLERROR(glNewList(display_list_id, GL_COMPILE),
	                           err, errStream);
	if(err != GL_NO_ERROR) {
        SetError(NX_INTERNAL_ERROR, errStream.str().c_str());
        return false;
    }
    return true;
}

// .............................................................................

bool NXSGOpenGLRenderable::endRender(void) const throw ()
{
	GLenum err = GL_NO_ERROR;
	ostringstream errStream;
	GUARDED_GL_OP_WITH_GLERROR(glEndList(),
	                           err, errStream);
    if(err != GL_NO_ERROR) {
        SetError(NX_INTERNAL_ERROR, errStream.str().c_str());
        return false;
    }
    return true;
}

// .............................................................................

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

// .............................................................................

bool NXSGOpenGLMaterial::apply(void) const throw ()
{
#ifdef NX_DEBUG
	GLenum err = GL_NO_ERROR;
	err = glGetError();
	assert(err == GL_NO_ERROR);
#endif
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

// .............................................................................

NXSGGlePolyCone::NXSGGlePolyCone(int npoints,
                                 gleDouble point_array[][3],
                                 float color_array[][3],
                                 gleDouble radius_array[])
: n(npoints), points(NULL), colors(NULL), radii(NULL)
{
	allocate();
	memcpy((void*) points, (void*) point_array, n * sizeof(gleDouble[3]));
	memcpy((void*) colors, (void*) color_array, n * sizeof(float[3]));
	memcpy((void*) radii, (void*) radius_array, n * sizeof(gleDouble));
}

// .............................................................................

NXSGGlePolyCone::NXSGGlePolyCone(int npoints)
: n(npoints), points(NULL), colors(NULL), radii(NULL)
{
	allocate();
}

// .............................................................................

NXSGGlePolyCone::~NXSGGlePolyCone() { deallocate(); }

// .............................................................................

void NXSGGlePolyCone::allocate(void)
{
	try {
		points = new gleDouble[n][3];
		colors = new float[n][3];
		radii  = new gleDouble[n];
	}
	catch(...) {
		throw NXException(/** @todo */);
	}
	
}

// .............................................................................

void NXSGGlePolyCone::deallocate(void)
{
	guarded_delete_array(points);
	guarded_delete_array(colors);
	guarded_delete_array(radii);
	n = 0;
}

// .............................................................................

#ifdef NX_DEBUG
string const NXSGOpenGLNode::getName() const
{
//     ostringstream strm;
// 	strm << ("OGL_"  + name + "-") << id;
//     return strm.str();
	
	return "OGL_"  + name + "_" + NXUtility::itos(id);
}

// .............................................................................

string const NXSGOpenGLTransform::getName() const
{
//     ostringstream strm;
// 	strm << ("OGLTf_"  + name + "-") << id;
//     return strm.str();
	
	return "OGLTf_"  + name + "_" + NXUtility::itos(id);
}

// .............................................................................

string const NXSGOpenGLModelViewTransform::getName() const
{
//     ostringstream strm;
// 	strm << ("OGLMV_"  + name + "-") << id;
//     return strm.str();
	
	return "OGLMV_"  + name + "_" + NXUtility::itos(id);
}

// .............................................................................

string const NXSGOpenGLTranslate::getName() const
{
//     ostringstream strm;
// 	strm << ("OGLTra_"  + name + "-") << id;
//     return strm.str();
	
	return "OGLTra_"  + name + "_" + NXUtility::itos(id);
}

// .............................................................................

string const NXSGOpenGLRotate::getName() const
{
//     ostringstream strm;
// 	strm << ("OGLRot_"  + name + "-") << id;
//     return strm.str();
	
	return "OGLRot_"  + name + "_" + NXUtility::itos(id);
}

// .............................................................................

string const NXSGOpenGLScale::getName() const
{
//     ostringstream strm;
// 	strm << ("OGLSca_"  + name + "-") << id;
//     return strm.str();
	
	return "OGLSca_"  + name + "_" + NXUtility::itos(id);
}

// .............................................................................

string const NXSGOpenGLRenderable::getName() const
{
//     ostringstream strm;
// 	strm << ("OGLRend_"  + name + "-") << id;
//     return strm.str();
	return "OGLRend_"  + name + "_" + NXUtility::itos(id);
}

// .............................................................................

string const NXSGOpenGLMaterial::getName() const
{
//     ostringstream strm;
// 	strm << ("OGLMat_"  + name + "-") << id;
//     return strm.str();
	
	return "OGLMat_"  + name + "_" + NXUtility::itos(id);
}

// .............................................................................

string const NXSGGleSetJoinStyle::getName() const
{
	return "GLESetJoinStyle_" + name + "_" + NXUtility::itos(id);
}

// .............................................................................

string const NXSGGlePolyCone::getName() const
{
	return "GLEPolyCone_" + name + "_" + NXUtility::itos(id);
}


#endif

