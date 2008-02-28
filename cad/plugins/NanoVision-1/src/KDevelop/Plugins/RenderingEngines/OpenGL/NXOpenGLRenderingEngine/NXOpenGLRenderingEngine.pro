TEMPLATE = lib

CONFIG += dll \
 debug_and_release \
 stl \
 plugin
# opengl

HEADERS += ../../../../../../include/Nanorex/Interface/NXAtomRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXBondRenderData.h \
 ../../../../../../include/Nanorex/Interface/NXEntityManager.h \
 ../../../../../../include/Nanorex/Interface/NXOpenGLRendererPlugin.h \
 ../../../../../../include/Nanorex/Interface/NXOpenGLRenderingEngine.h \
 ../../../../../../include/Nanorex/Interface/NXRendererPlugin.h \
 ../../../../../../include/Nanorex/Interface/NXRenderingEngine.h \
 ../../../../../../include/Nanorex/Interface/NXRGBColor.h \
 ../../../../../../include/Nanorex/Interface/NXSceneGraph.h \
 ../../../../../../include/Nanorex/Interface/NXOpenGLMaterial.h

QT += opengl

INCLUDEPATH += ../../../../../../include \
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

CONFIG += opengl

TARGETDEPS += ../../../../../../lib/libNanorexUtility.so \
../../../../../../lib/libNanorexInterface.so \
../../../../../../lib/libNXOpenGLSceneGraph.a \
 ../../../../../../lib/libGLT.a
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

TARGET = NXOpenGLRenderingEngine

DESTDIR = ../../../../../../lib

SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine.cpp

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG

# Remove the "lib" from the start of the library
unix : QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs mv $(DESTDIR)$(TARGET)
macx : QMAKE_POST_LINK ~= s/.so/.dylib/g

