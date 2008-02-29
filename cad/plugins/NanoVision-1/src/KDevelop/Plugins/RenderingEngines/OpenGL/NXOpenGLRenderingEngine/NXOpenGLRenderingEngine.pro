TEMPLATE = lib

CONFIG += debug_and_release \
 staticlib \
 stl \
 opengl
# dll
# plugin

HEADERS += ../../../../../../include/Nanorex/Interface/NXAtomRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXBondRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXEntityManager.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRendererPlugin.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine.h \
 ../../../../../../include/Nanorex/Interface/NXRendererPlugin.h \
 ../../../../../../include/Nanorex/Interface/NXRenderingEngine.h \
 ../../../../../../include/Nanorex/Interface/NXRGBColor.h \
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
 $(OPENBABEL_INCPATH)

LIBS += -L$(OPENBABEL_LIBPATH) \
 -L../../../../../../lib \
 -lNXOpenGLSceneGraph \
 -lNanorexInterface \
 -lNanorexUtility \
 -lGLT \
 -lopenbabel
# qmake puts these library declarations too early in the g++ command on win32
win32 : LIBS += -lopengl32 -lglu32 -lgdi32 -luser32

TARGETDEPS += ../../../../../../lib/libNanorexUtility.so \
../../../../../../lib/libNanorexInterface.so \
../../../../../../lib/libNXOpenGLSceneGraph.a \
 ../../../../../../lib/libGLT.a 
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

TARGET = NXOpenGLRenderingEngine

DESTDIR = ../../../../../../lib

SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLCamera.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLCamera_sm.cpp \
 ../../../../../Plugins/RenderingEngines/OpenGL/trackball.c

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG

# Remove the "lib" from the start of the library
# unix : QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs mv $(DESTDIR)$(TARGET)
# macx : QMAKE_POST_LINK ~= s/.so/.dylib/g

