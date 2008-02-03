SOURCES += nv1.cpp \
           main.cpp \
 ResultsWindow.cpp \
 MainWindowTabWidget.cpp \
 ViewParametersWindow.cpp \
 TrajectoryGraphicsPane.cpp \
 DataWindow.cpp \
 LogHandlerWidget.cpp \
 Interface/NXSceneGraph.cpp
HEADERS += nv1.h \
 ResultsWindow.h \
 MainWindowTabWidget.h \
 ViewParametersWindow.h \
 TrajectoryGraphicsPane.h \
 DataWindow.h \
 main.h \
 LogHandlerWidget.h
TEMPLATE = app
CONFIG += warn_on \
	  thread \
          qt \
 debug
TARGET = ../bin/nv1
RESOURCES = application.qrc
FORMS += ResultsWindow.ui \
 MainWindowTabWidget.ui \
 ViewParametersWindow.ui \
 TrajectoryGraphicsPane.ui \
 LogHandlerWidget.ui

INCLUDEPATH += ../include \
 $(OPENBABEL_INCPATH)

LIBS += -L../lib \
-lNanorexInterface \
-lNanorexUtility \
 -lopenbabel
TARGETDEPS += ../lib/libNanorexInterface.so \
../lib/libNanorexUtility.so
CONFIG -= release

