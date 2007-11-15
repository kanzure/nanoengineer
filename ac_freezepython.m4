
#
# CHECK_FREEZEPYTHON(DESIRED-VERSION)
#
AC_DEFUN([CHECK_FREEZEPYTHON], [
	desired_version=$1

	if test -n "$FREEZEPYTHON"; then

		# Check version
		found_version=`$FREEZEPYTHON --version`
		found_version=`echo $found_version | \
			sed 's/FreezePython \([[0-9]]*.[[0-9]]*.[[0-9]]*\).*/\1/'`
		CHECK_VERSION($found_version, $desired_version)
		version_check=$CHECK_VERSION_RESULT
		if test $version_check -lt 0; then
			echo "*** FreezePython version $desired_version or later is required, but version $found_version "
			echo "*** was found instead. Either update your FreezePython, or don't use the"
			echo "*** --with-freezepython-prefix option."
			exit -1
		elif test $version_check -gt 0; then
			echo "### FreezePython version $found_version was found. That version may work, but the"
			echo "### officially supported version is $desired_version."
			if test "$STRICT_LIBRARY_CHECK" = "yes"; then
				echo "*** Strict library check failed. Either install the officially supported"
				echo "*** version, or don't use the --enable-strict-library-check option."
				exit -1
			fi
		fi
	else
		echo "### We're not building an executable distribution nor freezing the app."
		echo "### The --with-freezepython-prefix option was not specified."
	fi
])

