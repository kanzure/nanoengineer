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

LIBS += -L../../../../../../lib \
-lNanorexUtility \
-lNanorexInterface \
../GLT/libGLT.a \
 -lNXOpenGLSceneGraph \
 -lGLT
TARGETDEPS += ../../../../../../lib/libNanorexUtility.so \
../../../../../../lib/libNanorexInterface.so \
../GLT/libGLT.a \
 ../../../../../../lib/libNXOpenGLSceneGraph.a
TARGET = NXOpenGLRenderingEngine

DESTDIR = ../../../../../../lib

SOURCES += NXOpenGLRenderingEngine.cpp

