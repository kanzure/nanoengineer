// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef GROMACS_JOBHANDLE_H
#define GROMACS_JOBHANDLE_H

#include <string>
using namespace std;

#include "JobHandle.h"


/* CLASS: GROMACS_JobHandle */
class GROMACS_JobHandle : public JobHandle {

public:
	GROMACS_JobHandle(const string& initString);
	~GROMACS_JobHandle();
};

#endif
