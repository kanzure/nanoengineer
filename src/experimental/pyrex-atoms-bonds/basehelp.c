#include "Python.h"

#if 0
#define OBJ(x)  fprintf(stderr, "%s:%d %p\n", __FUNCTION__, __LINE__, x)
#else
#define OBJ(x)
#endif

static char *problem = NULL;

static PyObject *checkForErrors(void)
{
    if (problem != NULL) {
	PyErr_SetString(PyExc_RuntimeError, problem);
	return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}


/*
 * IntSet is an integer set which can be used for selections
 * and similar things. I'm not sure it will necessarily beat
 * Python's list or dictionary for speed. Eventually I'll write
 * performance tests for that.
 */

struct intsetLink {
    struct intsetLink *next;
    int x;
};

struct intset {
    // hash of the integer
    struct intsetLink *hashtable[256];
};


static inline int hash(int x)
{
    return ((x >> 16) ^ (x >> 8) ^ x) & 0xFF;
}

static inline struct intsetLink *seek(struct intsetLink *link, int x)
{
    while (1) {
	if (link == NULL) return NULL;
	if (link->x == x) return link;
	link = link->next;
    }
}

static inline void _remove(struct intsetLink **top, int x)
{
    struct intsetLink *previous, *current;
    if (*top == NULL)
	return;
    if ((*top)->x == x) {
	struct intsetLink *discard;
	discard = *top;
	*top = discard->next;
	free(discard);
	return;
    }
    previous = *top;
    current = previous->next;
    while (current != NULL) {
	if (current->x == x) {
	    previous->next = current->next;
	    free(current);
	    return;
	}
	previous = current;
	current = previous->next;
    }
}

static struct intset *intset_init(void)
{
    int i;
    struct intset *is;
    is = malloc(sizeof(struct intset));
    if (is == NULL) {
	problem = "Out of memory";
	return NULL;
    }
    OBJ(is);
    for (i = 0; i < 256; i++)
	is->hashtable[i] = NULL;
    return is;
}

static PyObject *intset_add(struct intset *is, int x)
{
    int i;
    struct intsetLink *link;
    if (is == NULL) goto fail;
    OBJ(is);
    i = hash(x);
    link = is->hashtable[i];
    if (!seek(link, x)) {
	struct intsetLink *newlink = malloc(sizeof(struct intsetLink));
	if (newlink == NULL) goto fail;
	newlink->next = link;
	newlink->x = x;
	is->hashtable[i] = newlink;
    }
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static PyObject *intset_contains(struct intset *is, int x)
{
    int i;
    struct intsetLink *link;
    if (is == NULL) goto fail;
    OBJ(is);
    i = hash(x);
    link = is->hashtable[i];
    if (seek(link, x)) {
	Py_INCREF(Py_True);
	return Py_True;
    } else {
	Py_INCREF(Py_False);
	return Py_False;
    }
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static PyObject *intset_remove(struct intset *is, int x)
{
    int i;
    if (is == NULL) goto fail;
    OBJ(is);
    i = hash(x);
    _remove(&is->hashtable[i], x);
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static PyObject *intset_del(struct intset *is)
{
    if (is == NULL) goto fail;
    OBJ(is);
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

/*
 * AtomBase
 */
struct atombase {
    int positionIndex;
};

struct atombase *atombase_init(void)
{
    struct atombase *ab;
    ab = malloc(sizeof(struct atombase));
    if (ab == NULL) {
	problem = "Out of memory";
	return NULL;
    }
    OBJ(ab);
    return ab;
}

void atombase_del(struct atombase* ab)
{
    // nothing to do yet
    OBJ(ab);
}


/*
 * BondBase
 */



/*
 * ChunkBase
 *
 * A chunk has a position list. Each atombase includes an index into
 * that position list. The position list starts with room for 1000
 * positions, and gets realloc'ed to double its present size whenever
 * it needs to.
 */
struct position {
    double x, y, z;
};
struct chunkbase {
    int numatoms;
    int arraysize;
    struct position *positions;
};

struct chunkbase * chunkbase_init(void)
{
    int i;
    struct chunkbase *cb;
    cb = malloc(sizeof(struct chunkbase));
    if (cb == NULL) {
	problem = "Out of memory";
	return NULL;
    }
    cb->arraysize = 1000;
    cb->positions = malloc(cb->arraysize * sizeof(struct position));
    if (cb->positions == NULL) {
	problem = "Out of memory";
	return NULL;
    }
    cb->numatoms = 0;
    OBJ(cb);
    return cb;
}

void chunkbase_del(struct chunkbase *cb)
{
    OBJ(cb);
    if (cb && cb->positions)
	free(cb->positions);
}

PyObject *chunkbase_addatom(struct chunkbase *cb, struct atombase *ab,
			    double x, double y, double z)
{
    int i;
    if (cb == NULL) goto fail;
    OBJ(cb);
    /* The first edge case is going from 999 atoms to 1000 atoms. */
    if (cb->numatoms + 1 >= cb->arraysize) {
	cb->arraysize *= 2;
	cb->positions = realloc(cb->positions,
				cb->arraysize * sizeof(struct position));
	if (cb->positions == NULL) goto fail;
    }
    cb->positions[cb->numatoms].x = x;
    cb->positions[cb->numatoms].y = y;
    cb->positions[cb->numatoms].z = z;
    ab->positionIndex = cb->numatoms;
    cb->numatoms++;
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}
