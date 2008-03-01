TEMPLATE = app

CONFIG -= release

CONFIG += debug \
stl \
opengl \
debug_and_release
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

LIBS += -lNXOpenGLRenderingEngine \
-lopenbabel \
 -lNXOpenGLRendererPlugin \
 -lNXBallAndStickOpenGLRenderer \
 -L../../../../../../../lib
DESTDIR = ../../../../../../../bin

