#
# CHECK_HDF5()
#
AC_DEFUN([CHECK_HDF5],[
  AC_REQUIRE([AC_PROG_CC])
  AC_REQUIRE([AC_PATH_XTRA])
        
  AC_ARG_WITH(hdf5,
    AC_HELP_STRING([--with-hdf5=PATH],[directory with HDF5 inside]),
    # expand tilde / other stuff
    eval with_hdf5=$with_hdf5
  )

 # store values
 ac_save_CFLAGS="$CFLAGS"
 ac_save_LDFLAGS="$LDFLAGS"
 ac_save_LIBS="$LIBS"
 LIBS=""

 # start building variables

 # use special HDF5-lib-path if it's set
 if test x$with_hdf5 != x ; then
   #  extract absolute path
   if test -d $with_hdf5; then
     eval with_hdf5=`cd $with_hdf5 ; pwd`
   else
     AC_MSG_ERROR([HDF5-directory $with_hdf5 does not exist])
   fi
   LDFLAGS="$LDFLAGS -L$with_hdf5/lib"
   HDF5_LDFLAGS="$LDFLAGS"
   CPPFLAGS="$CPPFLAGS -I$with_hdf5/include"
 fi

 # test for an arbitrary header
 AC_CHECK_HEADER([hdf5.h], 
   [HAVE_HDF5=1]
    HDF5_CPPFLAGS="$CPPFLAGS",
   [HAVE_HDF5=0])

 # test for lib
 if test x$HAVE_HDF5 = x1 ; then
   AC_CHECK_LIB(hdf5, H5open,[HDF5_LIBS=-lhdf5],[HAVE_HDF5=0]) #,-lz, -lsz)
 fi

 # pre-set variable for summary
 with_hdf5="no"

 # did we succeed?
 if test x$HAVE_HDF5 = x1 ; then
   AC_SUBST(HDF5_CPPFLAGS, $HDF5_CPPFLAGS)
   AC_SUBST(HDF5_LDFLAGS, $HDF5_LDFLAGS)
   AC_SUBST(HDF5_LIBS, $HDF5_LIBS)
   AC_DEFINE(HAVE_HDF5, 1, [Define to 1 if hdf5 was found])

   # proudly show in summary
   with_hdf5="yes"
 fi

 # also tell automake
 AM_CONDITIONAL(HDF5, test x$HAVE_HDF5 = x1)

 # reset values					    
 CFLAGS="$ac_save_CFLAGS"
 LIBS="$ac_save_LIBS"
 LDFLAGS="$ac_save_LDFLAGS"

])
