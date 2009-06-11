#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.61)

# Autoconf composes the distribution filename like: 4thArg-2ndArg, but we want
# an underscore between the NanoEngineer-1 and its version. The following line
# looks strange but gets us what we want.
AC_INIT(NanoEngineer, 1_0.9.2, support@nanorex.com, NanoEngineer)

# FIXME: add configure check for libgle.so: GLE Tubing and Extrusion
# library.

AM_INIT_AUTOMAKE
AC_COPYRIGHT([Copyright 2007 Nanorex, Inc.  See LICENSE file for details.])
AC_CONFIG_SRCDIR([cad/src/widgets/NE1ToolBar.py])
AC_CONFIG_HEADER([config.h])

# Checks for programs.
AM_PATH_PYTHON([2.3])
AC_SUBST(PYTHON_BASE, "$(echo ${PYTHON} | sed "s%/bin/python%%")")
AC_PATH_PROG(PYREXC, pyrexc)
AC_PROG_CXX
AC_PROG_CC
AC_PROG_LIBTOOL
AC_PROG_INSTALL
AC_PROG_LN_S

#
# Check strictness option
#
AC_ARG_ENABLE(strict-library-check,
			  AC_HELP_STRING([--enable-strict-library-check],
							 [fail if non-officially-supported libraries are found]))
if test "$enable_strict_library_check" = "yes"; then
	AC_SUBST(STRICT_LIBRARY_CHECK, "yes")
	echo "### Strict library checking is on."
else
	AC_SUBST(STRICT_LIBRARY_CHECK, "no")
fi


#
# Check if we're freezing the code
#
AC_ARG_WITH(freezepython-prefix,
            AC_HELP_STRING([--with-freezepython-prefix=PREFIX],
                           [find FreezePython installed under PREFIX]),
            freezepython_prefix="$withval", freezepython_prefix="")
if test -n "$freezepython_prefix"; then
    AC_SUBST(FREEZEPYTHON, "$freezepython_prefix/FreezePython")
fi
AM_CONDITIONAL([RUN_FREEZEPYTHON], [test -n "$freezepython_prefix"])


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
CHECK_FREEZEPYTHON([3.0.3])
CHECK_QT([4.2.3])
CHECK_PYQT([4.2])
CHECK_NUMARRAY([1.5.2])
CHECK_NUMERIC([23.8])
CHECK_NUMPY([1.0.2])
CHECK_CTYPES([1.0.2])
CHECK_PYOPENGL([3.0.0a6])
CHECK_PIL([1.1.6])

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

AC_CONFIG_FILES([Makefile
		cad/Makefile
			cad/doc/Makefile
			cad/src/Makefile
			cad/partlib/Makefile
			cad/plugins/Makefile
				cad/plugins/DNA/Makefile
				cad/plugins/HDF5_SimResults/Makefile
					cad/plugins/HDF5_SimResults/src/Makefile
						cad/plugins/HDF5_SimResults/src/Testing/Makefile
		debian/postinst
		sim/Makefile
			sim/src/Makefile])
AC_OUTPUT

