TEMPLATE = lib

CONFIG += dll \
plugin \
debug \
stl \
opengl
CONFIG -= release

QT += opengl

HEADERS += NXOpenGLRendererPlugin.h \
NXRendererPlugin.h \
NXSceneGraph.h \
NXAtomRenderData.h \
NXBondRenderData.h \
NXRGBColor.h \
NXOpenGLMaterial.h \
 NXBallAndStickOpenGLRenderer.h
SOURCES += NXBallAndStickOpenGLRenderer.cpp

TARGETDEPS += ../../../../../../../lib/libNanorexUtility.so \
../../../../../../../lib/libNanorexInterface.so \
 ../../../../../../../lib/libNXOpenGLRendererPlugin.a
TARGET = BallAndStickOpenGLRenderer

DESTDIR = ../../../../../../../lib

INCLUDEPATH += ../../NXOpenGLRendererPlugin \
../../../../../../../include
LIBS += -L../../../../../../../lib \
-lNXOpenGLRendererPlugin \
-lNXOpenGLSceneGraph
