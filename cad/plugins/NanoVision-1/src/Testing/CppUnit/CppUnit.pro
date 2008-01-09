SOURCES += CppUnit.cpp \
 ../../Interface/NXNumbers.cpp \
 ../../Interface/NXNumbersTest.cpp \
 ../../Interface/NXChemistryDataModel.cpp \
 ../../Interface/NXEntityManager.cpp \
 ../../Interface/NXEntityManagerTest.cpp

TEMPLATE = app

TARGET = CppUnit

LIBS += -lcppunit

DESTDIR = /home/bh/11Nano/SVN-D/cad/plugins/NanoVision-1/src/Testing/CppUnit

HEADERS += ../../Interface/NXNumbersTest.h \
../../../include/Nanorex/Interface/NXNumbers.h \
 ../../../include/Nanorex/Interface/NXChemistryDataModel.h \
 ../../../include/Nanorex/Interface/NXEntityManager.h
INCLUDEPATH += /home/bh/11Nano/SVN-D/cad/plugins/NanoVision-1/include

