SOURCES += nv1.cpp \
           main.cpp \
 ResultsWindow.cpp
HEADERS += nv1.h \
 ResultsWindow.h
TEMPLATE = app
CONFIG += warn_on \
	  thread \
          qt
TARGET = ../bin/nv1
RESOURCES = application.qrc
FORMS += ResultsWindow.ui

