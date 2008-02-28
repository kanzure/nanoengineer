TEMPLATE = app

CONFIG -= release

CONFIG += debug \
stl \
opengl \
 debug_and_release

QT += opengl

LIBS +=  -L../../../lib/ \
-L$(OPENBABEL_LIBPATH) \
-lNanorexInterface \
-lNanorexUtility \
-lopenbabel

SOURCES += ../../DataWindow.cpp \
../../LogHandlerWidget.cpp \
../../main.cpp \
../../MainWindowTabWidget.cpp \
../../nv1.cpp \
../../ResultsWindow.cpp \
../../InputParametersWindow.cpp \
../../ResultsSummaryWindow.cpp \
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
../../ResultsSummaryWindow.h \
../../ErrorDialog.h \
../../JobManagement/GROMACS_JobMonitor.h \
../../JobManagement/JobMonitor.h \
 ../../TrajectoryGraphicsWindow.h

FORMS += ../../LogHandlerWidget.ui \
../../MainWindowTabWidget.ui \
../../ResultsWindow.ui \
../../InputParametersWindow.ui \
../../ResultsSummaryWindow.ui \
../../ErrorDialog.ui \
 ../../TrajectoryGraphicsWindow.ui

RESOURCES += ../../application.qrc

INCLUDEPATH += ../../../include \
 $(OPENBABEL_INCPATH)

TARGET = nv1

DESTDIR = ../../../bin

# This tells qmake to not create a Mac bundle for this application.
CONFIG -= app_bundle

#macx : TARGETDEPS ~= s/.so/.dylib/g

