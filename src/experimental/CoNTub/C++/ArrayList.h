#ifndef ARRAYLIST_H_INCLUDED
#define ARRAYLIST_H_INCLUDED

#include "Atomo.h"

class ArrayList
{
public:
    ArrayList(void) { }
    ArrayList(int n) { }
    Atomo get(int i);
    void add(Atomo a);
    int size();
};

#endif
