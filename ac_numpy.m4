
#
# CHECK_NUMPY(DESIRED-VERSION)
#
AC_DEFUN([CHECK_NUMPY], [
	desired_version=$1

	found_version=`python -c "from numpy import version; print version.version"`
	CHECK_DESIRED_VERSION([NumPy], $desired_version, $found_version)
])

