
#
# CHECK_NUMARRAY(DESIRED-VERSION)
#
AC_DEFUN([CHECK_NUMARRAY], [
	desired_version=$1

	found_version=`python -c "from numarray import numinclude; print numinclude.version"`
	CHECK_DESIRED_VERSION([numarray], $desired_version, $found_version)
])

