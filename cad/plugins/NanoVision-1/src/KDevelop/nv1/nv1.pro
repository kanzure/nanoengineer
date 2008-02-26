TEMPLATE = app

CONFIG -= release

CONFIG += debug \
stl \
opengl \
 debug_and_release

QT += opengl

LIBS += -lopenbabel \
-lNanorexInterface \
-lNanorexUtility \
 -L../../../lib/ \
 -L../../../lib \
 -L/home/rmanoj/Nanorex/SVN/trunk/cad/plugins/NanoVision-1/lib

macx : TARGETDEPS ~= s/.so/.dylib/g

SOURCES += ../../DataWindow.cpp \
../../LogHandlerWidget.cpp \
../../main.cpp \
../../MainWindowTabWidget.cpp \
../../nv1.cpp \
../../ResultsWindow.cpp \
../../InputParametersWindow.cpp \
../../ErrorDialog.cpp \
../../JobManagement/GROMACS_JobMonitor.cpp \
../../JobManagement/JobMonitor.cpp \
 ../../TrajectoryGraphicsWindow.cpp

HEADERS += ../../DataWindow.h \
../../LogHandlerWidget.h \
../../main.h \
../../MainWindowTabWidget.h \
../../nv1.h \
../../ResultsWindow.h \
../../InputParametersWindow.h \
../../ErrorDialog.h \
../../JobManagement/GROMACS_JobMonitor.h \
../../JobManagement/JobMonitor.h \
 ../../TrajectoryGraphicsWindow.h

FORMS += ../../LogHandlerWidget.ui \
../../MainWindowTabWidget.ui \
../../ResultsWindow.ui \
../../InputParametersWindow.ui \
../../ErrorDialog.ui \
 ../../TrajectoryGraphicsWindow.ui

RESOURCES += ../../application.qrc

INCLUDEPATH += ../../../include \
 $(OPENBABEL_INCPATH)

TARGET = nv1

DESTDIR = ../../../bin

# This tells qmake to not create a Mac bundle for this application.
CONFIG -= app_bundle

