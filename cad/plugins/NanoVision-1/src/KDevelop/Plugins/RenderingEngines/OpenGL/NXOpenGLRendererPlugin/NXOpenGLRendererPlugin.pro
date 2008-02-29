SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRendererPlugin.cpp
TEMPLATE = lib

CONFIG += staticlib \
debug \
opengl
CONFIG -= release
TARGET = NXOpenGLRendererPlugin

HEADERS += ../../../../../../include/Nanorex/Interface/NXAtomRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXBondRenderData.h \
 ../../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLMaterial.h \
 ../../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRendererPlugin.h \
 ../../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLSceneGraph.h \
 ../../../../../../include/Nanorex/Interface/NXRendererPlugin.h
INCLUDEPATH += ../../../../../../include

QT -= gui

LIBS += NXSceneGraph
TARGETDEPS += ../../../../../../lib/libNXOpenGLSceneGraph.a

DESTDIR = ../../../../../../lib

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG

