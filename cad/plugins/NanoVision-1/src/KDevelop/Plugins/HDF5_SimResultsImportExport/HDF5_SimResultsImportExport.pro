SOURCES += ../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExport.cpp
HEADERS += ../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExport.h
INCLUDEPATH += ../../../../include \
 $(OPENBABEL_INCPATH)
TEMPLATE = lib

CONFIG += dll \
 debug

LIBS += -L../../../../lib \
-lNanorexUtility \
-lNanorexInterface \
 -lHDF5_SimResults
TARGETDEPS += ../../../../lib/libNanorexUtility.so \
../../../../lib/libNanorexInterface.so
DESTDIR = ../../../../lib

CONFIG -= release

