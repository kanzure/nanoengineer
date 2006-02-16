#include <sys/time.h>
#include "Python.h"
#include "Numeric/arrayobject.h"
// Pick up PyArray_FromDimsAndData

#if 0
#define XX(z)   z
#define MARK()  fprintf(stderr, "%s:%d\n", __FUNCTION__, __LINE__)
#define HEX(x)  fprintf(stderr, "%s:%d %s=%p\n", __FUNCTION__, __LINE__, #x, x)
#define INT(x)  fprintf(stderr, "%s:%d %s=%u\n", __FUNCTION__, __LINE__, #x, x)
#define DBL(x)  fprintf(stderr, "%s:%d %s=%le\n", __FUNCTION__, __LINE__, #x, x)
#define BEGIN() startingTime = now()
#define END()   DBL(now() - startingTime)
#else
#define XX(z)
#define MARK()
#define HEX(x)
#define INT(x)
#define BEGIN()
#define END()
#endif


/*
 * Time function for performance measurements, theoretically good to
 * the microsecond.
 */
static double now(void)
{
    struct timeval t;
    if (gettimeofday(&t, (struct timezone*)NULL) == 0)
	return (double)t.tv_sec + t.tv_usec*0.000001;
    else
	return 0.0;
}

#define MAX_NUM_NEIGHBORS 12  // ask Damian for the real number

static char *problem = NULL;
static double startingTime;

/*
 * An alternative way to keep count of the size of an integer set would
 * be to associate with each 512-word block a counter. Increment the
 * counter when you add to the block, decrement when you remove from it.
 * But if you're adding something that's already there, or removing
 * something that isn't there, then you shouldn't increment/decrement;
 * only do so if you're flipping a bit.
 *
 * This adds a teeny amount of overhead on adds and removes, but will
 * greatly reduce the time to get the size of the integer set.
 */
static const unsigned int _bitsums[256] = {
    0,  1,  1,  2,  1,  2,  2,  3,  1,  2,  2,  3,  2,  3,  3,  4,
    1,  2,  2,  3,  2,  3,  3,  4,  2,  3,  3,  4,  3,  4,  4,  5,
    1,  2,  2,  3,  2,  3,  3,  4,  2,  3,  3,  4,  3,  4,  4,  5,
    2,  3,  3,  4,  3,  4,  4,  5,  3,  4,  4,  5,  4,  5,  5,  6,
    1,  2,  2,  3,  2,  3,  3,  4,  2,  3,  3,  4,  3,  4,  4,  5,
    2,  3,  3,  4,  3,  4,  4,  5,  3,  4,  4,  5,  4,  5,  5,  6,
    2,  3,  3,  4,  3,  4,  4,  5,  3,  4,  4,  5,  4,  5,  5,  6,
    3,  4,  4,  5,  4,  5,  5,  6,  4,  5,  5,  6,  5,  6,  6,  7,
    1,  2,  2,  3,  2,  3,  3,  4,  2,  3,  3,  4,  3,  4,  4,  5,
    2,  3,  3,  4,  3,  4,  4,  5,  3,  4,  4,  5,  4,  5,  5,  6,
    2,  3,  3,  4,  3,  4,  4,  5,  3,  4,  4,  5,  4,  5,  5,  6,
    3,  4,  4,  5,  4,  5,  5,  6,  4,  5,  5,  6,  5,  6,  6,  7,
    2,  3,  3,  4,  3,  4,  4,  5,  3,  4,  4,  5,  4,  5,  5,  6,
    3,  4,  4,  5,  4,  5,  5,  6,  4,  5,  5,  6,  5,  6,  6,  7,
    3,  4,  4,  5,  4,  5,  5,  6,  4,  5,  5,  6,  5,  6,  6,  7,
    4,  5,  5,  6,  5,  6,  6,  7,  5,  6,  6,  7,  6,  7,  7,  8,
};

static inline unsigned int sum_of_bits(unsigned int x)
{
    return (_bitsums[(x >> 24) & 0xFF] + _bitsums[(x >> 16) & 0xFF] +
	    _bitsums[(x >> 8) & 0xFF] + _bitsums[x & 0xFF]);
}

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
    unsigned int **pointers[512];
};

static struct intset *intset_init(void)
{
    struct intset *is;
    is = malloc(sizeof(struct intset));
    if (is == NULL) {
	problem = "Out of memory";
	return NULL;
    }
    bzero(is->pointers, 512 * sizeof(unsigned int**));
    return is;
}

/*
 * We can use this function to figure out how much space to malloc for
 * a Numeric array.
 */
static int _intset_size(struct intset *is)
{
    unsigned int x0, x1, x2, sum;
    if (is == NULL) return -1;
    sum = 0;
    for (x0 = 0; x0 < 512; x0++) {
	if (is->pointers[x0] != NULL) {
	    for (x1 = 0; x1 < 512; x1++) {
		if ((is->pointers[x0])[x1] != NULL) {
		    for (x2 = 0; x2 < 512; x2++) {
			sum += sum_of_bits(((is->pointers[x0])[x1])[x2]);
		    }
		}
	    }
	}
    }
    return sum;
}

static PyObject *intset_size(struct intset *is)
{
    unsigned int x = _intset_size(is);
    if (x < 0) goto fail;
    return Py_BuildValue("i", x);
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static int _intset_contains(struct intset *is, int x)
{
    unsigned int x0, x1, x2, x3, **block2, *block;
    if (is == NULL) return -1;
    x0 = (x >> 23) & 0x1FF;
    block2 = is->pointers[x0];
    if (block2 == NULL) return 0;
    x1 = (x >> 14) & 0x1FF;
    block = block2[x1];
    if (block == NULL) return 0;
    x2 = (x >> 5) & 0x1FF;
    x3 = x & 0x1F;
    if ((block[x2] & (1 << x3)) == 0) return 0;
    return 1;
}

static PyObject *intset_contains(struct intset *is, int x)
{
    int r = _intset_contains(is, x);
    switch (r) {
    case 1:
	Py_INCREF(Py_True);
	return Py_True;
    case 0:
	Py_INCREF(Py_False);
	return Py_False;
    case -1:
    default:
	PyErr_SetString(PyExc_RuntimeError, "ouch");
	return NULL;
    }
}

static double intset_contains_performance_test(struct intset *is, int lim)
{
    volatile int dummy;  // avoid optimization
    int i;
    startingTime = now();
    for (i = 0; i < lim; i++) {
	dummy = _intset_contains(is, i);
    }
    return (now() - startingTime) / lim;
}

static PyObject *intset_asarray(struct intset *is)
{
    unsigned int x0, x1, x2, x3, size;
    unsigned int *data, *p;
    PyArrayObject *retval;
    if (is == NULL) goto fail;
    size = _intset_size(is);
    if (size < 0) goto fail;
    import_array();
    retval = (PyArrayObject *)
	PyArray_FromDims(1, (int*)&size, PyArray_UINT);
    data = p = (unsigned int*) retval->data;
    for (x0 = 0; x0 < 512; x0++) {
	if (is->pointers[x0] != NULL) {
	    for (x1 = 0; x1 < 512; x1++) {
		if ((is->pointers[x0])[x1] != NULL) {
		    unsigned int k = (x0 << 23) | (x1 << 14);
		    for (x2 = 0; x2 < 512; x2++) {
			unsigned int z = ((is->pointers[x0])[x1])[x2];
			for (x3 = 0; x3 < 32; x3++) {
			    if ((z & (1 << x3)) != 0) {
				*p++ = k;
			    }
			    k++;
			}
		    }
		}
	    }
	}
    }
    /* If I've figured this out right, then p should be exactly at
     * the end of data.
     */
    if (((int) (p - data)) != size) {
	PyErr_SetString(PyExc_RuntimeError, "array size mismatch");
	return NULL;
    }
    return PyArray_Return(retval);
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static PyObject *intset_remove(struct intset *is, int x)
{
    unsigned int x0, x1, x2, x3;
    unsigned int **block2, *block;
    if (is == NULL) goto fail;
    x0 = (x >> 23) & 0x1FF;
    block2 = is->pointers[x0];
    if (block2 == NULL) goto done;
    x1 = (x >> 14) & 0x1FF;
    block = block2[x1];
    if (block == NULL) goto done;
    x2 = (x >> 5) & 0x1FF;
    x3 = x & 0x1F;
    block[x2] &= ~(1 << x3);
 done:
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static int _intset_add(struct intset *is, int x)
{
    unsigned int x0, x1, x2, x3;
    unsigned int **block2, *block;
    if (is == NULL) goto fail;
    x0 = (x >> 23) & 0x1FF;
    block2 = is->pointers[x0];
    if (block2 == NULL) {
	block2 = is->pointers[x0] =
	    (unsigned int**) malloc(512 * sizeof(unsigned int*));
	if (block2 == NULL) goto fail;
	bzero(block2, 512 * sizeof(unsigned int*));
    }
    x1 = (x >> 14) & 0x1FF;
    block = block2[x1];
    if (block == NULL) {
	block = block2[x1] =
	    (unsigned int*) malloc(512 * sizeof(unsigned int));
	if (block == NULL) goto fail;
	bzero(block, 512 * sizeof(unsigned int));
    }
    x2 = (x >> 5) & 0x1FF;
    x3 = x & 0x1F;
    block[x2] |= 1 << x3;
    return 0;
 fail:
    return -1;
}

static PyObject *intset_add(struct intset *is, int x)
{
    if (_intset_add(is, x) != 0) goto fail;
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static PyObject *intset_fromList(struct intset *is, PyObject *lst)
{
    unsigned int i, n;
    if (!PyList_Check(lst)) goto fail;
    n = PyList_Size(lst);
    for (i = 0; i < n; i++) {
	PyObject *z = PyList_GetItem(lst, i);
	if (!PyInt_Check(z)) goto fail;
	if (_intset_add(is, PyInt_AsLong(z)) != 0) goto fail;
    }
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static PyObject *intset_addRange(struct intset *is, int m, int n)
{
    unsigned int x;
    for (x = m; x < n; x++)
	if (_intset_add(is, x) != 0)
	    goto fail;
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static double intset_addRangePerformance(struct intset *is, int n)
{
    startingTime = now();
    intset_addRange(is, 0, n);
    return (now() - startingTime) / n;
}

static PyObject *intset_del(struct intset *is)
{
    int i, j;
    if (is == NULL) goto fail;
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
    return ab;
}

void atombase_del(struct atombase* ab)
{
    // nothing to do yet
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
    return cb;
}

void chunkbase_del(struct chunkbase *cb)
{
    if (cb && cb->positions)
	free(cb->positions);
}

PyObject *chunkbase_addatom(struct chunkbase *cb, struct atombase *ab,
			    int atomtype,
			    double x, double y, double z)
{
    if (cb == NULL) goto fail;
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
