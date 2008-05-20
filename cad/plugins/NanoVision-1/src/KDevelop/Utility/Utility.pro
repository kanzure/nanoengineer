
TEMPLATE = lib

CONFIG += \
 dll \
 release \
 stl

win32 : CONFIG -= dll
win32 : CONFIG += staticlib

INCLUDEPATH += ../../../include

HEADERS += ../../../include/Nanorex/Utility/NXCommandLine.h \
../../../include/Nanorex/Utility/NXCommandResult.h \
../../../include/Nanorex/Utility/NXLogger.h \
../../../include/Nanorex/Utility/NXProperties.h \
../../../include/Nanorex/Utility/NXStringTokenizer.h \
../../../include/Nanorex/Utility/NXUtility.h \
 ../../../include/Nanorex/Utility/NXRGBColor.h \
 ../../../include/Nanorex/Utility/NXVector.h \
 ../../../include/Nanorex/Utility/NXQuaternion.h \
 ../../../include/Nanorex/Utility/NXTrackball.h \
 ../../../include/Nanorex/Utility/NXMatrix.h

SOURCES += ../../../src/Utility/NXCommandLine.cpp \
../../../src/Utility/NXCommandResult.cpp \
../../../src/Utility/NXLogger.cpp \
../../../src/Utility/NXProperties.cpp \
../../../src/Utility/NXStringTokenizer.cpp \
../../../src/Utility/NXUtility.cpp

TARGET = NanorexUtility

# This puts a "_d" after debug targets
#CONFIG(debug,debug|release){
#    TARGET = $$join(TARGET,,,_d)
#}

DESTDIR = ../../../lib

QT -= gui

#QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
# -g \
# -O0 \
# -fno-inline

QMAKE_CXXFLAGS_RELEASE += -DNDEBUG -O2

