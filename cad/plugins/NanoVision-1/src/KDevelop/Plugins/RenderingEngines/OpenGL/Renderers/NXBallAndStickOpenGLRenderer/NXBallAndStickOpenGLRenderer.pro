TEMPLATE = lib

CONFIG += stl \
opengl \
dll \
 debug_and_release \
 plugin \
 rtti
win32 : CONFIG -= dll
win32 : CONFIG += staticlib

QT += opengl

HEADERS += ../../../../../../../include/Nanorex/Interface/NXRendererPlugin.h \
 ../../../../../../../include/Nanorex/Interface/NXSceneGraph.h \
 ../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.h \
 ../../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLMaterial.h \
 ../../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRendererPlugin.h \
 ../../../../../../../include/Nanorex/Interface/NXAtomData.h \
 ../../../../../../../include/Nanorex/Interface/NXBondData.h

macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

DESTDIR = ../../../../../../../lib


# qmake puts these library declarations too early in the g++ command on win32
win32 : LIBS += -lopengl32 -lglu32 -lgdi32 -luser32 

SOURCES += ../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.cpp

TARGET = NXBallAndStickOpenGLRenderer

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline

# Remove the "lib" from the start of the library
# unix : QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs mv $(DESTDIR)$(TARGET)
# macx : QMAKE_POST_LINK ~= s/.so/.dylib/g



TARGETDEPS += ../../../../../../../lib/libNXOpenGLSceneGraph.a \
  ../../../../../../../lib/libGLT.a \
  ../../../../../../../lib/libNanorexInterface.so \
  ../../../../../../../lib/libNanorexUtility.so



INCLUDEPATH += $(OPENBABEL_INCPATH) \
  ../../../../../../../include

LIBS += -L../../../../../../../lib \
  -lNanorexInterface \
  -lNanorexUtility \
  -lNXOpenGLSceneGraph \
  -lGLT

