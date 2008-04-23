TEMPLATE = app
TARGET = MMPOpenGLRendererTest
DESTDIR = ../../../../../bin/


CONFIG += debug \
stl \
rtti \
opengl 

QT += opengl


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

PROJECTLIBS = -lNanorexUtility_d \
  -lNanorexInterface_d \
  -lNanorexMMPImportExport_d \
  -lNXOpenGLRenderingEngine_d \
  -lNXBallAndStickOpenGLRenderer_d


LIBS += -L../../../../../lib \
  $$PROJECTLIBS \
  -L$(OPENBABEL_LIBPATH) \
  -lopenbabel

TARGETDEPS += ../../../../../lib/libNXBallAndStickOpenGLRenderer_d.so \
  ../../../../../lib/libNXOpenGLRenderingEngine_d.so \
  ../../../../../lib/libNXOpenGLSceneGraph_d.a \
  ../../../../../lib/libGLT_d.a \
  ../../../../../lib/libNanorexMMPImportExport_d.so \
  ../../../../../lib/libNanorexInterface_d.so \
  ../../../../../lib/libNanorexUtility_d.so

macx: TARGETDEPS ~= s/.so/.dylib/g
win32: TARGETDEPS ~= s/.so/.dll/g

# make clean targets
QMAKE_CLEAN += $${DESTDIR}$${TARGET}

