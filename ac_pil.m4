
#
# CHECK_PIL(DESIRED-VERSION)
#
AC_DEFUN([CHECK_PIL], [
	desired_version=$1

	found_version=`python -c "from PIL import Image; print Image.VERSION"`
	CHECK_DESIRED_VERSION([PIL], $desired_version, $found_version)
])

