SOURCES += NXOpenGLRendererPlugin.cpp
TEMPLATE = lib

CONFIG += staticlib \
debug \
opengl
CONFIG -= release
TARGET = NXOpenGLRendererPlugin

HEADERS += NXAtomRenderData.h \
NXBondRenderData.h \
NXOpenGLMaterial.h \
NXOpenGLRendererPlugin.h \
NXRendererPlugin.h \
NXRGBColor.h \
NXSceneGraph.h \
NXOpenGLSceneGraph.h
INCLUDEPATH += ../../../../../../include

QT -= gui

LIBS += NXSceneGraph
TARGETDEPS += ../../../../../../lib/libNXOpenGLSceneGraph.a

DESTDIR = ../../../../../../lib

