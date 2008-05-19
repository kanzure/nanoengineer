
SOURCES += ../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExport.cpp

HEADERS += ../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExport.h

DESTDIR = ../../../../lib

INCLUDEPATH += ../../../../include \
 $(OPENBABEL_INCPATH) \
 $(HDF5_SIMRESULTS_INCPATH)

TEMPLATE = lib

CONFIG += dll \
 plugin \
 release \
 stl

TARGET = HDF5_SimResultsImportExport

TARGETDEPS += ../../../../lib/libNanorexInterface.so \
  ../../../../lib/libNanorexUtility.so

#CONFIG(debug,debug|release) {
#	TARGET = $$join(TARGET,,,_d)
#	PROJECTLIBS ~= s/(.+)/\1_d/g
#	TARGETDEPS ~= s/(.+).so/\1_d.so/g
#}

unix {
	QMAKE_CLEAN += $${DESTDIR}$${TARGET}.so

	# Remove the "lib" from the start of the library
	QMAKE_POST_LINK = echo $(DESTDIR)$(TARGET) | sed -e \'s/\\(.*\\)lib\\(.*\\)\\(\\.so\\)/\1\2\3/\' | xargs mv $(DESTDIR)$(TARGET)
}

macx {
	QMAKE_CLEAN += $${DESTDIR}$${TARGET}.dylib
	TARGETDEPS ~= s/.so/.dylib/g
    QMAKE_POST_LINK ~= s/.so/.dylib/g
}

win32 {
	QMAKE_CLEAN += $${DESTDIR}$${TARGET}.dll
	TARGETDEPS ~= s/.so/.a/g
}

QMAKE_CXXFLAGS_RELEASE += -DNDEBUG -O2

LIBS += -L../../../../lib \
  -lNanorexInterface \
  -lNanorexUtility \
  -L$(OPENBABEL_LIBPATH) \
  -lopenbabel \
  -L$(HDF5_SIMRESULTS_LIBPATH) \
  -lHDF5_SimResults \
  -lhdf5

