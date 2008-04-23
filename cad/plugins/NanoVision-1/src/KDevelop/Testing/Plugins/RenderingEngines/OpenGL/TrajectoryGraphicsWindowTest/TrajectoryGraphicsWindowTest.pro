TEMPLATE = app
TARGET = TrajectoryGraphicsWindowTest
DESTDIR = ../../../../../../../bin/


CONFIG += stl \
rtti \
opengl \
debug 

QT += opengl

HEADERS += ../../../../../../Testing/OpenGL/TrajectoryTestGraphicsManager.h \
../../../../../../TrajectoryGraphicsWindow.h \
../../../../../../DataWindow.h

SOURCES += ../../../../../../Testing/OpenGL/TrajectoryGraphicsWindowTest.cpp \
 ../../../../../../Testing/OpenGL/TrajectoryTestGraphicsManager.cpp \
 ../../../../../../TrajectoryGraphicsWindow.cpp \
 ../../../../../../DataWindow.cpp

TARGETDEPS += ../../../../../../../lib/libNXBallAndStickOpenGLRenderer_d.so \
  ../../../../../../../lib/libNXOpenGLRenderingEngine_d.so \
  ../../../../../../../lib/libNXOpenGLSceneGraph_d.a \
  ../../../../../../../lib/libGLT_d.a \
  ../../../../../../../lib/libNanorexInterface_d.so \
  ../../../../../../../lib/libNanorexUtility_d.so

INCLUDEPATH += ../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer \
  ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine \
  ../../../../../../../src/ \
  ../../../../../../../include/ \
  $(OPENBABEL_INCPATH)


FORMS += ../../../../../../TrajectoryGraphicsWindow.ui

LIBS += -L../../../../../../../lib \
  -lNanorexInterface_d \
  -lNanorexUtility_d \
  -lGLT_d \
  -lNXOpenGLSceneGraph_d \
  -lNXOpenGLRenderingEngine_d \
  -lNXBallAndStickOpenGLRenderer_d \
  -L$(OPENBABEL_LIBPATH) \
  -lopenbabel

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
  -g \
  -O0 \
  -fno-inline

# make 'clean' target
QMAKE_CLEAN += $${DESTDIR}$${TARGET}


