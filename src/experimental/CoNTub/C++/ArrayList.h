#ifndef ARRAYLIST_H_INCLUDED
#define ARRAYLIST_H_INCLUDED

#include "Atomo.h"

class ArrayList
{
    int _size, capacity;
    Atomo *contents;
public:
    ArrayList(void);
    ArrayList(int n);
    ~ArrayList(void);
    Atomo *get(int i);
    void add(Atomo a);
    int size(void);
    void remove(int);
    void set(int, Atomo);
    int contains(Atomo);
};

#endif
