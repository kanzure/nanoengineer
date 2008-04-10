TEMPLATE = app


CONFIG += stl \
opengl \
 debug_and_release

CONFIG(debug,debug|release) {
	TARGET = $$join(TARGET,,,_d)
}

QT += opengl



SOURCES += ../../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRendererTest.cpp

HEADERS += ../../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRendererTest.h

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline


DESTDIR = ../../../../../../../../bin

INCLUDEPATH += $(OPENBABEL_INCPATH) \
  ../../../../../../../../include \
  ../../../../../../../../src/Plugins/RenderingEngines/OpenGL/GLT \
  ../../../../../../../../src/Plugins/RenderingEngines/OpenGL/Renderers

TARGETDEPS += ../../../../../../../../lib/libNXBallAndStickOpenGLRenderer.so \
  ../../../../../../../../lib/libNXOpenGLSceneGraph.a \
  ../../../../../../../../lib/libGLT.a \
  ../../../../../../../../lib/libNanorexInterface.so \
  ../../../../../../../../lib/libNanorexUtility.so
LIBS += -L../../../../../../../../lib \
  -lNXBallAndStickOpenGLRenderer \
  -lNanorexInterface \
  -lNanorexUtility \
  -lNXOpenGLSceneGraph \
  -lGLT

