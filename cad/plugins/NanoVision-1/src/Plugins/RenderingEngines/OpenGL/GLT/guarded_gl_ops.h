// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

/// \file guarded_gl_ops.h
/// \brief Wraps OpenGL calls in asserts to trap errors

// NOTE: include after GL.h


#ifndef GUARDED_GL_OPS_H
#define GUARDED_GL_OPS_H

#include <cassert>
#include <sstream>

#ifdef NX_DEBUG
#define GUARDED_GL_OP(op) { \
	assert(glGetError() == GL_NO_ERROR); \
	op; \
	assert(glGetError() == GL_NO_ERROR); \
}
#else
#define GUARDED_GL_OP(op) op;
#endif


/// 'op' is an OpenGL statement,
/// 'err' is a variable of type GLenum
/// 'errMsgStream' is a variable of type std::ostream or derived
#ifdef NX_DEBUG

#define GUARDED_GL_OP_WITH_GLERROR(op,err,errMsgStream) \
err = glGetError(); \
assert(err == GL_NO_ERROR); \
op; \
err = GLERROR(errMsgStream);

#else

#define GUARDED_GL_OP_WITH_GLERROR(op,err,errMsgStream) \
op; \
err = GLERROR(errMsgStream);

#endif


#endif// GUARDED_GL_OPS_H
