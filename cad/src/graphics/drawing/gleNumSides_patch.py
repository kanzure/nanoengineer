# Patch the gle[GS]etNumSides functions to call gle[GS]etNumSlices.
#
# This can be loaded only if needed, for example:
# try:
#     from OpenGL.GLE import gleGetNumSides, gleSetNumSides
# except:
#     print "GLE module can't be imported. Now trying _GLE"
#     from OpenGL._GLE import gleGetNumSides, gleSetNumSides
# if not bool(gleGetNumSides):
#     from graphics.drawing.gleNumSides_patch import gleGetNumSides
#     from graphics.drawing.gleNumSides_patch import gleSetNumSides

# Only the interface to gle[GS]etNumSides is in PyOpenGL-3.0.0a6.
# On 10.5.2 (Leoplard), only gle[GS]etNumSlices is in the shared lib file:
# /System/Library/Frameworks/glut.framework/glut .
#
# Maybe Apple had included an earlier version of GLE in the Mac port.
# GLE was not actually not an official part of OpenGL until GLUT 3.6:
#    http://www.opengl.org/resources/libraries/glut/glut_downloads.php#3.6
#
#    Linas Vesptas's GLE Tubing and Extrusion library
#    <http://linas.org/gle/index.html> with documentation and example
#    programs is now a part of GLUT.

# The following was extracted and modified from gle[GS]etNumSides in
#    /Library/Python/2.5/site-packages/PyOpenGL-3.0.0a6-py2.5.egg/
#        OpenGL/raw/GLE/__init__.py

from ctypes import c_int
from OpenGL import platform, arrays
from OpenGL.constant import Constant
from OpenGL import constants as GLconstants

# /usr/include/GL/gle.h 114
gleGetNumSides = platform.createBaseFunction(
        'gleGetNumSlices', dll=platform.GLE, resultType=c_int,
        argTypes=[],
        doc='gleGetNumSlices(  ) -> c_int',
        argNames=(),
)

# /usr/include/GL/gle.h 115
gleSetNumSides = platform.createBaseFunction(
        'gleSetNumSlices', dll=platform.GLE, resultType=None,
        argTypes=[c_int],
        doc='gleSetNumSlices( c_int(slices) ) -> None',
        argNames=('slices',),
)
