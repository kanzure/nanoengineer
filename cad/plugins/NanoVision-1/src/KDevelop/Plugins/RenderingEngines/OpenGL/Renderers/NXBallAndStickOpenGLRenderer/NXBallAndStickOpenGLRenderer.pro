TEMPLATE = lib

CONFIG += debug_and_release \
stl \
opengl \
staticlib
# dll
# plugin

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
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

DESTDIR = ../../../../../../../lib

INCLUDEPATH += ../../NXOpenGLRendererPlugin \
../../../../../../../include

LIBS += -L../../../../../../../lib \
 -lNXOpenGLRendererPlugin \
 -lNXOpenGLSceneGraph \
 -lNanorexUtility \
 -lNanorexInterface
# qmake puts these library declarations too early in the g++ command on win32
win32 : LIBS += -lopengl32 -lglu32 -lgdi32 -luser32

SOURCES += ../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.cpp

TARGET = NXBallAndStickOpenGLRenderer

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG

# Remove the "lib" from the start of the library
# unix : QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs mv $(DESTDIR)$(TARGET)
# macx : QMAKE_POST_LINK ~= s/.so/.dylib/g

