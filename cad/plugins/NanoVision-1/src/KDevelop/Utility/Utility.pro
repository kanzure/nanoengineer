TEMPLATE = lib

CONFIG += stl \
 dll \
 debug_and_release \
 build_all

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

CONFIG(debug,debug|release) {
	TARGET = $$join(TARGET,,,_d)
}

DESTDIR = ../../../lib

QT -= gui

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline


