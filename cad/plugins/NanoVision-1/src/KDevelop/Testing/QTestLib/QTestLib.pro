TEMPLATE = app

CONFIG += debug_and_release \
qtestlib \
exceptions \
stl \
rtti \
opengl

SOURCES += ../../../Interface/NXGraphicsManagerTest.cpp

HEADERS += ../../../Interface/NXGraphicsManagerTest.h

INCLUDEPATH += $(OPENBABEL_INCPATH) \
  ../../../../include

QT += opengl

DESTDIR = ../../../../bin



TARGET = NXGraphicsManagerTest

LIBS += -L../../../../lib \
  -lNanorexInterface \
  -lNanorexUtility

