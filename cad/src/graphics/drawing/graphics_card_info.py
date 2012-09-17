# Copyright 2005-2009 Nanorex, Inc.  See LICENSE file for details.
"""
graphics_card_info.py - def get_gl_info_string, to query OpenGL extensions

@version: $Id$
@copyright: 2005-2009 Nanorex, Inc.  See LICENSE file for details.

History:

051129 Brad G developed (in drawer.py)

(since then, perhaps, minor improvements by various developers)

080519 Russ split up drawer.py; this function ended up in gl_lighting.py

090314 Bruce moved it into its own file
"""

from OpenGL.GL import glAreTexturesResident
from OpenGL.GL import glBegin
from OpenGL.GL import glBindTexture
from OpenGL.GL import glDeleteTextures
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import glEnd
from OpenGL.GL import GL_EXTENSIONS
from OpenGL.GL import glFinish
from OpenGL.GL import glGenTextures
from OpenGL.GL import glGetInteger
from OpenGL.GL import glGetString
from OpenGL.GL import GL_QUADS
from OpenGL.GL import GL_RENDERER
from OpenGL.GL import GL_RGBA
from OpenGL.GL import glTexCoord2f
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import GL_VENDOR
from OpenGL.GL import GL_VERSION
from OpenGL.GL import glVertex2f

from OpenGL.GLU import gluBuild2DMipmaps

from utilities.debug_prefs import debug_pref, Choice_boolean_False

from utilities import debug_flags
from utilities.debug import print_compact_traceback

# ==

def get_gl_info_string(glpane): # grantham 20051129
    """
    Return a string containing some useful information about the OpenGL
    implementation.

    Use the GL context from the given QGLWidget glpane (by calling
    glpane.makeCurrent()).
    """

    glpane.makeCurrent() #bruce 070308 added glpane arg and makeCurrent call

    gl_info_string = ''

    gl_info_string += 'GL_VENDOR : "%s"\n' % glGetString(GL_VENDOR)
    gl_info_string += 'GL_VERSION : "%s"\n' % glGetString(GL_VERSION)
    gl_info_string += 'GL_RENDERER : "%s"\n' % glGetString(GL_RENDERER)
    gl_extensions = glGetString(GL_EXTENSIONS)
    gl_extensions = gl_extensions.strip()
    gl_extensions = gl_extensions.replace(" ", "\n* ")
    gl_info_string += 'GL_EXTENSIONS : \n* %s\n' % gl_extensions

    if debug_pref("Graphics Card Info: call glAreTexturesResident?",
                  Choice_boolean_False):
        # Give a practical indication of how much video memory is available.
        # Should also do this with VBOs.

        # I'm pretty sure this code is right, but PyOpenGL seg faults in
        # glAreTexturesResident, so it's disabled until I can figure that
        # out. [grantham] [bruce 070308 added the debug_pref]

        all_tex_in = True
        tex_bytes = '\0' * (512 * 512 * 4)
        tex_names = []
        tex_count = 0
        tex_names = glGenTextures(1024)
        glEnable(GL_TEXTURE_2D)
        while all_tex_in:
            glBindTexture(GL_TEXTURE_2D, tex_names[tex_count])
            gluBuild2DMipmaps(GL_TEXTURE_2D, 4, 512, 512, GL_RGBA,
                              GL_UNSIGNED_BYTE, tex_bytes)
            tex_count += 1

            glTexCoord2f(0.0, 0.0)
            glBegin(GL_QUADS)
            glVertex2f(0.0, 0.0)
            glVertex2f(1.0, 0.0)
            glVertex2f(1.0, 1.0)
            glVertex2f(0.0, 1.0)
            glEnd()
            glFinish()

            residences = glAreTexturesResident(tex_names[:tex_count])
            all_tex_in = reduce(lambda a,b: a and b, residences)
                # bruce 070308 sees this exception from this line:
                # TypeError: reduce() arg 2 must support iteration

        glDisable(GL_TEXTURE_2D)
        glDeleteTextures(tex_names)

        gl_info_string += "Could create %d 512x512 RGBA resident textures\n" \
                          % tex_count
        pass

    if True: ## or could be a debug_pref("Graphics Card Info: get all GL_MAX symbols?")
        #bruce 090314 new feature
        import OpenGL.GL
        symbols = [x for x in dir(OpenGL.GL) if x.startswith('GL_MAX_')]
        symbols.sort()
        gl_info_string += '\n'
        for symbol in symbols:
            try:
                numeric_symbol = getattr(OpenGL.GL, symbol)
                intval = glGetInteger(numeric_symbol)
            except:
                # this happens to most symbols, not sure why
                if debug_flags.atom_debug:
                    print_compact_traceback( "%s = ??: " % symbol )
                        # overkill, only the exception itself matters
                    # typical output (on Bruce's MacBookPro, 090314):
                    ## GL_MAX_4D_TEXTURE_SIZE_SGIS = ??:
                    ## <type 'exceptions.KeyError'>:
                    ## ('Unknown specifier GL_MAX_4D_TEXTURE_SIZE_SGIS (33080)',
                    ##  'Failure in cConverter <OpenGL.converters.SizedOutput object at 0x1457fab0>',
                    ##  [GL_MAX_4D_TEXTURE_SIZE_SGIS], 1, <OpenGL.wrapper.glGetIntegerv object at 0x1458aa30>)
                    ## [graphics_card_info.py:122] [wrapper.py:676] [converters.py:195] [converters.py:234]
                    pass
                pass ## gl_info_string += "%s = ??\n" % symbol
            else:
                gl_info_string += "%s = %r\n" % (symbol, intval)
            continue
        pass

    return gl_info_string

# end
