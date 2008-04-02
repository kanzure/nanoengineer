TEMPLATE = lib

CONFIG += stl \
 opengl \
 dll \
 debug_and_release \
 rtti \
 plugin

win32 : CONFIG -= dll
win32 : CONFIG += staticlib

HEADERS += ../../../../../../include/Nanorex/Interface/NXAtomData.h \
 ../../../../../../include/Nanorex/Interface/NXBondData.h \
 ../../../../../../include/Nanorex/Interface/NXEntityManager.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRendererPlugin.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine.h \
 ../../../../../../include/Nanorex/Interface/NXRendererPlugin.h \
 ../../../../../../include/Nanorex/Interface/NXRenderingEngine.h \
 ../../../../../../include/Nanorex/Interface/NXSceneGraph.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLSceneGraph.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLMaterial.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLCamera.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLCamera_sm.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/trackball.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/statemap.h

QT += opengl

INCLUDEPATH += ../../../../../../include \
 ../../../../../../src \
 ../../../../../../src/Plugins/RenderingEngines/OpenGL/GLT \
 $(OPENBABEL_INCPATH) \
 $(HDF5_SIMRESULTS_INCPATH) \
 ../../../../../../src/Plugins/RenderingEngines/OpenGL

# qmake puts these library declarations too early in the g++ command on win32
win32 : LIBS += -lopengl32 -lglu32 -lgdi32 -luser32

macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

TARGET = NXOpenGLRenderingEngine

DESTDIR = ../../../../../../lib

SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLCamera.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLCamera_sm.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/trackball.c

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline

# Remove the "lib" from the start of the library
# unix : QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs mv $(DESTDIR)$(TARGET)
# macx : QMAKE_POST_LINK ~= s/.so/.dylib/g


TARGETDEPS += ../../../../../../lib/libNXOpenGLSceneGraph.a \
  ../../../../../../lib/libGLT.a \
  ../../../../../../lib/libNanorexInterface.so \
  ../../../../../../lib/libNanorexUtility.so


LIBS += -L../../../../../../lib \
  -lNanorexUtility \
  -lNanorexInterface \
  ../../../../../../lib/libGLT.a \
  ../../../../../../lib/libNXOpenGLSceneGraph.a \
  -L$(OPENBABEL_LIBPATH) \
  -lopenbabel

