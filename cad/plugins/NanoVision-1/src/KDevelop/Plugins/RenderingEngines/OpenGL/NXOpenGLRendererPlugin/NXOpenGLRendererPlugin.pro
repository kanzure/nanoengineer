TEMPLATE = lib

CONFIG += opengl \
 dll \
 debug_and_release

CONFIG(debug,debug|release) {
	TARGET = $$join(TARGET,,,_d)
}

win32 : CONFIG -= dll
win32 : CONFIG += staticlib

TARGET = NXOpenGLRendererPlugin

HEADERS += ../../../../../../include/Nanorex/Interface/NXAtomRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXBondRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXRendererPlugin.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLMaterial.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRendererPlugin.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLSceneGraph.h

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

# qmake puts these library declarations too early in the g++ command on win32
win32 : LIBS += -lopengl32 -lglu32 -lgdi32 -luser32


INCLUDEPATH += $(OPENBABEL_INCPATH) \
  ../../../../../../include \
  ../../../../../../src/Plugins/RenderingEngines/OpenGL

LIBS += -L../../../../../../lib \
  -lNanorexInterface \
  -lNanorexUtility \
  -lNXOpenGLSceneGraph \
  -lGLT

