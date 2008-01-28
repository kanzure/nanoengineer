CONFIG -= release \
qt \
thread
CONFIG += debug \
opengl \
staticlib
QT -= core \
gui
TEMPLATE = lib

SOURCES += color.cpp \
light.cpp \
lightm.cpp \
material.cpp \
vector3.cpp \
error.cpp \
string.cpp \
viewport.cpp \
matrix4.cpp \
texture.cpp \
bbox.cpp \
umatrix.cpp \
vector4.cpp \
project.cpp
TARGET = GLT

HEADERS += glt_bbox.h \
glt_color.h \
glt_config.h \
glt_error.h \
glt_gl.h \
glt_glu.h \
glt_light.h \
glt_lightm.h \
glt_matrix4.h \
glt_string.h \
glt_texture.h \
glt_umatrix.h \
glt_vector3.h \
glt_viewport.h \
glt_material.h \
glt_real.h \
glt_refcount.h \
glt_vector4.h \
glt_project.h
DESTDIR = ../../../../../../lib/

