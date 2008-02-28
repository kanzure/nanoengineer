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
-lNanorexInterface \
-lNanorexUtility \
-lopenbabel \
-lHDF5_SimResults \
-lhdf5

TARGETDEPS += ../../../../lib/libNanorexUtility.so \
../../../../lib/libNanorexInterface.so
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

DESTDIR = ../../../../lib

# Remove the "lib" from the start of the library
unix : QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs mv $(DESTDIR)$(TARGET)
macx : QMAKE_POST_LINK ~= s/.so/.dylib/g

