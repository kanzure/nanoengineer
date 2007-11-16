
INCLUDES = -I../../include -I..

bin_PROGRAMS = hdf5CppUnit

hdf5CppUnit_SOURCES = CppUnit.cpp ../HDF5_SimResultsTest.cpp

hdf5CppUnit_CPPFLAGS = @CPPUNIT_CFLAGS@
hdf5CppUnit_LDFLAGS = -L../.libs
hdf5CppUnit_LDADD = @CPPUNIT_LIBS@ -lHDF5_SimResults -lhdf5

