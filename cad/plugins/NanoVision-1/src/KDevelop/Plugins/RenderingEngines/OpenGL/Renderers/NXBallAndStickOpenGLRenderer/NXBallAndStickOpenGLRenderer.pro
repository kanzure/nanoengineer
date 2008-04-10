TEMPLATE = lib
TARGET = NXBallAndStickOpenGLRenderer
DESTDIR = ../../../../../../../lib/

CONFIG += stl \
opengl \
dll \
plugin \
rtti \
debug_and_release \
build_all

CONFIG(debug,debug|release) {
	TARGET = $$join(TARGET,,,_d)
}


QT += opengl

HEADERS += ../../../../../../../include/Nanorex/Interface/NXRendererPlugin.h \
 ../../../../../../../include/Nanorex/Interface/NXSceneGraph.h \
 ../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.h \
 ../../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLMaterial.h \
 ../../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRendererPlugin.h \
 ../../../../../../../include/Nanorex/Interface/NXAtomData.h \
 ../../../../../../../include/Nanorex/Interface/NXBondData.h


SOURCES += ../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer.cpp

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline



TARGETDEPS += ../../../../../../../lib/libNXOpenGLSceneGraph.a \
  ../../../../../../../lib/libGLT.a \
  ../../../../../../../lib/libNanorexInterface.so \
  ../../../../../../../lib/libNanorexUtility.so


INCLUDEPATH += $(OPENBABEL_INCPATH) \
  ../../../../../../../include

unix {
# Remove the "lib" from the start of the library
	QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs cp $(DESTDIR)$(TARGET)
	QMAKE_CLEAN += $${DESTDIR}$${TARGET}.so $${DESTDIR}lib$${TARGET}.so
}

macx {
	TARGETDEPS ~= s/.so/.dylib/g
	QMAKE_POST_LINK ~= s/.so/.dylib/g
	QMAKE_CLEAN += $${DESTDIR}$${TARGET}.dylib
}

win32 {
	CONFIG -= dll
	CONFIG += staticlib
	TARGETDEPS ~= s/.so/.a/g
# qmake puts these library declarations too early in the g++ command on win32
	LIBS += -lopengl32 -lglu32 -lgdi32 -luser32 
}


PROJECTLIBS = -lNanorexUtility \
  -lNanorexInterface \
  -lNXOpenGLSceneGraph \
  -lGLT

CONFIG(debug,debug|release) {
	PROJECTLIBS ~= s/(.+)/\1_d/g
}

LIBS += -L../../../../../../../lib \
$$PROJECTLIBS


