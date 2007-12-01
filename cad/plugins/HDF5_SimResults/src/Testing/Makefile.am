
INCLUDES = -I../../include -I..

bin_PROGRAMS = hdf5CppUnit Producer Consumer

hdf5CppUnit_SOURCES = CppUnit.cpp ../HDF5_SimResultsTest.cpp
hdf5CppUnit_CPPFLAGS = @CPPUNIT_CFLAGS@
hdf5CppUnit_LDFLAGS = -L../.libs
hdf5CppUnit_LDADD = @CPPUNIT_LIBS@ -lHDF5_SimResults -lhdf5

Producer_SOURCES = Producer.cpp
Producer_LDFLAGS = -L../.libs
Producer_LDADD = -lHDF5_SimResults -lhdf5

Consumer_SOURCES = Consumer.cpp
Consumer_LDFLAGS = -L../.libs
Consumer_LDADD = -lrt -lHDF5_SimResults -lhdf5

