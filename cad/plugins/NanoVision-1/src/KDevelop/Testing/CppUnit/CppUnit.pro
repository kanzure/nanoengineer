TEMPLATE = app
TARGET = CppUnit
DESTDIR = ../../../../bin/

CONFIG += stl \
 debug

CONFIG(debug,debug|release){
    TARGET = $$join(TARGET,,,_d)
}

QT += gui

SOURCES += ../../../Testing/CppUnit/CppUnit.cpp \
 ../../../Interface/NXEntityManagerTest.cpp \
 ../../../Interface/NXNumbersTest.cpp \
 ../../../Utility/NXCommandResultTest.cpp \
 ../../../Utility/NXLoggerTest.cpp \
 ../../../Utility/NXStringTokenizerTest.cpp \
 ../../../Utility/NXUtilityTest.cpp \
 ../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExportTest.cpp \
 ../../../Plugins/OpenBabelImportExport/OpenBabelImportExportTest.cpp \
 ../../../Interface/NXSceneGraphTest.cpp \
 ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExportTest.cpp \
 ../../../Utility/NXVectorTest.cpp
# ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExportRagelTest.cpp


INCLUDEPATH += ../../../../include \
 $(OPENBABEL_INCPATH) \
 $(HDF5_SIMRESULTS_INCPATH) \
 ../../../../src
# The "../../../src" is temporary for NXEntityManager to access an
# HDF5_SimResultsImportExport plugin function directly.


HEADERS += ../../../Utility/NXCommandResultTest.h \
../../../Utility/NXLoggerTest.h \
../../../Utility/NXStringTokenizerTest.h \
../../../Utility/NXUtilityTest.h \
../../../Interface/NXEntityManagerTest.h \
../../../Interface/NXNumbersTest.h \
../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExportTest.h \
 ../../../Plugins/OpenBabelImportExport/OpenBabelImportExportTest.h \
 ../../../Interface/NXSceneGraphTest.h \
 ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExportTest.h \
 ../../../Utility/NXVectorTest.h
# ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExportRagelTest.h

# This tell qmake to not create a Mac bundle for this application.
CONFIG -= app_bundle 

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline

QMAKE_CXXFLAGS_RELEASE += -DNX_DEBUG

TARGETDEPS += ../../../../lib/libNanorexInterface.so \
  ../../../../lib/libNanorexUtility.so
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g


DISTFILES += ../../../Plugins/NanorexMMPImportExport/molecule.rl \
 ../../../Plugins/NanorexMMPImportExport/atom.rl \
 ../../../Plugins/NanorexMMPImportExport/utilities.rl \
 ../../../Plugins/NanorexMMPImportExport/group.rl \
 ../../../Plugins/NanorexMMPImportExport/NanorexMMPImportExportRagelTest.rl

PROJECTLIBS = -lNanorexMMPImportExport \
  -lNanorexUtility \
  -lNanorexInterface

CONFIG(debug,debug|release) {
	 PROJECTLIBS ~= s/(.+)/\1_d/g
}

LIBS += -L../../../../lib \
  $$PROJECTLIBS \
  -L$(OPENBABEL_LIBPATH) \
  -L$(HDF5_SIMRESULTS_INCPATH) \
  -lcppunit \
  -lopenbabel

# make clean target
QMAKE_CLEAN += $${DESTDIR}$${TARGET}
