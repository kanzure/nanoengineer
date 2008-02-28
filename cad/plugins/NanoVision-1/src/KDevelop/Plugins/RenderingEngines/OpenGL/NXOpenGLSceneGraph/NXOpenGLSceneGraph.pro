HEADERS += ../../../../../../include/Nanorex/Interface/NXOpenGLMaterial.h \
 ../../../../../../include/Nanorex/Interface/NXOpenGLSceneGraph.h \
 ../../../../../../include/Nanorex/Interface/NXSceneGraph.h

TEMPLATE = lib

CONFIG += staticlib \
debug \
opengl
CONFIG -= release

QT -= gui

TARGET = NXOpenGLSceneGraph

INCLUDEPATH += ../../../../../../include

TARGETDEPS += ../../../../../../lib/libNanorexUtility.so
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLSceneGraph.cpp

DESTDIR = ../../../../../../lib

LIBS += -L../../../../../../lib \
-lNanorexInterface \
-lNanorexUtility

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG

