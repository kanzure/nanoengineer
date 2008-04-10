TEMPLATE = app
TARGET = TrajectoryGraphicsWindowTest
DESTDIR = ../../../../../../../bin/


CONFIG += stl \
rtti \
opengl \
debug_and_release \
build_all

CONFIG(debug,debug|release) : TARGET = $${TARGET}_d

QT += opengl

HEADERS += ../../../../../../Testing/OpenGL/TrajectoryTestGraphicsManager.h \
../../../../../../TrajectoryGraphicsWindow.h \
../../../../../../DataWindow.h

SOURCES += ../../../../../../Testing/OpenGL/TrajectoryGraphicsWindowTest.cpp \
 ../../../../../../Testing/OpenGL/TrajectoryTestGraphicsManager.cpp \
 ../../../../../../TrajectoryGraphicsWindow.cpp \
 ../../../../../../DataWindow.cpp

TARGETDEPS += ../../../../../../../lib/libNXBallAndStickOpenGLRenderer.so \
  ../../../../../../../lib/libNXOpenGLRenderingEngine.so \
  ../../../../../../../lib/libNXOpenGLSceneGraph.a \
  ../../../../../../../lib/libGLT.a \
  ../../../../../../../lib/libNanorexInterface.so \
  ../../../../../../../lib/libNanorexUtility.so

INCLUDEPATH += ../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRenderer \
  ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngine \
  ../../../../../../../src/ \
  ../../../../../../../include/ \
  $(OPENBABEL_INCPATH)


FORMS += ../../../../../../TrajectoryGraphicsWindow.ui

PROJECTLIBS = -lNanorexInterface \
-lNanorexUtility \
-lGLT \
-lNXOpenGLSceneGraph \
-lNXOpenGLRenderingEngine \
-lNXBallAndStickOpenGLRenderer

CONFIG(debug,debug|release): PROJECTLIBS ~= s/(.+)/\1_d/g

LIBS += -L../../../../../../../lib \
   $$PROJECTLIBS \
  -L$(OPENBABEL_LIBPATH) \
  -lopenbabel

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
  -g \
  -O0 \
  -fno-inline

# make 'clean' target
QMAKE_CLEAN += $${DESTDIR}$${TARGET}


