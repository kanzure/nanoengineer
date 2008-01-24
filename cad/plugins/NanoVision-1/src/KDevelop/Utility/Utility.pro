SOURCES +=  ../../Utility/NXCommandResult.cpp \
  ../../Utility/NXLogger.cpp \
  ../../Utility/NXPlugin.cpp \
  ../../Utility/NXPluginGroup.cpp \
  ../../Utility/NXProperties.cpp \
  ../../Utility/NXStringTokenizer.cpp \
  ../../Utility/NXUtility.cpp

HEADERS += ../../include/Nanorex/Utility/NXLogger.h \
../../include/Nanorex/Utility/NXPluginGroup.h \
../../include/Nanorex/Utility/NXPlugin.h \
../../include/Nanorex/Utility/NXProperties.h \
../../include/Nanorex/Utility/NXStringTokenizer.h \
../../include/Nanorex/Utility/NXUtility.h \
 ../../include/Nanorex/Utility/NXCommandResult.h

TEMPLATE = lib

CONFIG += dll



TARGET = NanorexUtility

DESTDIR = ../../../lib

INCLUDEPATH += ../../../include

