
#
# CHECK_PYOPENGL(DESIRED-VERSION)
#
AC_DEFUN([CHECK_PYOPENGL], [
	desired_version=$1

	found_version=`python -c "import OpenGL;print OpenGL.__version__"`
	CHECK_DESIRED_VERSION([PyOpenGL], $desired_version, $found_version)
])

