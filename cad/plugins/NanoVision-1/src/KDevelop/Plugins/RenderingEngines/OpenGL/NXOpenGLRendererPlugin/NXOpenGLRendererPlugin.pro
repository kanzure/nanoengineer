SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRendererPlugin.cpp
TEMPLATE = lib

CONFIG += opengl \
 dll \
 debug \
 debug_and_release

TARGET = NXOpenGLRendererPlugin

HEADERS += ../../../../../../include/Nanorex/Interface/NXAtomRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXBondRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXRendererPlugin.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLMaterial.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRendererPlugin.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLSceneGraph.h
INCLUDEPATH += ../../../../../../include \
 ../../../../../../src/Plugins/RenderingEngines/OpenGL

QT -= gui

TARGETDEPS += ../../../../../../lib/libNXOpenGLSceneGraph.a \
 ../../../../../../lib/libGLT.a \
 ../../../../../../lib/libNanorexInterface.so \
 ../../../../../../lib/libNanorexUtility.so

DESTDIR = ../../../../../../lib

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline

CONFIG -= release

