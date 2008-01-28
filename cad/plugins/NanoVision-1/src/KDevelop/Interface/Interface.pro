
LIBS += -lopenbabel \
 -L../../../lib \
 -lNanorexUtility

HEADERS += \
NXDataImportExportPlugin.h \
 NXDataStoreInfo.h \
 NXEntityManager.h \
 NXMoleculeData.h \
 NXMoleculeSet.h \
 NXNanoVisionResultCodes.h \
 NXNumbers.h \
 NXAtomRenderData.h \
 NXBondRenderData.h

INCLUDEPATH += ../../../include \
 $(OPENBABEL_INCPATH)

SOURCES += NXDataImportExportPlugin.cpp \
 NXDataStoreInfo.cpp \
 NXEntityManager.cpp \
 NXMoleculeData.cpp \
 NXMoleculeSet.cpp \
 NXNumbers.cpp \
 NXAtomRenderData.cpp \
 NXBondRenderData.cpp

TEMPLATE = lib

CONFIG += dll \
 debug \
 stl

TARGET = NanorexInterface

DESTDIR = ../../../lib

TARGETDEPS += ../../../lib/libNanorexUtility.so

CONFIG -= release
QT -= gui

