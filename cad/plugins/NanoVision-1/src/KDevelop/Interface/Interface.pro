

HEADERS += \
../../../include/Nanorex/Interface/NXDataImportExportPlugin.h \
 ../../../include/Nanorex/Interface/NXDataStoreInfo.h \
 ../../../include/Nanorex/Interface/NXEntityManager.h \
 ../../../include/Nanorex/Interface/NXGraphicsManager.h \
 ../../../include/Nanorex/Interface/NXMoleculeData.h \
 ../../../include/Nanorex/Interface/NXMoleculeSet.h \
 ../../../include/Nanorex/Interface/NXNanoVisionResultCodes.h \
 ../../../include/Nanorex/Interface/NXNumbers.h \
 ../../../include/Nanorex/Interface/NXRendererPlugin.h \
 ../../../include/Nanorex/Interface/NXRenderingEngine.h \
 ../../../include/Nanorex/Interface/NXAtomData.h \
 ../../../include/Nanorex/Interface/NXSceneGraph.h \
 ../../../include/Nanorex/Interface/NXBondData.h \
 ../../../include/Nanorex/Interface/NXNamedView.h
INCLUDEPATH += ../../../include \
 $(OPENBABEL_INCPATH) \
 ../../../src \
 $(HDF5_SIMRESULTS_INCPATH)
# The "../../../src" and $HDF5... are temporary for NXEntityManager to access an
# HDF5_SimResultsImportExport plugin function directly.

SOURCES += ../../Interface/NXDataStoreInfo.cpp \
 ../../Interface/NXEntityManager.cpp \
 ../../Interface/NXGraphicsManager.cpp \
 ../../Interface/NXMoleculeData.cpp \
 ../../Interface/NXMoleculeSet.cpp \
 ../../Interface/NXNumbers.cpp \
 ../../Interface/NXNanoVisionResultCodes.cpp \
 ../../Interface/NXSceneGraph.cpp \
 ../../Interface/NXRenderingEngine.cpp \
 ../../Interface/NXAtomData.cpp

TEMPLATE = lib

CONFIG += stl \
 dll \
 debug_and_release \
 build_all

TARGET = NanorexInterface

CONFIG(debug,debug|release) {
	TARGET = $$join(TARGET,,,_d)
}

win32 : CONFIG -= dll
win32 : CONFIG += staticlib

DESTDIR = ../../../lib

TARGETDEPS += ../../../lib/libNanorexUtility.so
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

QT -= gui

LIBS += -L../../../lib \
  -lNanorexUtility_d \
  -L$(OPENBABEL_LIBPATH) \
  -lopenbabel

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
  -g \
  -O0 \
  -fno-inline

QMAKE_CXXFLAGS_RELEASE += -DNX_DEBUG

