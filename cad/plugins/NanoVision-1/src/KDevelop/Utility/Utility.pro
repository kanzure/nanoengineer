TEMPLATE = lib

CONFIG += dll \
 debug \
 stl

INCLUDEPATH += ../../../include

HEADERS += NXCommandResult.h \
NXLogger.h \
NXPluginGroup.h \
NXPlugin.h \
NXProperties.h \
NXStringTokenizer.h \
NXUtility.h
SOURCES += NXCommandResult.cpp \
NXLogger.cpp \
NXPlugin.cpp \
NXPluginGroup.cpp \
NXProperties.cpp \
NXStringTokenizer.cpp \
NXUtility.cpp

TARGET = NanorexUtility

CONFIG -= release
DESTDIR = ../../../lib

QT -= gui
