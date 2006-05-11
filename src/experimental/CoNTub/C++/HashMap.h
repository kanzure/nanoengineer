#ifndef HASHMAP_H_INCLUDED
#define HASHMAP_H_INCLUDED

#include <iostream>
#include <string.h>
#include <exception>
#include "ArrayList.h"

class HashMap
{
    int size, capacity;
    int *keys;
    ArrayList *values;
public:
    HashMap(void);
    void put(int, ArrayList);
    ArrayList get(int) throw();
    int hasKey(int);
};

#endif
