SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRendererPlugin.cpp
TEMPLATE = lib

CONFIG += opengl \
 dll \
 debug_and_release
win32: CONFIG -= dll
win32: CONFIG += staticlib

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
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

DESTDIR = ../../../../../../lib

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline

LIBS += -L../../../../../../lib \
 -lNanorexInterface \
 -lNXOpenGLSceneGraph \
 -lNanorexUtility \
 -lGLT
# qmake puts these library declarations too early in the g++ command on win32
win32 : LIBS += -lopengl32 -lglu32 -lgdi32 -luser32

