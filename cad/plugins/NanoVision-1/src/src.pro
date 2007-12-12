SOURCES += nv1.cpp \
           main.cpp \
 MdiWindow.cpp
HEADERS += nv1.h \
 MdiWindow.h
TEMPLATE = app
CONFIG += warn_on \
	  thread \
          qt
TARGET = ../bin/nv1
RESOURCES = application.qrc
