// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef JOBHANDLE_H
#define JOBHANDLE_H

#include <string>
using namespace std;


/* CLASS: JobHandle */
class JobHandle {

public:
	JobHandle(const string& initString);
	virtual ~JobHandle();
};

#endif
