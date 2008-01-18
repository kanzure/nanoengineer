SOURCES += HDF5_SimResultsImportExport.cpp
HEADERS += HDF5_SimResultsImportExport.h
INCLUDEPATH += ../../../include \
/usr/local/include/openbabel-2.0
TEMPLATE = lib

CONFIG += dll

LIBS += -L../../../lib \
-lNanorexUtility \
-lNanorexInterface
TARGETDEPS += ../../../lib/libNanorexUtility.so \
../../../lib/libNanorexInterface.so
DESTDIR = ../../../lib

