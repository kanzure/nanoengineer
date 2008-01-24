
LIBS += -lopenbabel \
 -L../../../lib \
 -lNanorexUtility

HEADERS += \
../../../include/Nanorex/Interface/NXNumbers.h \
 ../../../include/Nanorex/Interface/NXEntityManager.h \
 ../../../include/Nanorex/Interface/NXMoleculeSet.h \
 ../../../include/Nanorex/Interface/NXNanoVisionResultCodes.h \
 ../../../include/Nanorex/Interface/NXDataImportExportPlugin.h \
 ../../../include/Nanorex/Interface/NXMoleculeData.h \
 ../../include/Nanorex/Interface/NXDataStoreInfo.h

INCLUDEPATH += /usr/local/include/openbabel-2.0/ \
 ../../../include

SOURCES += ../../Interface/NXDataImportExportPlugin.cpp \
 ../../Interface/NXEntityManager.cpp \
 ../../Interface/NXMoleculeData.cpp \
 ../../Interface/NXMoleculeSet.cpp \
 ../../Interface/NXNumbers.cpp \
 ../../Interface/NXDataStoreInfo.cpp

TEMPLATE = lib

CONFIG += dll

TARGET = NanorexInterface

DESTDIR = ../../../lib

TARGETDEPS += ../../../lib/libNanorexUtility.so

