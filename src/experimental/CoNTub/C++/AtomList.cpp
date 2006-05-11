/*
 * This is a C++ version of Java's AtomList class.
 */

#include <assert.h>
#include "AtomList.h"

AtomList::AtomList(void)
{
    _size = 0;
    capacity = 20;
    contents = new Atomo[capacity];
}

AtomList::AtomList(int n)
{
    _size = 0;
    if (n < 20)
	n = 20;
    capacity = n;
    contents = new Atomo[n];
}

AtomList::~AtomList(void)
{
    //delete[] contents;
}

Atomo * AtomList::get(int i)
{
    return &contents[i];
}

void AtomList::add(Atomo a)
{
    if (_size + 1 > capacity) {
	Atomo *newcontents;
	capacity *= 2;
	newcontents = new Atomo[capacity];
	for (int i = 0; i < _size; i++)
	    newcontents[i] = contents[i];
	// delete[] contents;
	contents = newcontents;
    }
    contents[_size++] = a;
}

int AtomList::size(void)
{
    return _size;
}

void AtomList::remove(int i)
{
    assert(i < _size);
    while (i + 1 < _size) {
	contents[i] = contents[i + 1];
	i++;
    }
    _size--;
}

void AtomList::set(int i, Atomo a)
{
    contents[i] = a;
}

int AtomList::contains(Atomo a)
{
    for (int i = 0; i < _size; i++) {
	assert(a.index != -1);
	assert(contents[i].index != -1);
	if (a.index == contents[i].index)
	    return 1;
    }
    return 0;
}
