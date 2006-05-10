#ifndef TABPE_H_INCLUDED
#define TABPE_H_INCLUDED

#include "Color.h"

class tabPe
{
 public:
    String getSimbolo (int t);
    Color getColor (int t);
    int getSize (int t);
};

extern tabPe tabPe_getInstance(void);

#endif
