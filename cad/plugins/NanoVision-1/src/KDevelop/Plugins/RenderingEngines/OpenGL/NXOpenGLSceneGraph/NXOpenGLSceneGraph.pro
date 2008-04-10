TEMPLATE = lib
TARGET = NXOpenGLSceneGraph
DESTDIR = ../../../../../../lib/

CONFIG += staticlib \
opengl \
 rtti \
 debug_and_release \
 stl \
 build_all

CONFIG(debug,debug|release) {
	TARGET = $$join(TARGET,,,_d)
}

QT += opengl
QT -= gui

TARGETDEPS += ../../../../../../lib/libNanorexUtility.so

macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

INCLUDEPATH += ../../../../../../include

HEADERS += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLMaterial.h \
 ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLSceneGraph.h \
 ../../../../../../include/Nanorex/Interface/NXSceneGraph.h


SOURCES += ../../../../../Plugins/RenderingEngines/OpenGL/NXOpenGLSceneGraph.cpp

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline

# make clean targets
unix : QMAKE_CLEAN += $${DESTDIR}lib$${TARGET}.a
macx : QMAKE_CLEAN += $${DESTDIR}lib$${TARGET}.a
win32: QMAKE_CLEAN += $${DESTDIR}$${TARGET}.a


