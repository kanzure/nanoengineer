// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/* $Id$ */

#ifndef TABPE_H_INCLUDED
#define TABPE_H_INCLUDED

#include "String.h"

/*
 * There is never a need for more than one periodic table in any
 * program run. The periodicTable() function provides a pointer to
 * an instance of the periodic table, and that's the right thing
 * to use.
 */

class tabPe
{
    String *simbolo;
    double *sz, *en2, *en3;
 public:
    double *en1;
    tabPe();  // only to be called from tabPe_getInstance()
    String getSimbolo (int t);
    double getSize (int t);
};

tabPe *periodicTable(void);

#endif
