#ifndef TABPE_H_INCLUDED
#define TABPE_H_INCLUDED

#include "Color.h"

class tabPe
{
    String *simbolo;
    Color *col;
 public:
    double *sz, *en1, *en2, *en3;
    String getSimbolo (int t);
    Color getColor (int t);
    int getSize (int t);
};

extern tabPe tabPe_getInstance(void);

#endif
