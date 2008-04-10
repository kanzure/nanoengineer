TEMPLATE = app
TARGET = MMPOpenGLRendererTest
DESTDIR = ../../../../../bin/


CONFIG += debug_and_release \
stl \
rtti \
opengl \
build_all

QT += opengl

CONFIG(debug,debug|release) : TARGET = $${TARGET}_d

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
  -g \
  -O0 \
  -fno-inline

INCLUDEPATH += ../../../../../src/Plugins/RenderingEngines/OpenGL \
  ../../../../../src/Plugins/RenderingEngines/OpenGL/GLT \
  $(OPENBABEL_INCPATH) \
  ../../../../../src \
  ../../../../../include

SOURCES += ../../../../Plugins/NanorexMMPImportExport/MMPOpenGLRendererTest.cpp

PROJECTLIBS = -lNanorexUtility \
  -lNanorexInterface \
  -lNanorexMMPImportExport \
  -lNXOpenGLRenderingEngine \
  -lNXBallAndStickOpenGLRenderer

CONFIG(debug,debug|release) : PROJECTLIBS ~= s/(.+)/\1_d/g

LIBS += -L../../../../../lib \
  $$PROJECTLIBS \
  -L$(OPENBABEL_LIBPATH) \
  -lopenbabel

TARGETDEPS += ../../../../../lib/libNXBallAndStickOpenGLRenderer.so \
  ../../../../../lib/libNXOpenGLRenderingEngine.so \
  ../../../../../lib/libNXOpenGLSceneGraph.a \
  ../../../../../lib/libGLT.a \
  ../../../../../lib/libNanorexMMPImportExport.so \
  ../../../../../lib/libNanorexInterface.so \
  ../../../../../lib/libNanorexUtility.so

macx: TARGETDEPS ~= s/.so/.dylib/g
win32: TARGETDEPS ~= s/.so/.dll/g

# make clean targets
QMAKE_CLEAN += $${DESTDIR}$${TARGET}
