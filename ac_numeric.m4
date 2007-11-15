
#
# CHECK_NUMERIC(DESIRED-VERSION)
#
AC_DEFUN([CHECK_NUMERIC], [
	desired_version=$1

	found_version=`python -c "from numeric_version import version; print version"`
	CHECK_DESIRED_VERSION([Numeric], $desired_version, $found_version)
])

