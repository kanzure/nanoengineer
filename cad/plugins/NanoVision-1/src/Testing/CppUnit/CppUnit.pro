SOURCES += CppUnit.cpp \
 ../../Interface/NXNumbers.cpp \
 ../../Interface/NXNumbersTest.cpp

TEMPLATE = app

TARGET = CppUnit

LIBS += -lcppunit

DESTDIR = /home/bh/11Nano/SVN-D/cad/plugins/NanoVision-1/src/Testing/CppUnit

HEADERS += ../../Interface/NXNumbersTest.h \
../../../include/Nanorex/Interface/NXNumbers.h
INCLUDEPATH += /home/bh/11Nano/SVN-D/cad/plugins/NanoVision-1/include

