SOURCES +=  NXCommandResult.cpp \
  NXLogger.cpp \
  NXPlugin.cpp \
  NXPluginGroup.cpp \
  NXProperties.cpp \
  NXStringTokenizer.cpp \
  NXUtility.cpp







HEADERS += ../../include/Nanorex/Utility/NXLogger.h \
../../include/Nanorex/Utility/NXPluginGroup.h \
../../include/Nanorex/Utility/NXPlugin.h \
../../include/Nanorex/Utility/NXProperties.h \
../../include/Nanorex/Utility/NXStringTokenizer.h \
../../include/Nanorex/Utility/NXUtility.h \
 ../../include/Nanorex/Utility/NXCommandResult.h
TEMPLATE = lib

CONFIG += dll



INCLUDEPATH += ../../include

DESTDIR = ../../lib

TARGET = NanorexUtility

