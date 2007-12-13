SOURCES += nv1.cpp \
           main.cpp \
 ResultsWindow.cpp \
 MainWindowTabWidget.cpp \
 ViewParametersWindow.cpp \
 TrajectoryGraphicsPane.cpp
HEADERS += nv1.h \
 ResultsWindow.h \
 MainWindowTabWidget.h \
 ViewParametersWindow.h \
 TrajectoryGraphicsPane.h
TEMPLATE = app
CONFIG += warn_on \
	  thread \
          qt
TARGET = ../bin/nv1
RESOURCES = application.qrc
FORMS += ResultsWindow.ui \
 MainWindowTabWidget.ui \
 ViewParametersWindow.ui \
 TrajectoryGraphicsPane.ui

