
#
# CHECK_CPPUNIT(MINIMUM-VERSION)
#

AC_DEFUN([CHECK_CPPUNIT], [
  min_version=$1

  AC_ARG_WITH(cppunit-prefix,
              AC_HELP_STRING([--with-cppunit-prefix=PREFIX],
                             [find CppUnit installed under PREFIX]),
              cppunit_prefix="$withval", cppunit_prefix="")
  AC_ARG_WITH(cppunit-exec-prefix,
              AC_HELP_STRING([--with-cppunit-exec-prefix=EPREFIX],
                             [the exec prefix where CppUnit binaries were installed]),
              cppunit_exec_prefix="$withval", cppunit_exec_prefix="")

  if test -n "$cppunit_exec_prefix"; then
    AC_PATH_PROG(CPPUNIT_CONFIG_SCRIPT, cppunit-config, no,
                 "$cppunit_exec_prefix/bin")
  else
    if test -n "$cppunit_prefix"; then
      AC_PATH_PROG(CPPUNIT_CONFIG_SCRIPT, cppunit-config, no,
                   "$cppunit_prefix/bin")
    else
      AC_PATH_PROG(CPPUNIT_CONFIG_SCRIPT, cppunit-config, no)
    fi
  fi

  if test "$CPPUNIT_CONFIG_SCRIPT" = "no" ; then
    echo "*** CppUnit version $min_version or later is required to build the CppUnit test"
    echo "*** suite, but it was not found. Either install the latest CppUnit"
    echo "*** (http://cppunit.sourceforge.net/), or"
    echo "*** adjust your PATH environment variable or use the --with-cppunit-prefix or"
    echo "*** --with-cppunit-exec-prefix options so that the cppunit-config script for"
    echo "*** your installation can be found, or don't specify the --enable-cppunit-tests"
    echo "*** option."
    exit -1
  else
    #
    # Check version
    #
    AC_MSG_CHECKING(for CppUnit version >= $min_version)
    found_lib_version=`$CPPUNIT_CONFIG_SCRIPT --version`
    found_major_version=`echo $found_lib_version | \
           sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)[[a-z]]*/\1/'`
    found_minor_version=`echo $found_lib_version | \
           sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)[[a-z]]*/\2/'`
    found_micro_version=`echo $found_lib_version | \
           sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)[[a-z]]*/\3/'`

    min_major_version=`echo "$min_version" | \
           sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)/\1/'`
    min_minor_version=`echo "$min_version" | \
           sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)/\2/'`
    min_micro_version=`echo "$min_version" | \
           sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)/\3/'`

    version_ok=no
    if test $found_major_version -gt $min_major_version; then
      version_ok=yes
    elif test $found_major_version -eq $min_major_version && \
         test $found_minor_version -gt $min_minor_version; then
      version_ok=yes
    elif test $found_major_version -eq $min_major_version && \
         test $found_minor_version -eq $min_minor_version && \
         test $found_micro_version -ge $min_micro_version; then
      version_ok=yes
    fi

    if test "$version_ok" = "no"; then
      AC_MSG_RESULT(no)
      echo "*** CppUnit version $min_version or later is required, but an old version"
      echo "*** was found ($found_lib_version). Please install the latest CppUnit"
      echo "*** (http://cppunit.sourceforge.net/)."
      exit -1
    else
      AC_MSG_RESULT(yes)
    fi

    #
    # Check libs
    #
    libs_result=`$CPPUNIT_CONFIG_SCRIPT --libs`
    if test "x$libs_result" != "x"; then
      AC_SUBST(CPPUNIT_LIBS, "$libs_result")
    fi

    #
    # Check includes
    #
    includes_result=`$CPPUNIT_CONFIG_SCRIPT --cflags`
    if test "x$includes_result" != "x"; then
      AC_SUBST(CPPUNIT_CFLAGS, "$includes_result")
    fi
  fi
])

