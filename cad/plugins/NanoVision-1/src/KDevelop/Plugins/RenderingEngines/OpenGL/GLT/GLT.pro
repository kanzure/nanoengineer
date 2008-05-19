
TEMPLATE = lib
TARGET = GLT
DESTDIR = ../../../../../../lib/

CONFIG -= qt \
 thread 

CONFIG += opengl \
 staticlib \
 release

#CONFIG(debug,debug|release){
#    TARGET = $$join(TARGET,,,_d)
#}

QT -= core \
 gui

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
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/glt_rgb.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/GLT/guarded_gl_ops.h

#QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
#-g \
#-O0 \
#-fno-inline

QMAKE_CXXFLAGS_RELEASE += -DNDEBUG -O2

# make clean targets
unix : QMAKE_CLEAN += $${DESTDIR}lib$${TARGET}.a
macx : QMAKE_CLEAN += $${DESTDIR}lib$${TARGET}.a
win32 : QMAKE_CLEAN += $${DESTDIR}$${TARGET}.lib

