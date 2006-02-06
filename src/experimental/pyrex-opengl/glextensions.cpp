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

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "glextensions.h"

/* Check extensions string for an extension substring */
bool GLContext::hasExtension(const unsigned char *exts, char *ext)
{
    static char extStringSpace[512];

    if(exts == NULL || ext == NULL)
        return false;

    if(strcmp((char *)exts + strlen((char *)exts) - strlen(ext), ext) == 0) {
	return true;
    }

    sprintf(extStringSpace, "%s ", ext);
    return (strstr((const char *)exts, extStringSpace) != NULL);
}

/* Check GL strings for an extension */
bool GLContext::hasGLExtension(char *ext)
{
    return hasExtension(glGetString(GL_EXTENSIONS), ext);
}

#if !defined(_WIN32)

/*
 * GLUT doesn't expose a Display*, which we need in order to check
 * GLX extensions.  So we guess a little bit on the Display* that was
 * opened and hope for the best.
 */
static Display *getTheDisplay(void)
{
    static Display *dsp = NULL;

    if(dsp == NULL) {
	// I hope this is pretty close to what GLUT has opened.
	if(getenv("DISPLAY") != NULL)
	    dsp = XOpenDisplay(getenv("DISPLAY"));
	else
	    dsp = XOpenDisplay(":0.0");

	if(dsp == NULL) {
	    fprintf(stderr, "Couldn't open X Display\n");
	    exit(1);
	}
    }

    return dsp;
}

/* Check GLX strings for an extension */
bool GLContext::hasGLXExtension(char *ext)
{
    return hasExtension((const unsigned char *)
           glXGetClientString(getTheDisplay(), GLX_EXTENSIONS), ext)
        && hasExtension((const unsigned char *)
	   glXQueryExtensionsString(getTheDisplay(), 0), ext);
}

#endif

#if defined(_WIN32)

PROC GLContext::wsiGetProcAddress(const char *procName)
{
    PROC proc;
   
    proc =  wglGetProcAddress((LPCSTR)procName);

    if(proc == NULL) {
        fprintf(stderr, "wsiGetProcAddress asked for \"%s\" and "
            "received NULL.\n", procName);
    }

    return proc;
}

#else /* !defined(_WIN32) */

__GLXextFuncPtr GLContext::wsiGetProcAddress(const char *procName)
{
    __GLXextFuncPtr proc;
   
    proc =  glXGetProcAddressARB((const GLubyte *)procName);

    if(proc == NULL) {
        fprintf(stderr, "wsiGetProcAddress asked for \"%s\" and "
            "received NULL.\n", procName);
    }

    return proc;
}

#endif /* defined(_WIN32) */

GLContext::GLContext(void)
{
    char *version;

    version = (char *)glGetString(GL_VERSION);

    if(version == NULL) {
        // 20060206 - grantham
        // Potentially report failure to caller requesting "new"
        // App can check version numbers, I suppose.
        VersionMajor = 0;
        VersionMinor = 0;
    } else
        sscanf(version, "%d.%d", &VersionMajor, &VersionMinor);

    if(hasGLExtension("GL_ATI_texture_float")) {
	has_GL_ARB_fragment_program = true;
    } else
	has_GL_ARB_fragment_program = false;

    if(hasGLExtension("GL_NV_occlusion_query")) {
	has_GL_NV_occlusion_query = true;

        GenOcclusionQueriesNV = (GL_GENOCCLUSIONQUERIESNVPROC)
            wsiGetProcAddress("glGenOcclusionQueriesNV");
        DeleteOcclusionQueriesNV = (GL_DELETEOCCLUSIONQUERIESNVPROC)
            wsiGetProcAddress("glDeleteOcclusionQueriesNV");
        IsOcclusionQueryNV = (GL_ISOCCLUSIONQUERYNVPROC)
            wsiGetProcAddress("glIsOcclusionQueryNV");
        BeginOcclusionQueryNV = (GL_BEGINOCCLUSIONQUERYNVPROC)
            wsiGetProcAddress("glBeginOcclusionQueryNV");
        EndOcclusionQueryNV = (GL_ENDOCCLUSIONQUERYNVPROC)
            wsiGetProcAddress("glEndOcclusionQueryNV");
        GetOcclusionQueryivNV = (GL_GETOCCLUSIONQUERYIVNVPROC)
            wsiGetProcAddress("glGetOcclusionQueryivNV");
        GetOcclusionQueryuivNV = (GL_GETOCCLUSIONQUERYUIVNVPROC)
            wsiGetProcAddress("glGetOcclusionQueryuivNV");
    } else
	has_GL_NV_occlusion_query = false;

    if(hasGLExtension("GL_ARB_occlusion_query")) {
	has_GL_ARB_occlusion_query = true;

        GenQueriesARB = (GL_GENQUERIESARBPROC)
            wsiGetProcAddress("glGenQueriesARB");
        DeleteQueriesARB = (GL_DELETEQUERIESARBPROC)
            wsiGetProcAddress("glDeleteQueriesARB");
        IsQueryARB = (GL_ISQUERYARBPROC)
            wsiGetProcAddress("glIsQueryARB");
        BeginQueryARB = (GL_BEGINQUERYARBPROC)
            wsiGetProcAddress("glBeginQueryARB");
        EndQueryARB = (GL_ENDQUERYARBPROC)
            wsiGetProcAddress("glEndQueryARB");
        GetQueryObjectivARB = (GL_GETQUERYOBJECTIVARBPROC)
            wsiGetProcAddress("glGetQueryObjectivARB");
        GetQueryObjectuivARB = (GL_GETQUERYOBJECTUIVARBPROC)
            wsiGetProcAddress("glGetQueryObjectuivARB");
    } else
	has_GL_ARB_occlusion_query = false;

    if(hasGLExtension("GL_ATI_vertex_array_object")) {
	has_GL_ATI_vertex_array_object = true;

        NewObjectBufferATI = (GL_NEWOBJECTBUFFERATIPROC)
            wsiGetProcAddress("glNewObjectBufferATI");
        IsObjectBufferATI = (GL_ISOBJECTBUFFERATIPROC)
            wsiGetProcAddress("glIsObjectBufferATI");
        UpdateObjectBufferATI = (GL_UPDATEOBJECTBUFFERATIPROC)
            wsiGetProcAddress("glUpdateObjectBufferATI");
        GetObjectBufferfvATI = (GL_GETOBJECTBUFFERFVATIPROC)
            wsiGetProcAddress("glGetObjectBufferfvATI");
        GetObjectBufferivATI = (GL_GETOBJECTBUFFERIVATIPROC)
            wsiGetProcAddress("glGetObjectBufferivATI");
        DeleteObjectBufferATI = (GL_DELETEOBJECTBUFFERATIPROC)
            wsiGetProcAddress("glDeleteObjectBufferATI");
        ArrayObjectATI = (GL_ARRAYOBJECTATIPROC)
            wsiGetProcAddress("glArrayObjectATI");
        GetArrayObjectfvATI = (GL_GETARRAYOBJECTFVATIPROC)
            wsiGetProcAddress("glGetArrayObjectfvATI");
        GetArrayObjectivATI = (GL_GETARRAYOBJECTIVATIPROC)
            wsiGetProcAddress("glGetArrayObjectivATI");
        VariantArrayObjectATI = (GL_VARIANTARRAYOBJECTATIPROC)
            wsiGetProcAddress("glVariantArrayObjectATI");
        GetVariantArrayObjectfvATI = (GL_GETVARIANTARRAYOBJECTFVATIPROC)
            wsiGetProcAddress("glGetVariantArrayObjectfvATI");
        GetVariantArrayObjectivATI = (GL_GETVARIANTARRAYOBJECTIVATIPROC)
            wsiGetProcAddress("glGetVariantArrayObjectivATI");
    } else
	has_GL_ATI_vertex_array_object = false;

    if(hasGLExtension("GL_ATI_element_array")) {
	has_GL_ATI_element_array = true;

        ElementPointerATI = (GL_ELEMENTPOINTERATIPROC)
            wsiGetProcAddress("glElementPointerATI");
        DrawElementArrayATI = (GL_DRAWELEMENTARRAYATIPROC)
            wsiGetProcAddress("glDrawElementArrayATI");
        DrawRangeElementArrayATI = (GL_DRAWRANGEELEMENTARRAYATIPROC)
            wsiGetProcAddress("glDrawRangeElementArrayATI");
    } else
	has_GL_ATI_element_array = false;

    if(hasGLExtension("GL_ARB_vertex_buffer_object")) {
	has_GL_ARB_vertex_buffer_object = true;

        BindBufferARB = (GL_BINDBUFFERARBPROC)
            wsiGetProcAddress("glBindBufferARB");
        DeleteBuffersARB = (GL_DELETEBUFFERSARBPROC)
            wsiGetProcAddress("glDeleteBuffersARB");
        GenBuffersARB = (GL_GENBUFFERSARBPROC)
            wsiGetProcAddress("glGenBuffersARB");
        IsBufferARB = (GL_ISBUFFERARBPROC)
            wsiGetProcAddress("glIsBufferARB");
        BufferDataARB = (GL_BUFFERDATAARBPROC)
            wsiGetProcAddress("glBufferDataARB");
        BufferSubDataARB = (GL_BUFFERSUBDATAARBPROC)
            wsiGetProcAddress("glBufferSubDataARB");
        GetBufferSubDataARB = (GL_GETBUFFERSUBDATAARBPROC)
            wsiGetProcAddress("glGetBufferSubDataARB");
        MapBufferARB = (GL_MAPBUFFERARBPROC)
            wsiGetProcAddress("glMapBufferARB");
        UnmapBufferARB = (GL_UNMAPBUFFERARBPROC)
            wsiGetProcAddress("glUnmapBufferARB");
        GetBufferParameterivARB = (GL_GETBUFFERPARAMETERIVARBPROC)
            wsiGetProcAddress("glGetBufferParameterivARB");
        GetBufferPointervARB = (GL_GETBUFFERPOINTERVARBPROC)
            wsiGetProcAddress("glGetBufferPointervARB");
    } else
	has_GL_ARB_vertex_buffer_object = false;

    if(hasGLExtension("GL_ARB_fragment_program")) {
	has_GL_ARB_fragment_program = true;

        ProgramStringARB = (GL_PROGRAMSTRINGARBPROC)
            wsiGetProcAddress("glProgramStringARB");
        BindProgramARB = (GL_BINDPROGRAMARBPROC)
            wsiGetProcAddress("glBindProgramARB");
        DeleteProgramsARB = (GL_DELETEPROGRAMSARBPROC)
            wsiGetProcAddress("glDeleteProgramsARB");
        GenProgramsARB = (GL_GENPROGRAMSARBPROC)
            wsiGetProcAddress("glGenProgramsARB");
        ProgramEnvParameter4dARB = (GL_PROGRAMENVPARAMETER4DARBPROC)
            wsiGetProcAddress("glProgramEnvParameter4dARB");
        ProgramEnvParameter4dvARB = (GL_PROGRAMENVPARAMETER4DVARBPROC)
            wsiGetProcAddress("glProgramEnvParameter4dvARB");
        ProgramEnvParameter4fARB = (GL_PROGRAMENVPARAMETER4FARBPROC)
            wsiGetProcAddress("glProgramEnvParameter4fARB");
        ProgramEnvParameter4fvARB = (GL_PROGRAMENVPARAMETER4FVARBPROC)
            wsiGetProcAddress("glProgramEnvParameter4fvARB");
        ProgramLocalParameter4dARB = (GL_PROGRAMLOCALPARAMETER4DARBPROC)
            wsiGetProcAddress("glProgramLocalParameter4dARB");
        ProgramLocalParameter4dvARB = (GL_PROGRAMLOCALPARAMETER4DVARBPROC)
            wsiGetProcAddress("glProgramLocalParameter4dvARB");
        ProgramLocalParameter4fARB = (GL_PROGRAMLOCALPARAMETER4FARBPROC)
            wsiGetProcAddress("glProgramLocalParameter4fARB");
        ProgramLocalParameter4fvARB = (GL_PROGRAMLOCALPARAMETER4FVARBPROC)
            wsiGetProcAddress("glProgramLocalParameter4fvARB");
        GetProgramEnvParameterdvARB = (GL_GETPROGRAMENVPARAMETERDVARBPROC)
            wsiGetProcAddress("glGetProgramEnvParameterdvARB");
        GetProgramEnvParameterfvARB = (GL_GETPROGRAMENVPARAMETERFVARBPROC)
            wsiGetProcAddress("glGetProgramEnvParameterfvARB");
        GetProgramLocalParameterdvARB = (GL_GETPROGRAMLOCALPARAMETERDVARBPROC)
            wsiGetProcAddress("glGetProgramLocalParameterdvARB");
        GetProgramLocalParameterfvARB = (GL_GETPROGRAMLOCALPARAMETERFVARBPROC)
            wsiGetProcAddress("glGetProgramLocalParameterfvARB");
        GetProgramivARB = (GL_GETPROGRAMIVARBPROC)
            wsiGetProcAddress("glGetProgramivARB");
        GetProgramStringARB = (GL_GETPROGRAMSTRINGARBPROC)
            wsiGetProcAddress("glGetProgramStringARB");
        IsProgramARB = (GL_ISPROGRAMARBPROC)
            wsiGetProcAddress("glIsProgramARB");
    } else
	has_GL_ARB_fragment_program = true;

    if(VersionMinor >= 3) {
        ActiveTexture = (GL_ACTIVETEXTUREPROC)
            wsiGetProcAddress("glActiveTexture");
        ClientActiveTexture = (GL_CLIENTACTIVETEXTUREPROC)
            wsiGetProcAddress("glClientActiveTexture");
        MultiTexCoord2f = (GL_MULTITEXCOORD2FPROC)
            wsiGetProcAddress("glMultiTexCoord2f");
        MultiTexCoord2fv = (GL_MULTITEXCOORD2FVPROC)
            wsiGetProcAddress("glMultiTexCoord2fv");
        if(ActiveTexture == NULL) {
            fprintf(stderr, "Activating buggy GetProcAddress workaround "
                "for Multitexture functions...\n");
            ActiveTexture = (GL_ACTIVETEXTUREPROC)
                wsiGetProcAddress("glActiveTextureARB");
            ClientActiveTexture = (GL_CLIENTACTIVETEXTUREPROC)
                wsiGetProcAddress("glClientActiveTextureARB");
            MultiTexCoord2f = (GL_MULTITEXCOORD2FPROC)
                wsiGetProcAddress("glMultiTexCoord2fARB");
            MultiTexCoord2fv = (GL_MULTITEXCOORD2FVPROC)
                wsiGetProcAddress("glMultiTexCoord2fvARB");
        }
    }
}

