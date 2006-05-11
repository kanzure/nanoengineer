#ifndef TABPE_H_INCLUDED
#define TABPE_H_INCLUDED

#include "String.h"

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
