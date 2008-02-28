#!/bin/sh

export OPENBABEL_INCPATH=/usr/local/include/openbabel-2.0
export OPENBABEL_LIBPATH=/usr/local/lib
export HDF5_SIMRESULTS_LIBPATH=/usr/local/lib
export HDF5_SIMRESULTS_INCPATH=/usr/local/include

kdevelop --profile CandCppIDE src/KDevelop/nv1.kdevelop

