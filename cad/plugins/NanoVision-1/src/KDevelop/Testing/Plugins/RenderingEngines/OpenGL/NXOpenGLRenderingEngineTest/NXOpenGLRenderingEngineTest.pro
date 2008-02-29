TEMPLATE = app

CONFIG -= release

CONFIG += debug \
stl \
opengl \
debug_and_release
QT += opengl

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
-g \
-fno-inline
INCLUDEPATH += ../../../../../../../include \
../../../../../../../src/Plugins/RenderingEngines/OpenGL/GLT \
 $(OPENBABEL_INCPATH) \
 ../../../../../../../src
SOURCES += ../../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLRenderingEngineTest.cpp

LIBS += -L../../../../../../../lib \
-lNXOpenGLRenderingEngine \
-lopenbabel \
 -lNXOpenGLRendererPlugin \
 -lNXBallAndStickOpenGLRenderer
DESTDIR = ../../../../../../../bin

