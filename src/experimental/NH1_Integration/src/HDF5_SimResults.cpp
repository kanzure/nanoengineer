
/* Copyright (c) 2006 Nanorex, Inc.  All rights reserved. */

#include "HDF5_SimResults.h"

namespace ne1 {


/* CONSTRUCTOR */
HDF5_SimResults::HDF5_SimResults() {
}


/* DESTRUCTOR */
HDF5_SimResults::~HDF5_SimResults() {
}


/* FUNCTION: openDataStore */
int HDF5_SimResults::openDataStore(const char* directory,
								   std::string& message) {
	printf("\ndirectory=%s\n", directory);
	
	return 0;
}

} // ne1::
