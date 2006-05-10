#ifndef HASHMAP_H_INCLUDED
#define HASHMAP_H_INCLUDED

#include <iostream>
#include <string.h>
#include "ArrayList.h"

class HashMap
{
public:
    HashMap() { }
    void put(int, ArrayList);
    ArrayList get(int);
    int hasKey(int);
};

#endif
