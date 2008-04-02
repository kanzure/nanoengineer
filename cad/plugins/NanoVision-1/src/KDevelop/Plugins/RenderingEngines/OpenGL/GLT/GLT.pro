
CONFIG -= qt \
thread \
 release

CONFIG += opengl \
staticlib \
 debug_and_release

QT -= core \
gui

TEMPLATE = lib

SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/GLT/bbox.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/color.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/error.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/light.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/lightm.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/material.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/matrix4.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/project.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/string.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/texture.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/umatrix.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/vector3.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/vector4.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/viewport.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/rgb.cpp
TARGET = GLT

HEADERS += ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_bbox.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_color.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_config.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_error.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_gl.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_glu.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_light.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_lightm.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_material.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_matrix4.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_project.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_real.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_refcount.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_string.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_texture.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_umatrix.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_vector3.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_vector4.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_viewport.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_rgb.h
DESTDIR = ../../../../../../lib/

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
-g \
-O0 \
-fno-inline
