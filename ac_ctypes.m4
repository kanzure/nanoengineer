
#
# CHECK_CTYPES(DESIRED-VERSION)
#
AC_DEFUN([CHECK_CTYPES], [
	desired_version=$1

	found_version=`python -c "import ctypes;print ctypes.__version__"`
	CHECK_DESIRED_VERSION([ctypes], $desired_version, $found_version)
])

