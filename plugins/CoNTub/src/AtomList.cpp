// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
/* $Id$ */

/*
 * This is a C++ version of Java's AtomList class.
 */

#include <iostream>
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

/*
 * There is a very effective optimization that can be used
 * for neighborhoods. I am not doing it here until I think
 * we need it, because it's a bit of work. As you add atoms
 * to the AtomList, you save a pointer to them in one of several
 * lists, pre-sorting atoms by coarse position. Doing so is
 * very quick. Then when you want the neighborhood around an
 * atom, you need only search the nearby buckets.
 */

#define GAP  (1.5 * 1.42)

int closeEnough(Atomo *a1, Atomo *a2)
{
    double distx = a1->vert.x - a2->vert.x;
    if (distx < -GAP || distx > GAP)
	return 0;
    double disty = a1->vert.y - a2->vert.y;
    if (disty < -GAP || disty > GAP)
	return 0;
    double distz = a1->vert.z - a2->vert.z;
    if (distz < -GAP || distz > GAP)
	return 0;
    double distsq = distx * distx + disty * disty +
	distz * distz;
    return distsq < GAP * GAP;
}

AtomList AtomList::neighborhood(Atomo *a)
{
    AtomList al = AtomList();
    for (int i = 0; i < _size; i++) {
	Atomo *b = &contents[i];
	if (closeEnough(a, b))
	    al.add(*b);
    }
    return al;
}
