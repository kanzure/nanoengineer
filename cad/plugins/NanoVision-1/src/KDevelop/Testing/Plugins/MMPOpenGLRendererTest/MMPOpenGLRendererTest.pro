SOURCES += ../../../../Plugins/NanorexMMPImportExport/MMPOpenGLRendererTest.cpp

TEMPLATE = app

CONFIG -= release

CONFIG += debug \
stl \
rtti \
opengl
QT += opengl

DESTDIR = ../../../../../bin/

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
  -g \
  -O0 \
  -fno-inline

INCLUDEPATH += ../../../../../src/Plugins/RenderingEngines/OpenGL \
  ../../../../../src/Plugins/RenderingEngines/OpenGL/GLT \
  $(OPENBABEL_INCPATH) \
  ../../../../../src \
  ../../../../../include

LIBS += -L../../../../../lib \
  -lNXBallAndStickOpenGLRenderer \
  -lNXOpenGLRenderingEngine \
  -lNanorexMMPImportExport \
  -lNanorexInterface \
  -lNanorexUtility \
  -lopenbabel

TARGETDEPS += ../../../../../lib/libNXBallAndStickOpenGLRenderer.so

