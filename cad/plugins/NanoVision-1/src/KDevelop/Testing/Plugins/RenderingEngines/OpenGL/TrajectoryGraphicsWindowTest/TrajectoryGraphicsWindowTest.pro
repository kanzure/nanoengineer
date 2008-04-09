SOURCES += ../../../../../../Testing/OpenGL/TrajectoryGraphicsWindowTest.cpp \
 ../../../../../../Testing/OpenGL/TrajectoryTestGraphicsManager.cpp \
 ../../../../../../TrajectoryGraphicsWindow.cpp \
 ../../../../../../DataWindow.cpp

TEMPLATE = app

CONFIG += debug_and_release \
stl \
rtti \
opengl
QT += opengl

DESTDIR = ../../../../../../../bin/

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
  -g \
  -O0 \
  -fno-inline



TARGETDEPS += ../../../../../../../lib/libNXBallAndStickOpenGLRenderer.so \
  ../../../../../../../lib/libNXOpenGLRenderingEngine.so \
  ../../../../../../../lib/libNXOpenGLSceneGraph.a \
  ../../../../../../../lib/libGLT.a \
  ../../../../../../../lib/libNanorexInterface.so \
  ../../../../../../../lib/libNanorexUtility.so

HEADERS += ../../../../../../Testing/OpenGL/TrajectoryTestGraphicsManager.h \
../../../../../../TrajectoryGraphicsWindow.h \
../../../../../../DataWindow.h
INCLUDEPATH += ../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer \
  ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine \
  ../../../../../../../src/ \
  ../../../../../../../include/ \
  $(OPENBABEL_INCPATH)

LIBS += -L../../../../../../../lib \
  -lNXBallAndStickOpenGLRenderer \
  -lNXOpenGLRenderingEngine \
  ../../../../../../../lib/libNXOpenGLSceneGraph.a \
  ../../../../../../../lib/libGLT.a \
  -lNanorexUtility \
  -lNanorexInterface \
  -L$(OPENBABEL_LIBPATH) \
  -lopenbabel

FORMS += ../../../../../../TrajectoryGraphicsWindow.ui

