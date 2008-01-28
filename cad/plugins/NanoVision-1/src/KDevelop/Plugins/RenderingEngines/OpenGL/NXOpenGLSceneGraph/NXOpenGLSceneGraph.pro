HEADERS += NXOpenGLMaterial.h \
NXSceneGraph.h \
NXOpenGLSceneGraph.h
TEMPLATE = lib

CONFIG += staticlib \
debug \
opengl
CONFIG -= release

QT -= gui

TARGET = NXOpenGLSceneGraph

INCLUDEPATH += ../../../../../../include

LIBS += NXUtility
TARGETDEPS += ../../../../../../lib/libNanorexUtility.so

SOURCES += NXOpenGLSceneGraph.cpp

DESTDIR = ../../../../../../lib

