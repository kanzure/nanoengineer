#ifndef TABPE_H_INCLUDED
#define TABPE_H_INCLUDED

class Color;

class tabPe
{
 public:
    char * getSimbolo (int t);
    Color *getColor (int t);
    int getSize (int t);
};

extern tabPe * tabPe_getInstance(void);

#endif
