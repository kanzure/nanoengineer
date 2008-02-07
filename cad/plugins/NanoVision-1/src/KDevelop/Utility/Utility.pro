TEMPLATE = lib

CONFIG += dll \
 debug \
 stl

INCLUDEPATH += ../../../include

HEADERS += ../../../include/Nanorex/Utility/NXCommandLine.h \
../../../include/Nanorex/Utility/NXCommandResult.h \
../../../include/Nanorex/Utility/NXLogger.h \
../../../include/Nanorex/Utility/NXPluginGroup.h \
../../../include/Nanorex/Utility/NXPlugin.h \
../../../include/Nanorex/Utility/NXProperties.h \
../../../include/Nanorex/Utility/NXStringTokenizer.h \
../../../include/Nanorex/Utility/NXUtility.h \
 ../../../include/Nanorex/Utility/NXPoint.h \
 ../../../include/Nanorex/Utility/NXRGBColor.h

SOURCES += ../../../src/Utility/NXCommandLine.cpp \
../../../src/Utility/NXCommandResult.cpp \
../../../src/Utility/NXLogger.cpp \
../../../src/Utility/NXPlugin.cpp \
../../../src/Utility/NXPluginGroup.cpp \
../../../src/Utility/NXProperties.cpp \
../../../src/Utility/NXStringTokenizer.cpp \
../../../src/Utility/NXUtility.cpp

TARGET = NanorexUtility

CONFIG -= release
DESTDIR = ../../../lib

QT -= gui
