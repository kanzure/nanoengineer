TEMPLATE = app

CONFIG -= release

CONFIG += debug_and_release \
stl \
opengl \
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

LIBS += -lopenbabel \
 -L../../../../../../../lib

DESTDIR = ../../../../../../../bin

TARGETDEPS += ../../../../../../../lib/libNXBallAndStickOpenGLRenderer.so \
../../../../../../../lib/libNXOpenGLRendererPlugin.so \
../../../../../../../lib/libNXOpenGLRenderingEngine.so \
../../../../../../../lib/libNXOpenGLSceneGraph.a \
../../../../../../../lib/libGLT.a \
../../../../../../../lib/libNanorexInterface.so \
../../../../../../../lib/libNanorexUtility.so
