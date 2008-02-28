TEMPLATE = lib

CONFIG += dll \
 debug_and_release \
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
 ../../../../../../include/Nanorex/Interface/NXSceneGraph.h \
 ../../../../../../include/Nanorex/Interface/NXOpenGLMaterial.h

QT += opengl

INCLUDEPATH += ../../../../../../include \
 ../../../../../../src/Plugins/RenderingEngines/OpenGL/GLT \
 $(OPENBABEL_INCPATH)

LIBS += -lopenbabel \
 -L../../../../../../lib \
 -lGLT \
 -lNXOpenGLSceneGraph \
 -lNanorexInterface \
 -lNanorexUtility

TARGETDEPS += ../../../../../../lib/libNanorexUtility.so \
../../../../../../lib/libNanorexInterface.so \
../../../../../../lib/libNXOpenGLSceneGraph.a \
 ../../../../../../lib/libGLT.a
macx:TARGETDEPS ~= s/.so/.dylib/g

TARGET = NXOpenGLRenderingEngine

DESTDIR = ../../../../../../lib

SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine.cpp

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG

# Remove the "lib" from the start of the library
QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs mv $(DESTDIR)$(TARGET)
macx : QMAKE_POST_LINK ~= s/.so/.dylib/g

