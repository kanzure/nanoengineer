
INCLUDES = -I../include

lib_LTLIBRARIES = libHDF5_SimResults.la

#libHDF5_SimReslts_la_CPPFLAGS = @LOG4CPP_CFLAGS@ @NSPR_CFLAGS@ @ZLIB_CFLAGS@
libHDF5_SimResults_la_LIBADD = -lhdf5
libHDF5_SimResults_la_LDFLAGS = -version-info 1:0:0
 
#nanohiveutildir = $(includedir)/NanoHiveUtil
#nanohiveutil_HEADERS = \
#	$(top_builddir)/../include/NanoHiveUtil/CmdLine.h \
#	$(top_builddir)/../include/NanoHiveUtil/ZipUnzip/zip.h
ne1includedir = $(includedir)/ne1
ne1include_HEADERS = ../include/ne1/HDF5_SimResults.h ../include/ne1/SimResultsDataStore.h
 
libHDF5_SimResults_la_SOURCES = \
	HDF5_SimResults.cpp \
	SimResultsDataStore.cpp

