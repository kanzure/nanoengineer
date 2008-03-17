#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.56)

# Autoconf composes the distribution filename like: 4thArg-2ndArg, but we want
# an underscore between the NanoEngineer-1 and its version. The following line
# looks strange but gets us what we want.
AC_INIT(HDF5_SimResults, 0.1.0, support@nanorex.com, HDF5_SimResults)

AM_INIT_AUTOMAKE
AC_COPYRIGHT([Copyright 2008 Nanorex, Inc.  See LICENSE file for details.])
AC_CONFIG_SRCDIR([src/HDF5_SimResults.cpp])
AC_CONFIG_HEADER([config.h])

# Checks for programs.
AC_PROG_CXX
AC_PROG_CC
AC_PROG_LIBTOOL
AC_PROG_INSTALL
AC_PROG_LN_S

#
# Check if we're building the CppUnit tests
#
AC_ARG_ENABLE(cppunit-tests,
            AC_HELP_STRING([--enable-cppunit-tests],
                           [build the CppUnit test suites]))
if test -z "$enable_cppunit_tests"; then
  enable_cppunit_tests="no"
fi
AM_CONDITIONAL([ENABLE_CPPUNIT_TESTS], [test "$enable_cppunit_tests" = "yes"])


#
# Checks for libraries.
#
CHECK_HDF5()

#   CppUnit Tests (CppUnit)
if test "$enable_cppunit_tests" = "yes"; then
  CHECK_CPPUNIT([1.10.0])
fi


# Checks for header files.
#AC_HEADER_STDC
#AC_CHECK_HEADERS([limits.h stdlib.h string.h sys/time.h unistd.h])

# Checks for typedefs, structures, and compiler characteristics.
#AC_C_CONST
#AC_HEADER_STDBOOL
#AC_C_INLINE
#AC_C_RESTRICT
#AC_HEADER_TIME
#AC_STRUCT_TM
#AC_C_VOLATILE

# Checks for library functions.
#AC_FUNC_MALLOC
#AC_FUNC_MEMCMP
#AC_HEADER_MAJOR
#AC_FUNC_REALLOC
#AC_FUNC_SELECT_ARGTYPES
#AC_TYPE_SIGNAL
#AC_FUNC_STAT
#AC_FUNC_STRTOD
#AC_FUNC_VPRINTF
#AC_CHECK_FUNCS([clock_gettime gettimeofday memmove memset pow select sqrt strcasecmp strerror strncasecmp strtol])

# Miscellaneous
AC_SUBST(UNAME_A, "$(uname -a)")

AC_CONFIG_FILES([Makefile src/Makefile src/Testing/Makefile])
AC_OUTPUT

