TEMPLATE = app

CONFIG += stl \
opengl \
 debug_and_release \
 rtti
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


DESTDIR = ../../../../../../../bin

TARGETDEPS += ../../../../../../../lib/libNXBallAndStickOpenGLRenderer.so \
  ../../../../../../../lib/libNXOpenGLRenderingEngine.so \
  ../../../../../../../lib/libNXOpenGLSceneGraph.a \
  ../../../../../../../lib/libGLT.a \
  ../../../../../../../lib/libNanorexInterface.so \
  ../../../../../../../lib/libNanorexUtility.so




LIBS += -L../../../../../../../lib \
  -lNXBallAndStickOpenGLRenderer \
  -lNXOpenGLRenderingEngine \
  -lNanorexInterface \
  -lNanorexUtility \
  -lNXOpenGLSceneGraph \
  -lGLT \
  -lopenbabel

