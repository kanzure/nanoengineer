
TEMPLATE = app
TARGET = nv1
DESTDIR = ../../../bin/

CONFIG += stl \
 opengl \
 release \
 rtti

QT += opengl

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
 ../../ResultsSummaryWindow.cpp \
 ../../JobSelectorDialog.cpp \
 ../../PreferencesDialog.cpp \
 ../../UserSettings.cpp \
 ../../AboutBox.cpp

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
 ../../ResultsSummaryWindow.h \
 ../../JobSelectorDialog.h \
 ../../PreferencesDialog.h \
 ../../UserSettings.h \
 ../../AboutBox.h

FORMS += ../../LogHandlerWidget.ui \
 ../../MainWindowTabWidget.ui \
 ../../ResultsWindow.ui \
 ../../ErrorDialog.ui \
 ../../TrajectoryGraphicsWindow.ui \
 ../../InputParametersWindow.ui \
 ../../ResultsSummaryWindow.ui \
 ../../JobSelectorDialog.ui \
 ../../PreferencesDialog.ui \
 ../../AboutBox.ui

RESOURCES += ../../application.qrc

INCLUDEPATH += ../../../include \
 $(OPENBABEL_INCPATH) \
 $(HDF5_SIMRESULTS_INCPATH) \
 ../../Plugins/RenderingEngines/OpenGL/GLT \
 ../../../src \
 ../../../src/Plugins/RenderingEngines/OpenGL

# This tells qmake to not create a Mac bundle for this application.
CONFIG -= app_bundle 

#QMAKE_CXXFLAGS_DEBUG += -DNX_DEBUG \
# -g \
# -O0 \
# -fno-inline

QMAKE_CXXFLAGS_RELEASE += -DNDEBUG -O2

TARGETDEPS += ../../../lib/libNanorexInterface.so \
  ../../../lib/libNanorexUtility.so
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

#CONFIG(debug,debug|release) {
#	TARGET = $${TARGET}_d
#	PROJECTLIBS ~= s/(.+)/\1_d/g
#	TARGETDEPS ~= s/(.+).so/\1_d.so/g
#}

LIBS += -L../../../lib \
  -lNanorexUtility -lNanorexInterface \
  -L$(OPENBABEL_LIBPATH) \
  -lopenbabel

# qmake puts these library declarations too early in the g++ command on win32
win32 : LIBS += -lopengl32 -lglu32 -lgdi32 -luser32

# make clean target
QMAKE_CLEAN += $${DESTDIR}$${TARGET}

