
/* Copyright (c) 2006 Nanorex, Inc.  All rights reserved. */

#ifndef NE1_HDF5_SIMRESULTS_H
#define NE1_HDF5_SIMRESULTS_H

#include <stdlib.h>
#include <string>

#include "SimResultsDataStore.h"

namespace ne1 {


/* CLASS: HDF5_SimResults
 *
 * HDF5 implementation of SimResultsDataStore.
 */
class HDF5_SimResults : public SimResultsDataStore {
  public:
	HDF5_SimResults();
	~HDF5_SimResults();
	int openDataStore(const char* directory, std::string& message);
};

} // ne1::

#endif
