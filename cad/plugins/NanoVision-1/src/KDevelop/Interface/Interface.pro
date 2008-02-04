
LIBS += -lopenbabel \
 -L../../../lib \
 -lNanorexUtility

HEADERS += \
../../../include/Nanorex/Interface/NXDataImportExportPlugin.h \
 ../../../include/Nanorex/Interface/NXDataStoreInfo.h \
 ../../../include/Nanorex/Interface/NXEntityManager.h \
 ../../../include/Nanorex/Interface/NXMoleculeData.h \
 ../../../include/Nanorex/Interface/NXMoleculeSet.h \
 ../../../include/Nanorex/Interface/NXNanoVisionResultCodes.h \
 ../../../include/Nanorex/Interface/NXNumbers.h \
 ../../../include/Nanorex/Interface/NXAtomRenderData.h \
 ../../../include/Nanorex/Interface/NXBondRenderData.h \
 ../../../include/Nanorex/Interface/NXSceneGraph.h \
 ../../../include/Nanorex/Interface/NXTrackball.h \
 ../../../include/Nanorex/Interface/NXRendererPlugin.h \
 ../../../include/Nanorex/Interface/NXRenderingEngine.h

INCLUDEPATH += ../../../include \
 $(OPENBABEL_INCPATH)

SOURCES += ../../Interface/NXDataImportExportPlugin.cpp \
 ../../Interface/NXDataStoreInfo.cpp \
 ../../Interface/NXEntityManager.cpp \
 ../../Interface/NXMoleculeData.cpp \
 ../../Interface/NXMoleculeSet.cpp \
 ../../Interface/NXNumbers.cpp \
 ../../Interface/NXAtomRenderData.cpp \
 ../../Interface/NXBondRenderData.cpp \
 ../../Interface/NXNanoVisionResultCodes.cpp \
 ../../Interface/NXSceneGraph.cpp

TEMPLATE = lib

CONFIG += dll \
 debug \
 stl

TARGET = NanorexInterface

DESTDIR = ../../../lib

TARGETDEPS += ../../../lib/libNanorexUtility.so
macx : TARGETDEPS ~= s/.so/.dylib/g

CONFIG -= release
QT -= gui

