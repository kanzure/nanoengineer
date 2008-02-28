TEMPLATE = lib

CONFIG += debug_and_release \
 stl \
 dll
win32 : CONFIG -= dll
win32 : CONFIG += staticlib

INCLUDEPATH += ../../../include

HEADERS += ../../../include/Nanorex/Utility/NXCommandLine.h \
../../../include/Nanorex/Utility/NXCommandResult.h \
../../../include/Nanorex/Utility/NXLogger.h \
../../../include/Nanorex/Utility/NXProperties.h \
../../../include/Nanorex/Utility/NXStringTokenizer.h \
../../../include/Nanorex/Utility/NXUtility.h \
 ../../../include/Nanorex/Utility/NXPoint.h \
 ../../../include/Nanorex/Utility/NXRGBColor.h

SOURCES += ../../../src/Utility/NXCommandLine.cpp \
../../../src/Utility/NXCommandResult.cpp \
../../../src/Utility/NXLogger.cpp \
../../../src/Utility/NXProperties.cpp \
../../../src/Utility/NXStringTokenizer.cpp \
../../../src/Utility/NXUtility.cpp

TARGET = NanorexUtility

DESTDIR = ../../../lib

QT -= gui
