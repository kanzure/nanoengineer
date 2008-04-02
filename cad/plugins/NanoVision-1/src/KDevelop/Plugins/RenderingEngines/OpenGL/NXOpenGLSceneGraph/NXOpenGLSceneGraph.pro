HEADERS += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLMaterial.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLSceneGraph.h \
 ../../../../../../include/Nanorex/Interface/NXSceneGraph.h

TEMPLATE = lib

CONFIG += staticlib \
opengl \
 debug_and_release \
 rtti

QT -= gui

TARGET = NXOpenGLSceneGraph

INCLUDEPATH += ../../../../../../include

TARGETDEPS += ../../../../../../lib/libNanorexUtility.so
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLSceneGraph.cpp

DESTDIR = ../../../../../../lib


QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline

QT += opengl

