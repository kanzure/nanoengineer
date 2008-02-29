TEMPLATE = app

CONFIG += debug_and_release \
stl \
opengl

QT += opengl

LIBS +=  -L$(OPENBABEL_LIBPATH) \
 -L../../../lib \
 -lNXOpenGLRenderingEngine \
 -lNXOpenGLSceneGraph \
 -lGLT \
 -lNanorexInterface \
 -lNanorexUtility \
 -lopenbabel
# qmake puts these library declarations too early in the g++ command on win32
win32 : LIBS += -lopengl32 -lglu32 -lgdi32 -luser32

SOURCES += ../../DataWindow.cpp \
../../LogHandlerWidget.cpp \
../../main.cpp \
../../MainWindowTabWidget.cpp \
../../nv1.cpp \
../../ResultsWindow.cpp \
../../ErrorDialog.cpp \
../../JobManagement/GROMACS_JobMonitor.cpp \
../../JobManagement/JobMonitor.cpp \
 ../../TrajectoryGraphicsWindow.cpp \
 ../../StructureGraphicsWindow.cpp \
 ../../InputParametersWindow.cpp \
 ../../ResultsSummaryWindow.cpp

HEADERS += ../../DataWindow.h \
../../LogHandlerWidget.h \
../../main.h \
../../MainWindowTabWidget.h \
../../nv1.h \
../../ResultsWindow.h \
../../ErrorDialog.h \
../../JobManagement/GROMACS_JobMonitor.h \
../../JobManagement/JobMonitor.h \
 ../../TrajectoryGraphicsWindow.h \
 ../../StructureGraphicsWindow.h \
 ../../InputParametersWindow.h \
 ../../ResultsSummaryWindow.h

FORMS += ../../LogHandlerWidget.ui \
../../MainWindowTabWidget.ui \
../../ResultsWindow.ui \
../../ErrorDialog.ui \
 ../../TrajectoryGraphicsWindow.ui \
 ../../InputParametersWindow.ui \
 ../../ResultsSummaryWindow.ui

RESOURCES += ../../application.qrc

INCLUDEPATH += ../../../include \
 $(OPENBABEL_INCPATH) \
 ../../Plugins/RenderingEngines/OpenGL/GLT \
 ../../../src

TARGET = nv1

DESTDIR = ../../../bin

# This tells qmake to not create a Mac bundle for this application.
CONFIG -= app_bundle

#macx : TARGETDEPS ~= s/.so/.dylib/g

