SOURCES += ../../../Testing/CppUnit/CppUnit.cpp \
 ../../../Interface/NXEntityManagerTest.cpp \
 ../../../Interface/NXNumbersTest.cpp \
 ../../../Utility/NXCommandResultTest.cpp \
 ../../../Utility/NXLoggerTest.cpp \
 ../../../Utility/NXStringTokenizerTest.cpp \
 ../../../Utility/NXUtilityTest.cpp \
 ../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExportTest.cpp \
 ../../../Plugins/OpenBabelImportExport/OpenBabelImportExportTest.cpp \
 ../../../Utility/NXPointTest.cpp \
 ../../../Interface/NXSceneGraphTest.cpp

TEMPLATE = app

TARGET = CppUnit

LIBS += -L../../../../lib \
 -L$(OPENBABEL_LIBPATH) \
 -L$(HDF5_SIMRESULTS_INCPATH) \
 -lNanorexInterface \
 -lNanorexUtility \
 -lcppunit \
 -lopenbabel

INCLUDEPATH += ../../../../include \
 $(OPENBABEL_INCPATH) \
 $(HDF5_SIMRESULTS_INCPATH)

HEADERS += ../../../Utility/NXCommandResultTest.h \
../../../Utility/NXLoggerTest.h \
../../../Utility/NXStringTokenizerTest.h \
../../../Utility/NXUtilityTest.h \
../../../Interface/NXEntityManagerTest.h \
../../../Interface/NXNumbersTest.h \
../../../Plugins/HDF5_SimResultsImportExport/HDF5_SimResultsImportExportTest.h \
 ../../../Plugins/OpenBabelImportExport/OpenBabelImportExportTest.h \
 ../../../Utility/NXPointTest.h \
 ../../../Interface/NXSceneGraphTest.h

TARGETDEPS += ../../../../lib/libNanorexUtility.so \
../../../../lib/libNanorexInterface.so
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

DESTDIR = ../../../../bin

CONFIG -= release

CONFIG += debug \
stl

# This tell qmake to not create a Mac bundle for this application.
CONFIG -= app_bundle

QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
 -g \
 -O0 \
 -fno-inline

