SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRendererPlugin.cpp
TEMPLATE = lib

CONFIG += staticlib \
debug \
opengl
CONFIG -= release
TARGET = NXOpenGLRendererPlugin

HEADERS += ../../../../../../include/Nanorex/Interface/NXAtomRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXBondRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXOpenGLMaterial.h \
 ../../../../../../include/Nanorex/Interface/NXOpenGLRendererPlugin.h \
 ../../../../../../include/Nanorex/Interface/NXOpenGLSceneGraph.h \
 ../../../../../../include/Nanorex/Interface/NXRendererPlugin.h
INCLUDEPATH += ../../../../../../include

QT -= gui

LIBS += NXSceneGraph
TARGETDEPS += ../../../../../../lib/libNXOpenGLSceneGraph.a

DESTDIR = ../../../../../../lib

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG

