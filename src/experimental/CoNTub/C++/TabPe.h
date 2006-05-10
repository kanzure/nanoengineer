#ifndef TABPE_H_INCLUDED
#define TABPE_H_INCLUDED

#include "String.h"
#include "Color.h"

class tabPe
{
    String *simbolo;
    Color *col;
    double *sz, *en2, *en3;
 public:
    double *en1;
    tabPe();  // only to be called from tabPe_getInstance()
    String getSimbolo (int t);
    Color getColor (int t);
    double getSize (int t);
};

extern tabPe tabPe_getInstance(void);

#endif
