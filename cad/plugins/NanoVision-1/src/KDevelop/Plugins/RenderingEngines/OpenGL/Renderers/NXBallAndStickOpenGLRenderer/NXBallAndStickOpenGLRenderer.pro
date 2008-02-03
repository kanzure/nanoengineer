TEMPLATE = lib

CONFIG += dll \
plugin \
debug \
stl \
opengl
CONFIG -= release

QT += opengl

HEADERS += ../../../../../../../include/Nanorex/Interface/NXAtomRenderData.h \
 ../../../../../../../include/Nanorex/Interface/NXBondRenderData.h \
 ../../../../../../../include/Nanorex/Interface/NXOpenGLMaterial.h \
 ../../../../../../../include/Nanorex/Interface/NXOpenGLRendererPlugin.h \
 ../../../../../../../include/Nanorex/Interface/NXRendererPlugin.h \
 ../../../../../../../include/Nanorex/Interface/NXRGBColor.h \
 ../../../../../../../include/Nanorex/Interface/NXSceneGraph.h \
 ../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.h

TARGETDEPS += ../../../../../../../lib/libNanorexUtility.so \
../../../../../../../lib/libNanorexInterface.so \
 ../../../../../../../lib/libNXOpenGLRendererPlugin.a

DESTDIR = ../../../../../../../lib

INCLUDEPATH += ../../NXOpenGLRendererPlugin \
../../../../../../../include
LIBS += -lNXOpenGLRendererPlugin \
-lNXOpenGLSceneGraph \
 -L../../../../../../../lib
SOURCES += ../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.cpp

TARGET = NXBallAndStickOpenGLRenderer

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG

