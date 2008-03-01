TEMPLATE = app

CONFIG -= release

CONFIG += debug \
stl \
opengl \
 debug_and_release
QT += opengl

INCLUDEPATH += ../../../../../../../../include \
../../../../../../../../src/Plugins/RenderingEngines/OpenGL/GLT \
../../../../../../../../src/Plugins/RenderingEngines/OpenGL/Renderers
TARGETDEPS += ../../../../../../../../lib/libNXOpenGLRendererPlugin.a \
 ../../../../../../../../lib/libNXOpenGLSceneGraph.a \
 ../../../../../../../../lib/libGLT.a
SOURCES += ../../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRendererTest.cpp

HEADERS += ../../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRendererTest.h

LIBS += -L../../../../../../../../lib \
-lNXBallAndStickOpenGLRenderer \
-lNanorexInterface \
-lNanorexUtility \
-lGLT \
 -lNXOpenGLRendererPlugin \
 -lopenbabel
QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline


