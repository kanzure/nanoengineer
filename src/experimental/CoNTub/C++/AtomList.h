#ifndef ARRAYLIST_H_INCLUDED
#define ARRAYLIST_H_INCLUDED

#include "Atomo.h"

class AtomList
{
    int _size, capacity;
    Atomo *contents;
public:
    AtomList(void);
    AtomList(int n);
    ~AtomList(void);
    Atomo *get(int i);
    void add(Atomo a);
    int size(void);
    void remove(int);
    void set(int, Atomo);
    int contains(Atomo);
};

#endif
