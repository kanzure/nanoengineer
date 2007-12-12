SOURCES += nv1.cpp \
           main.cpp \
 ResultsWindow.cpp \
 MainWindowTabWidget.cpp
HEADERS += nv1.h \
 ResultsWindow.h \
 MainWindowTabWidget.h
TEMPLATE = app
CONFIG += warn_on \
	  thread \
          qt
TARGET = ../bin/nv1
RESOURCES = application.qrc
FORMS += ResultsWindow.ui \
 MainWindowTabWidget.ui

