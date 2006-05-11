#include "HashMap.h"

HashMap::HashMap()
{
    size = 0;
    capacity = 20;
    keys = new int[20];
    values = new ArrayList[20];
}

void HashMap::put(int x, ArrayList alst)
{
    for (int i = 0; i < size; i++)
	if (keys[i] == x) {
	    values[i] = alst;
	    return;
	}
    if (size + 1 > capacity) {
	capacity *= 2;
	int *newkeys = new int[capacity];
	ArrayList *newvals = new ArrayList[capacity];
	for (int i = 0; i < size; i++) {
	    newkeys[i] = keys[i];
	    newvals[i] = values[i];
	}
	delete[] keys;
	delete[] values;
	keys = newkeys;
	values = newvals;
    }
    keys[size] = x;
    values[size] = alst;
    size++;
}

ArrayList HashMap::get(int x) throw()
{
    for (int i = 0; i < size; i++)
	if (keys[i] == x)
	    return values[i];
    throw std::exception();
}

int HashMap::hasKey(int x)
{
    for (int i = 0; i < size; i++)
	if (keys[i] == x)
	    return 1;
    return 0;
}
