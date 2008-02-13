SOURCES += ../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExport.cpp

HEADERS += ../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExport.h

INCLUDEPATH += ../../../../include \
 $(OPENBABEL_INCPATH) \
 $(HDF5_SIMRESULTS_INCPATH)

TEMPLATE = lib

CONFIG += dll \
 debug_and_release \
 plugin

LIBS += -L../../../../lib \
-L$(OPENBABEL_LIBPATH) \
-L$(HDF5_SIMRESULTS_LIBPATH) \
-lNanorexUtility \
-lNanorexInterface \
-lopenbabel \
-lHDF5_SimResults \
-lhdf5

TARGETDEPS += ../../../../lib/libNanorexUtility.so \
../../../../lib/libNanorexInterface.so
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

DESTDIR = ../../../../lib
