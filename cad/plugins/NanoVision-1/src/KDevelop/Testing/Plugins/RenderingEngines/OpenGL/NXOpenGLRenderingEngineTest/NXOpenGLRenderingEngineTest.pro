TEMPLATE = app
TARGET = NXOpenGLRenderingEngineTest
DESTDIR = ../../../../../../../bin/

CONFIG += stl \
opengl \
 debug_and_release \
 rtti \
 build_all

QT += opengl

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
-g \
-O0 \
-fno-inline

INCLUDEPATH += ../../../../../../../include \
../../../../../../../src/Plugins/RenderingEngines/OpenGL/GLT \
 $(OPENBABEL_INCPATH) \
 ../../../../../../../src \
 ../../../../../../../src/Plugins/RenderingEngines/OpenGL

SOURCES += ../../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngineTest.cpp


TARGETDEPS += ../../../../../../../lib/libNXBallAndStickOpenGLRenderer.so \
  ../../../../../../../lib/libNXOpenGLRenderingEngine.so \
  ../../../../../../../lib/libNXOpenGLSceneGraph.a \
  ../../../../../../../lib/libGLT.a \
  ../../../../../../../lib/libNanorexInterface.so \
  ../../../../../../../lib/libNanorexUtility.so

macx: TARGETDEPS ~= s/.so/.dylib/g

PROJECTLIBS =  -lNXBallAndStickOpenGLRenderer \
  -lNXOpenGLRenderingEngine \
  -lNanorexInterface \
  -lNanorexUtility \
  -lNXOpenGLSceneGraph \
  -lGLT

CONFIG(debug,debug|release) {
	TARGET = $${TARGET}_d
	PROJECTLIBS ~= s/(.+)/\1_d/g
}

LIBS += -L../../../../../../../lib \
  $$PROJECTLIBS \
  -L$(OPENBABEL_INCPATH) \
  -lopenbabel

# make clean target
QMAKE_CLEAN += $${DESTDIR}$${TARGET}

