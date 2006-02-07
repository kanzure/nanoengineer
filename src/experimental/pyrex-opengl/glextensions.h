/*----------------------------------------------------------------------------

Copyright (c) 2000, Brad Grantham and Applied Conjecture. All
rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
  3. Neither the name Brad Grantham nor Applied Conjecture
     may be used to endorse or promote products derived from this software
     without permission.

THIS SOFTWARE IS PROVIDED BY BRAD GRANTHAM AND APPLIED CONJECTURE``AS
IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE BRAD GRANTHAM
OR APPLIED CONJECTURE BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

----------------------------------------------------------------------------*/

#ifndef _glextensions_h_
#define _glextensions_h_

#ifdef _WIN32 /*------------------------------------------------------------*/

#include <windows.h>
#include <GL/gl.h>
#include "glext.h"

#elif MACOSX /*-------------------------------------------------------------*/

/* MacOS window handling? */
#include <gl.h>
#include "glext.h"

#else /* Presumably Linux */ /*---------------------------------------------*/

#define GLX_GLXEXT_PROTOTYPES
#include <X11/Xlib.h>
#include <GL/gl.h>
#include <GL/glx.h>
#include <GL/glext.h>
#include <GL/glxext.h>

#endif /*-------------------------------------------------------------------*/

#if !defined(GL_ARB_occlusion_query)
#define GL_ARB_occlusion_query 1
#define GL_QUERY_COUNTER_BITS_ARB         0x8864
#define GL_CURRENT_QUERY_ARB              0x8865
#define GL_QUERY_RESULT_ARB               0x8866
#define GL_QUERY_RESULT_AVAILABLE_ARB     0x8867
#define GL_SAMPLES_PASSED_ARB             0x8914
#endif

typedef void (APIENTRY * GL_GENQUERIESARBPROC) (GLsizei n, GLuint *ids);
typedef void (APIENTRY * GL_DELETEQUERIESARBPROC) (GLsizei n, const GLuint *ids);
typedef GLboolean (APIENTRY * GL_ISQUERYARBPROC) (GLuint id);
typedef void (APIENTRY * GL_BEGINQUERYARBPROC) (GLenum target, GLuint id);
typedef void (APIENTRY * GL_ENDQUERYARBPROC) (GLenum target);
typedef void (APIENTRY * GL_GETQUERYIVARBPROC) (GLenum target, GLenum pname, GLint *params);
typedef void (APIENTRY * GL_GETQUERYOBJECTIVARBPROC) (GLuint id, GLenum pname, GLint *params);
typedef void (APIENTRY * GL_GETQUERYOBJECTUIVARBPROC) (GLuint id, GLenum pname, GLuint *params);


// ---------------------------------------------------------------------------
// GL_ARB_vertex_program ---------------------------------------------------
// ---------------------------------------------------------------------------
#if !defined(GL_ARB_vertex_program)
#define GL_ARB_vertex_program 1

#define GL_PROGRAM_FORMAT_ASCII_ARB                 0x8875
#define GL_PROGRAM_ERROR_POSITION_ARB               0x864B
#define GL_PROGRAM_ERROR_STRING_ARB                 0x8874
#define GL_MAX_PROGRAM_LOCAL_PARAMETERS_ARB         0x88B4
#define GL_MAX_PROGRAM_ENV_PARAMETERS_ARB           0x88B5

#endif

typedef void (APIENTRY * GL_GENOCCLUSIONQUERIESNVPROC) (GLsizei n, GLuint *ids);
typedef void (APIENTRY * GL_DELETEOCCLUSIONQUERIESNVPROC) (GLsizei n, const GLuint *ids);
typedef GLboolean (APIENTRY * GL_ISOCCLUSIONQUERYNVPROC) (GLuint id);
typedef void (APIENTRY * GL_BEGINOCCLUSIONQUERYNVPROC) (GLuint id);
typedef void (APIENTRY * GL_ENDOCCLUSIONQUERYNVPROC) (void);
typedef void (APIENTRY * GL_GETOCCLUSIONQUERYIVNVPROC) (GLuint id, GLenum pname, GLint *params);
typedef void (APIENTRY * GL_GETOCCLUSIONQUERYUIVNVPROC) (GLuint id, GLenum pname, GLuint *params);



typedef void (APIENTRY * GL_PROGRAMSTRINGARBPROC) (GLenum target, GLenum format, GLsizei len, const void *string);
typedef void (APIENTRY * GL_BINDPROGRAMARBPROC) (GLenum target, GLuint program);
typedef void (APIENTRY * GL_DELETEPROGRAMSARBPROC) (GLsizei n, const GLuint *programs);
typedef void (APIENTRY * GL_GENPROGRAMSARBPROC) (GLsizei n, GLuint *programs);
typedef void (APIENTRY * GL_PROGRAMENVPARAMETER4DARBPROC) (GLenum target, GLuint index, GLdouble x, GLdouble y, GLdouble z, GLdouble w);
typedef void (APIENTRY * GL_PROGRAMENVPARAMETER4DVARBPROC) (GLenum target, GLuint index, const GLdouble *params);
typedef void (APIENTRY * GL_PROGRAMENVPARAMETER4FARBPROC) (GLenum target, GLuint index, GLfloat x, GLfloat y, GLfloat z, GLfloat w);
typedef void (APIENTRY * GL_PROGRAMENVPARAMETER4FVARBPROC) (GLenum target, GLuint index, const GLfloat *params);
typedef void (APIENTRY * GL_PROGRAMLOCALPARAMETER4DARBPROC) (GLenum target, GLuint index, GLdouble x, GLdouble y, GLdouble z, GLdouble w);
typedef void (APIENTRY * GL_PROGRAMLOCALPARAMETER4DVARBPROC) (GLenum target, GLuint index, const GLdouble *params);
typedef void (APIENTRY * GL_PROGRAMLOCALPARAMETER4FARBPROC) (GLenum target, GLuint index, GLfloat x, GLfloat y, GLfloat z, GLfloat w);
typedef void (APIENTRY * GL_PROGRAMLOCALPARAMETER4FVARBPROC) (GLenum target, GLuint index, const GLfloat *params);
typedef void (APIENTRY * GL_GETPROGRAMENVPARAMETERDVARBPROC) (GLenum target, GLuint index, GLdouble *params);
typedef void (APIENTRY * GL_GETPROGRAMENVPARAMETERFVARBPROC) (GLenum target, GLuint index, GLfloat *params);
typedef void (APIENTRY * GL_GETPROGRAMLOCALPARAMETERDVARBPROC) (GLenum target, GLuint index, GLdouble *params);
typedef void (APIENTRY * GL_GETPROGRAMLOCALPARAMETERFVARBPROC) (GLenum target, GLuint index, GLfloat *params);
typedef void (APIENTRY * GL_GETPROGRAMIVARBPROC) (GLenum target, GLenum pname, int *params);
typedef void (APIENTRY * GL_GETPROGRAMSTRINGARBPROC) (GLenum target, GLenum pname, void *string);
typedef GLboolean (APIENTRY * GL_ISPROGRAMARBPROC) (GLuint program);


// ---------------------------------------------------------------------------
// GL_ARB_fragment_program ---------------------------------------------------
// ---------------------------------------------------------------------------

#if !defined(GL_ARB_fragment_program)
#define GL_ARB_fragment_program 1

#define GL_FRAGMENT_PROGRAM_ARB                     0x8804
#define GL_PROGRAM_ALU_INSTRUCTIONS_ARB             0x8805
#define GL_PROGRAM_TEX_INSTRUCTIONS_ARB             0x8806
#define GL_PROGRAM_TEX_INDIRECTIONS_ARB             0x8807
#define GL_PROGRAM_NATIVE_ALU_INSTRUCTIONS_ARB      0x8808
#define GL_PROGRAM_NATIVE_TEX_INSTRUCTIONS_ARB      0x8809
#define GL_PROGRAM_NATIVE_TEX_INDIRECTIONS_ARB      0x880A
#define GL_MAX_PROGRAM_ALU_INSTRUCTIONS_ARB         0x880B
#define GL_MAX_PROGRAM_TEX_INSTRUCTIONS_ARB         0x880C
#define GL_MAX_PROGRAM_TEX_INDIRECTIONS_ARB         0x880D
#define GL_MAX_PROGRAM_NATIVE_ALU_INSTRUCTIONS_ARB  0x880E
#define GL_MAX_PROGRAM_NATIVE_TEX_INSTRUCTIONS_ARB  0x880F
#define GL_MAX_PROGRAM_NATIVE_TEX_INDIRECTIONS_ARB  0x8810
#define GL_MAX_TEXTURE_COORDS_ARB                   0x8871
#define GL_MAX_TEXTURE_IMAGE_UNITS_ARB              0x8872

#endif /* GL_ARB_fragment_program */

// ---------------------------------------------------------------------------
// GL_ATI_texture_float ------------------------------------------------------
// ---------------------------------------------------------------------------
#if !defined(GL_ATI_texture_float)
#define GL_ATI_texture_float 1

#define GL_RGBA_FLOAT32_ATI			    0x8814
#define GL_RGB_FLOAT32_ATI			    0x8815
#define GL_ALPHA_FLOAT32_ATI			    0x8816
#define GL_INTENSITY_FLOAT32_ATI		    0x8817
#define GL_LUMINANCE_FLOAT32_ATI		    0x8818
#define GL_LUMINANCE_ALPHA_FLOAT32_ATI		    0x8819
#define GL_RGBA_FLOAT16_ATI			    0x881A
#define GL_RGB_FLOAT16_ATI			    0x881B
#define GL_ALPHA_FLOAT16_ATI			    0x881C
#define GL_INTENSITY_FLOAT16_ATI		    0x881D
#define GL_LUMINANCE_FLOAT16_ATI		    0x881E
#define GL_LUMINANCE_ALPHA_FLOAT16_ATI		    0x881F

#endif /* GL_ATI_texture_float */

typedef void (APIENTRY * GL_BINDBUFFERARBPROC)(GLenum target, GLuint buffer);
typedef void (APIENTRY * GL_DELETEBUFFERSARBPROC)(GLsizei n, const GLuint *buffers);
typedef void (APIENTRY * GL_GENBUFFERSARBPROC)(GLsizei n, GLuint *buffers);
typedef GLboolean (APIENTRY * GL_ISBUFFERARBPROC)(GLuint buffer);
typedef void (APIENTRY * GL_BUFFERDATAARBPROC)(GLenum target, GLsizeiptrARB size, const GLvoid *data, GLenum usage);
typedef void (APIENTRY * GL_BUFFERSUBDATAARBPROC)(GLenum target, GLintptrARB offset, GLsizeiptrARB size, const GLvoid *data);
typedef void (APIENTRY * GL_GETBUFFERSUBDATAARBPROC)(GLenum target, GLintptrARB offset, GLsizeiptrARB size, GLvoid *data);
typedef GLvoid* (APIENTRY * GL_MAPBUFFERARBPROC)(GLenum target, GLenum access);
typedef GLboolean (APIENTRY * GL_UNMAPBUFFERARBPROC)(GLenum target);
typedef void (APIENTRY * GL_GETBUFFERPARAMETERIVARBPROC)(GLenum target, GLenum pname, GLint *params);
typedef void (APIENTRY * GL_GETBUFFERPOINTERVARBPROC)(GLenum target, GLenum pname, GLvoid **params);

typedef GLuint (APIENTRY * GL_NEWOBJECTBUFFERATIPROC) (GLsizei size, const GLvoid *pointer, GLenum usage);
typedef GLboolean (APIENTRY * GL_ISOBJECTBUFFERATIPROC) (GLuint buffer);
typedef void (APIENTRY * GL_UPDATEOBJECTBUFFERATIPROC) (GLuint buffer, GLuint offset, GLsizei size, const GLvoid *pointer, GLenum preserve);
typedef void (APIENTRY * GL_GETOBJECTBUFFERFVATIPROC) (GLuint buffer, GLenum pname, GLfloat *params);
typedef void (APIENTRY * GL_GETOBJECTBUFFERIVATIPROC) (GLuint buffer, GLenum pname, GLint *params);
typedef void (APIENTRY * GL_DELETEOBJECTBUFFERATIPROC) (GLuint buffer);
typedef void (APIENTRY * GL_ARRAYOBJECTATIPROC) (GLenum array, GLint size, GLenum type, GLsizei stride, GLuint buffer, GLuint offset);
typedef void (APIENTRY * GL_GETARRAYOBJECTFVATIPROC) (GLenum array, GLenum pname, GLfloat *params);
typedef void (APIENTRY * GL_GETARRAYOBJECTIVATIPROC) (GLenum array, GLenum pname, GLint *params);
typedef void (APIENTRY * GL_VARIANTARRAYOBJECTATIPROC) (GLuint id, GLenum type, GLsizei stride, GLuint buffer, GLuint offset);
typedef void (APIENTRY * GL_GETVARIANTARRAYOBJECTFVATIPROC) (GLuint id, GLenum pname, GLfloat *params);
typedef void (APIENTRY * GL_GETVARIANTARRAYOBJECTIVATIPROC) (GLuint id, GLenum pname, GLint *params);

typedef void (APIENTRY * GL_ACTIVETEXTUREPROC) (GLenum texture);
typedef void (APIENTRY * GL_CLIENTACTIVETEXTUREPROC) (GLenum texture);
typedef void (APIENTRY * GL_MULTITEXCOORD1DPROC) (GLenum target, GLdouble s);
typedef void (APIENTRY * GL_MULTITEXCOORD1DVPROC) (GLenum target, const GLdouble *v);
typedef void (APIENTRY * GL_MULTITEXCOORD1FPROC) (GLenum target, GLfloat s);
typedef void (APIENTRY * GL_MULTITEXCOORD1FVPROC) (GLenum target, const GLfloat *v);
typedef void (APIENTRY * GL_MULTITEXCOORD1IPROC) (GLenum target, GLint s);
typedef void (APIENTRY * GL_MULTITEXCOORD1IVPROC) (GLenum target, const GLint *v);
typedef void (APIENTRY * GL_MULTITEXCOORD1SPROC) (GLenum target, GLshort s);
typedef void (APIENTRY * GL_MULTITEXCOORD1SVPROC) (GLenum target, const GLshort *v);
typedef void (APIENTRY * GL_MULTITEXCOORD2DPROC) (GLenum target, GLdouble s, GLdouble t);
typedef void (APIENTRY * GL_MULTITEXCOORD2DVPROC) (GLenum target, const GLdouble *v);
typedef void (APIENTRY * GL_MULTITEXCOORD2FPROC) (GLenum target, GLfloat s, GLfloat t);
typedef void (APIENTRY * GL_MULTITEXCOORD2FVPROC) (GLenum target, const GLfloat *v);
typedef void (APIENTRY * GL_MULTITEXCOORD2IPROC) (GLenum target, GLint s, GLint t);
typedef void (APIENTRY * GL_MULTITEXCOORD2IVPROC) (GLenum target, const GLint *v);
typedef void (APIENTRY * GL_MULTITEXCOORD2SPROC) (GLenum target, GLshort s, GLshort t);
typedef void (APIENTRY * GL_MULTITEXCOORD2SVPROC) (GLenum target, const GLshort *v);
typedef void (APIENTRY * GL_MULTITEXCOORD3DPROC) (GLenum target, GLdouble s, GLdouble t, GLdouble r);
typedef void (APIENTRY * GL_MULTITEXCOORD3DVPROC) (GLenum target, const GLdouble *v);
typedef void (APIENTRY * GL_MULTITEXCOORD3FPROC) (GLenum target, GLfloat s, GLfloat t, GLfloat r);
typedef void (APIENTRY * GL_MULTITEXCOORD3FVPROC) (GLenum target, const GLfloat *v);
typedef void (APIENTRY * GL_MULTITEXCOORD3IPROC) (GLenum target, GLint s, GLint t, GLint r);
typedef void (APIENTRY * GL_MULTITEXCOORD3IVPROC) (GLenum target, const GLint *v);
typedef void (APIENTRY * GL_MULTITEXCOORD3SPROC) (GLenum target, GLshort s, GLshort t, GLshort r);
typedef void (APIENTRY * GL_MULTITEXCOORD3SVPROC) (GLenum target, const GLshort *v);
typedef void (APIENTRY * GL_MULTITEXCOORD4DPROC) (GLenum target, GLdouble s, GLdouble t, GLdouble r, GLdouble q);
typedef void (APIENTRY * GL_MULTITEXCOORD4DVPROC) (GLenum target, const GLdouble *v);
typedef void (APIENTRY * GL_MULTITEXCOORD4FPROC) (GLenum target, GLfloat s, GLfloat t, GLfloat r, GLfloat q);
typedef void (APIENTRY * GL_MULTITEXCOORD4FVPROC) (GLenum target, const GLfloat *v);
typedef void (APIENTRY * GL_MULTITEXCOORD4IPROC) (GLenum target, GLint s, GLint t, GLint r, GLint q);
typedef void (APIENTRY * GL_MULTITEXCOORD4IVPROC) (GLenum target, const GLint *v);
typedef void (APIENTRY * GL_MULTITEXCOORD4SPROC) (GLenum target, GLshort s, GLshort t, GLshort r, GLshort q);
typedef void (APIENTRY * GL_MULTITEXCOORD4SVPROC) (GLenum target, const GLshort *v);

typedef void (APIENTRY * GL_ELEMENTPOINTERATIPROC) (GLenum type, const GLvoid *pointer);
typedef void (APIENTRY * GL_DRAWELEMENTARRAYATIPROC) (GLenum mode, GLsizei count);
typedef void (APIENTRY * GL_DRAWRANGEELEMENTARRAYATIPROC) (GLenum mode, GLuint start, GLuint end, GLsizei count);

struct GLContext {
    GLContext();
    static bool hasGLExtension(char *ext);
    static bool hasGLXExtension(char *ext);
    int VersionMinor;
    int VersionMajor;
    bool has_GL_ARB_fragment_program;
    bool has_GL_ATI_texture_float;
    bool has_GL_NV_occlusion_query;
    bool has_GL_ARB_occlusion_query;
    bool has_GL_ATI_vertex_array_object;
    bool has_GL_ATI_element_array;
    bool has_GL_ARB_vertex_buffer_object;

    GL_PROGRAMSTRINGARBPROC ProgramStringARB;
    GL_BINDPROGRAMARBPROC BindProgramARB;
    GL_DELETEPROGRAMSARBPROC DeleteProgramsARB;
    GL_GENPROGRAMSARBPROC GenProgramsARB;
    GL_PROGRAMENVPARAMETER4DARBPROC ProgramEnvParameter4dARB;
    GL_PROGRAMENVPARAMETER4DVARBPROC ProgramEnvParameter4dvARB;
    GL_PROGRAMENVPARAMETER4FARBPROC ProgramEnvParameter4fARB;
    GL_PROGRAMENVPARAMETER4FVARBPROC ProgramEnvParameter4fvARB;
    GL_PROGRAMLOCALPARAMETER4DARBPROC ProgramLocalParameter4dARB;
    GL_PROGRAMLOCALPARAMETER4DVARBPROC ProgramLocalParameter4dvARB;
    GL_PROGRAMLOCALPARAMETER4FARBPROC ProgramLocalParameter4fARB;
    GL_PROGRAMLOCALPARAMETER4FVARBPROC ProgramLocalParameter4fvARB;
    GL_GETPROGRAMENVPARAMETERDVARBPROC GetProgramEnvParameterdvARB;
    GL_GETPROGRAMENVPARAMETERFVARBPROC GetProgramEnvParameterfvARB;
    GL_GETPROGRAMLOCALPARAMETERDVARBPROC GetProgramLocalParameterdvARB;
    GL_GETPROGRAMLOCALPARAMETERFVARBPROC GetProgramLocalParameterfvARB;
    GL_GETPROGRAMIVARBPROC GetProgramivARB;
    GL_GETPROGRAMSTRINGARBPROC GetProgramStringARB;
    GL_ISPROGRAMARBPROC IsProgramARB;

    GL_GENOCCLUSIONQUERIESNVPROC GenOcclusionQueriesNV;
    GL_DELETEOCCLUSIONQUERIESNVPROC DeleteOcclusionQueriesNV;
    GL_ISOCCLUSIONQUERYNVPROC IsOcclusionQueryNV;
    GL_BEGINOCCLUSIONQUERYNVPROC BeginOcclusionQueryNV;
    GL_ENDOCCLUSIONQUERYNVPROC EndOcclusionQueryNV;
    GL_GETOCCLUSIONQUERYIVNVPROC GetOcclusionQueryivNV;
    GL_GETOCCLUSIONQUERYUIVNVPROC GetOcclusionQueryuivNV;

    GL_ACTIVETEXTUREPROC ActiveTexture;
    GL_CLIENTACTIVETEXTUREPROC ClientActiveTexture;
    // GL_MULTITEXCOORD1DPROC
    // GL_MULTITEXCOORD1DVPROC
    // GL_MULTITEXCOORD1FPROC
    // GL_MULTITEXCOORD1FVPROC
    // GL_MULTITEXCOORD1IPROC
    // GL_MULTITEXCOORD1IVPROC
    // GL_MULTITEXCOORD1SPROC
    // GL_MULTITEXCOORD1SVPROC
    // GL_MULTITEXCOORD2DPROC
    // GL_MULTITEXCOORD2DVPROC
    GL_MULTITEXCOORD2FPROC MultiTexCoord2f;
    GL_MULTITEXCOORD2FVPROC MultiTexCoord2fv;
    // GL_MULTITEXCOORD2IPROC
    // GL_MULTITEXCOORD2IVPROC
    // GL_MULTITEXCOORD2SPROC
    // GL_MULTITEXCOORD2SVPROC
    // GL_MULTITEXCOORD3DPROC
    // GL_MULTITEXCOORD3DVPROC
    // GL_MULTITEXCOORD3FPROC
    // GL_MULTITEXCOORD3FVPROC
    // GL_MULTITEXCOORD3IPROC
    // GL_MULTITEXCOORD3IVPROC
    // GL_MULTITEXCOORD3SPROC
    // GL_MULTITEXCOORD3SVPROC
    // GL_MULTITEXCOORD4DPROC
    // GL_MULTITEXCOORD4DVPROC
    // GL_MULTITEXCOORD4FPROC
    // GL_MULTITEXCOORD4FVPROC
    // GL_MULTITEXCOORD4IPROC
    // GL_MULTITEXCOORD4IVPROC
    // GL_MULTITEXCOORD4SPROC
    // GL_MULTITEXCOORD4SVPROC

    GL_NEWOBJECTBUFFERATIPROC NewObjectBufferATI;
    GL_ISOBJECTBUFFERATIPROC IsObjectBufferATI;
    GL_UPDATEOBJECTBUFFERATIPROC UpdateObjectBufferATI;
    GL_GETOBJECTBUFFERFVATIPROC GetObjectBufferfvATI;
    GL_GETOBJECTBUFFERIVATIPROC GetObjectBufferivATI;
    GL_DELETEOBJECTBUFFERATIPROC DeleteObjectBufferATI;
    GL_ARRAYOBJECTATIPROC ArrayObjectATI;
    GL_GETARRAYOBJECTFVATIPROC GetArrayObjectfvATI;
    GL_GETARRAYOBJECTIVATIPROC GetArrayObjectivATI;
    GL_VARIANTARRAYOBJECTATIPROC VariantArrayObjectATI;
    GL_GETVARIANTARRAYOBJECTFVATIPROC GetVariantArrayObjectfvATI;
    GL_GETVARIANTARRAYOBJECTIVATIPROC GetVariantArrayObjectivATI;

    GL_ELEMENTPOINTERATIPROC ElementPointerATI;
    GL_DRAWELEMENTARRAYATIPROC DrawElementArrayATI;
    GL_DRAWRANGEELEMENTARRAYATIPROC DrawRangeElementArrayATI;

    GL_BINDBUFFERARBPROC BindBufferARB;
    GL_DELETEBUFFERSARBPROC DeleteBuffersARB;
    GL_GENBUFFERSARBPROC GenBuffersARB;
    GL_ISBUFFERARBPROC IsBufferARB;
    GL_BUFFERDATAARBPROC BufferDataARB;
    GL_BUFFERSUBDATAARBPROC BufferSubDataARB;
    GL_GETBUFFERSUBDATAARBPROC GetBufferSubDataARB;
    GL_MAPBUFFERARBPROC MapBufferARB;
    GL_UNMAPBUFFERARBPROC UnmapBufferARB;
    GL_GETBUFFERPARAMETERIVARBPROC GetBufferParameterivARB;
    GL_GETBUFFERPOINTERVARBPROC GetBufferPointervARB;

    GL_GENQUERIESARBPROC GenQueriesARB;
    GL_DELETEQUERIESARBPROC DeleteQueriesARB;
    GL_ISQUERYARBPROC IsQueryARB;
    GL_BEGINQUERYARBPROC BeginQueryARB;
    GL_ENDQUERYARBPROC EndQueryARB;
    GL_GETQUERYIVARBPROC GetQueryivARB;
    GL_GETQUERYOBJECTIVARBPROC GetQueryObjectivARB;
    GL_GETQUERYOBJECTUIVARBPROC GetQueryObjectuivARB;

private:
    static bool hasExtension(const unsigned char *exts, char *ext);
    #if defined(_WIN32)
	PROC wsiGetProcAddress(const char *procName);
    #elif !defined(MACOSX) /* Presumably X Window System */
	__GLXextFuncPtr wsiGetProcAddress(const char *procName);
    #endif
};


#endif /* _glextensions_h_ */
