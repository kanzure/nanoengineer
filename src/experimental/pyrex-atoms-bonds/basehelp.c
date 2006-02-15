#include "Python.h"

#if 0
#define MARK()  fprintf(stderr, "%s:%d\n", __FUNCTION__, __LINE__)
#define PTR(x)  fprintf(stderr, "%s:%d %s=%p\n", __FUNCTION__, __LINE__, #x, x)
#define INT(x)  fprintf(stderr, "%s:%d %s=%d\n", __FUNCTION__, __LINE__, #x, x)
#else
#define MARK()
#define PTR(x)
#define INT(x)
#endif

#define MAX_NUM_NEIGHBORS 12  // ask Damian for the real number

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

struct intset {
    int **pointers[512];
};

static struct intset *intset_init(void)
{
    struct intset *is;
    is = malloc(sizeof(struct intset));
    if (is == NULL) {
	problem = "Out of memory";
	return NULL;
    }
    PTR(is);
    bzero(is->pointers, 512 * sizeof(int**));
    return is;
}

static PyObject *intset_contains(struct intset *is, int x)
{
    int x0, x1, x2, x3;
    int **block2, *block;
    if (is == NULL) goto fail;
    PTR(is);
    x0 = (x >> 22) & 0x1FF;
    x1 = (x >> 13) & 0x1FF;
    x2 = (x >> 5) & 0xFF;
    x3 = x & 0x1F;
    INT(x0);
    INT(x1);
    INT(x2);
    INT(x3);
    block2 = is->pointers[x0];
    PTR(block2);
    if (block2 == NULL) goto false;
    block = block2[x1];
    PTR(block);
    if (block == NULL) goto false;
    PTR(block[x2]);
    if ((block[x2] & (1 << x3)) == 0) goto false;
    Py_INCREF(Py_True);
    return Py_True;
 false:
    MARK();
    Py_INCREF(Py_False);
    return Py_False;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static PyObject *intset_remove(struct intset *is, int x)
{
    int x0, x1, x2, x3;
    int **block2, *block;
    if (is == NULL) goto fail;
    PTR(is);
    x0 = (x >> 22) & 0x1FF;
    x1 = (x >> 13) & 0x1FF;
    x2 = (x >> 5) & 0xFF;
    x3 = x & 0x1F;
    block2 = is->pointers[x0];
    if (block2 == NULL) goto done;
    block = block2[x1];
    if (block == NULL) goto done;
    block[x2] &= ~(1 << x3);
 done:
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static PyObject *intset_add(struct intset *is, int x)
{
    int x0, x1, x2, x3;
    int **block2, *block;
    if (is == NULL) goto fail;
    PTR(is);
    x0 = (x >> 22) & 0x1FF;
    x1 = (x >> 13) & 0x1FF;
    x2 = (x >> 5) & 0xFF;
    x3 = x & 0x1F;
    INT(x0);
    INT(x1);
    INT(x2);
    INT(x3);
    block2 = is->pointers[x0];
    PTR(block2);
    if (block2 == NULL) {
	block2 = is->pointers[x0] = (int**) malloc(512 * sizeof(int*));
	if (block2 == NULL) goto fail;
	bzero(block2, 512 * sizeof(int*));
    }
    PTR(block2);
    block = block2[x1];
    PTR(block);
    if (block == NULL) {
	block = block2[x1] = (int*) malloc(256 * sizeof(int));
	if (block == NULL) goto fail;
	bzero(block, 256 * sizeof(int));
    }
    PTR(block);
    block[x2] |= 1 << x3;
    PTR(block[x2]);
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static PyObject *intset_del(struct intset *is)
{
    int i, j;
    if (is == NULL) goto fail;
    PTR(is);
    for (i = 0; i < 512; i++) {
	if (is->pointers[i] != NULL) {
	    for (j = 0; j < 512; j++) {
		if ((is->pointers[i])[j] != NULL) {
		    free((is->pointers[i])[j]);
		}
	    }
	    free(is->pointers[i]);
	}
    }
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
    int numNeighbors;
    int bondIndices[MAX_NUM_NEIGHBORS];
};

struct atombase *atombase_init(void)
{
    struct atombase *ab;
    ab = malloc(sizeof(struct atombase));
    if (ab == NULL) {
	problem = "Out of memory";
	return NULL;
    }
    PTR(ab);
    return ab;
}

void atombase_del(struct atombase* ab)
{
    // nothing to do yet
    PTR(ab);
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
    int atomtype;
    double x, y, z;
};
struct chunkbase {
    int numatoms;
    int arraysize;
    struct position *positions;
};

struct chunkbase * chunkbase_init(void)
{
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
    PTR(cb);
    return cb;
}

void chunkbase_del(struct chunkbase *cb)
{
    PTR(cb);
    if (cb && cb->positions)
	free(cb->positions);
}

PyObject *chunkbase_addatom(struct chunkbase *cb, struct atombase *ab,
			    int atomtype,
			    double x, double y, double z)
{
    if (cb == NULL) goto fail;
    PTR(cb);
    /* The first edge case is going from 999 atoms to 1000 atoms. */
    if (cb->numatoms + 1 >= cb->arraysize) {
	cb->arraysize *= 2;
	cb->positions = realloc(cb->positions,
				cb->arraysize * sizeof(struct position));
	if (cb->positions == NULL) goto fail;
    }
    cb->positions[cb->numatoms].atomtype = atomtype;
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
