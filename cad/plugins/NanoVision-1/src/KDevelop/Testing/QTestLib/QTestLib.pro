TEMPLATE = app
TARGET = NXGraphicsManagerTest
DESTDIR = ../../../../bin/

CONFIG += debug_and_release \
qtestlib \
exceptions \
stl \
rtti \
opengl \
build_all

QT += opengl

PROJECTLIBS = -lNanorexInterface -lNanorexUtility

CONFIG(debug,debug|release) {
	TARGET = $${TARGET}_d
	PROJECTLIBS ~= s/(.+)/\1_d/g
}

SOURCES += ../../../Interface/NXGraphicsManagerTest.cpp

HEADERS += ../../../Interface/NXGraphicsManagerTest.h

INCLUDEPATH += $(OPENBABEL_INCPATH) \
  ../../../../include

LIBS += -L../../../../lib \
  $$PROJECTLIBS

# make clean targets
QMAKE_CLEAN += $${DESTDIR}$${TARGET}
