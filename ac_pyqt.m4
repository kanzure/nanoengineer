
#
# CHECK_PYQT(DESIRED-VERSION)
#
AC_DEFUN([CHECK_PYQT], [
	desired_version=$1

	found_version=`python -c "from PyQt4 import pyqtconfig; config = pyqtconfig.Configuration(); print config.pyqt_version_str"`
	CHECK_DESIRED_VERSION([PyQt], $found_version, $found_version)
])

