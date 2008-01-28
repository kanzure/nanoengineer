TEMPLATE = lib

CONFIG += dll \
 debug \
 stl \
 opengl \
 plugin

HEADERS += NXSceneGraph.h \
 NXOpenGLRendererPlugin.h \
 NXRendererPlugin.h \
 NXAtomRenderData.h \
 NXOpenGLRenderingEngine.h \
 NXRGBColor.h \
 NXBondRenderData.h \
 NXEntityManager.h \
 NXRenderingEngine.h
CONFIG -= release

QT += opengl

INCLUDEPATH += ../../../../../../include \
 /usr/include/openbabel-2.0 \
 ../../../../../../src/Plugins/RenderingEngines/OpenGL/GLT

LIBS += -lNXOpenGLSceneGraph \
 -lGLT \
 -L../../../../../../lib
TARGETDEPS += ../../../../../../lib/libNanorexUtility.so \
../../../../../../lib/libNanorexInterface.so \
../../../../../../lib/libNXOpenGLSceneGraph.a \
 ../../../../../../lib/libGLT.a
TARGET = NXOpenGLRenderingEngine

DESTDIR = ../../../../../../lib

SOURCES += NXOpenGLRenderingEngine.cpp

