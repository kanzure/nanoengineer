TEMPLATE = lib

CONFIG += dll \
 debug \
 stl \
 opengl \
 plugin

HEADERS += ../../../../../../include/Nanorex/Interface/NXAtomRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXBondRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXEntityManager.h \
 ../../../../../../include/Nanorex/Interface/NXOpenGLRendererPlugin.h \
 ../../../../../../include/Nanorex/Interface/NXOpenGLRenderingEngine.h \
 ../../../../../../include/Nanorex/Interface/NXRendererPlugin.h \
 ../../../../../../include/Nanorex/Interface/NXRenderingEngine.h \
 ../../../../../../include/Nanorex/Interface/NXRGBColor.h \
 ../../../../../../include/Nanorex/Interface/NXSceneGraph.h
CONFIG -= release

QT += opengl

INCLUDEPATH += ../../../../../../include \
 ../../../../../../src/Plugins/RenderingEngines/OpenGL/GLT \
 $(OPENBABEL_INCPATH)

LIBS += -lNXOpenGLSceneGraph \
 -lGLT \
 -lopenbabel \
 -L../../../../../../lib
TARGETDEPS += ../../../../../../lib/libNanorexUtility.so \
../../../../../../lib/libNanorexInterface.so \
../../../../../../lib/libNXOpenGLSceneGraph.a \
 ../../../../../../lib/libGLT.a
TARGET = NXOpenGLRenderingEngine

DESTDIR = ../../../../../../lib

SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine.cpp

