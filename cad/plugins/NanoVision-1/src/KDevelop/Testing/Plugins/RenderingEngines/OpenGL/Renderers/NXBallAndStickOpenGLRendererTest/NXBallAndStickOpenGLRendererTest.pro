TEMPLATE = app


CONFIG += stl \
opengl \
 debug_and_release

QT += opengl

INCLUDEPATH += ../../../../../../../../include \
../../../../../../../../src/Plugins/RenderingEngines/OpenGL/GLT \
../../../../../../../../src/Plugins/RenderingEngines/OpenGL/Renderers

LIBS += -L../../../../../../../../lib \
 -lNXOpenGLSceneGraph \
 -lGLT \
 -lNXOpenGLRendererPlugin \
 -lNXBallAndStickOpenGLRenderer \
 -lNanorexInterface \
 -lNanorexUtility

TARGETDEPS += ../../../../../../../../lib/libNXOpenGLSceneGraph.a \
 ../../../../../../../../lib/libGLT.a \
 ../../../../../../../../lib/libNXOpenGLRendererPlugin.so \
 ../../../../../../../../lib/libNXBallAndStickOpenGLRenderer.so \
 ../../../../../../../../lib/libNanorexInterface.so \
 ../../../../../../../../lib/libNanorexUtility.so
SOURCES += ../../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRendererTest.cpp

HEADERS += ../../../../../../../Plugins/RenderingEngines/OpenGL/Renderers/NXBallAndStickOpenGLRendererTest.h

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline


DESTDIR = ../../../../../../../../bin

