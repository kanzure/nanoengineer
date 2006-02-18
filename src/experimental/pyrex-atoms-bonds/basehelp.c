#include "Python.h"
#include "Numeric/arrayobject.h"

//#define DEBUG

#ifdef DEBUG
#define XX(z)   z
#define MARK()  fprintf(stderr, "%s:%d\n", __FUNCTION__, __LINE__)
#define HEX(x)  fprintf(stderr, "%s:%d %s=%p\n", __FUNCTION__, __LINE__, #x, x)
#define INT(x)  fprintf(stderr, "%s:%d %s=%u\n", __FUNCTION__, __LINE__, #x, x)
#define DBL(x)  fprintf(stderr, "%s:%d %s=%le\n", __FUNCTION__, __LINE__, #x, x)
#define STR(x)  fprintf(stderr, "%s:%d %s\n", __FUNCTION__, __LINE__, x)
#else
#define XX(z)
#define MARK()
#define HEX(x)
#define INT(x)
#define DBL(x)
#define STR(x)
#endif

#define FREE(x)       MARK(); free(x)
#define PYDECREF(x)   MARK(); Py_DECREF(x)
#define PYXDECREF(x)  MARK(); Py_XDECREF(x)

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

/****************************************************************
 * Set is an integer set which can be used for selections    *
 * and similar things.                                          *
 ****************************************************************/

struct set {
    void **root;
    int population;
};

/* Possible values for SUBKEYSIZE are 2, 4, 8.
 * Corresponding memory overheads for very small lists are
 * 256 bytes, 512 bytes, and 4096 bytes. Longer subkeys will
 * give quicker searches.
 */

// #define SUBKEYSIZE  2
// #define SUBKEYSIZE  4
#define SUBKEYSIZE  8
// #define SUBKEYSIZE  16
#define NUMENTRIES  (1 << SUBKEYSIZE)
#define SUBTABLESIZE  (NUMENTRIES * sizeof(void *))
#define SUBKEYMASK  (NUMENTRIES - 1)
#define NUMLAYERS   (32 / SUBKEYSIZE)
#define HIGHBITS(x)  (((x) >> (32 - SUBKEYSIZE)) & SUBKEYMASK)

static void _atomset_print_help(void **root, int indent)
{
    int i, j;
    if (indent == NUMLAYERS + 1)
	return;
    for (j = 0; j < indent; j++)
	printf("    ");
    printf("%p\n", root);
    if (root != NULL)
	for (i = 0; i < NUMENTRIES; i++)
	    _atomset_print_help(root[i], indent + 1);
}
static inline void _atomset_print(struct set *ss)
{
#ifdef DEBUG
    _atomset_print_help(ss->root, 0);
#endif
}

/*
 * the first argument is a pointer to root
 * root is a pointer to the head of a table
 * the n-th entry in the table is the next pointer
 * each iteration takes us from a pointer to root to
 * a pointer to root[n]
 */
static void **_findkey(struct set *ss, unsigned int key, int grow)
{
    int i;
    void ***p = &(ss->root);
    for (i = 0; i < NUMLAYERS; i++) {
	if (*p == NULL) {
	    if (!grow) return NULL;
	    *p = (void**) malloc(SUBTABLESIZE);
	    bzero(*p, SUBTABLESIZE);
	    if (p == NULL) {
		perror("out of memory");
		exit(1);
	    }
	}
	/* now we know p != NULL */
	int r = (key >> (32 - SUBKEYSIZE)) & SUBKEYMASK;
	p = (void***) &((*p)[r]);
	key <<= SUBKEYSIZE;
    }
    return (void**) p;
}

struct set *atomset_init(void)
{
    struct set *ss;
    ss = malloc(sizeof(struct set));
    if (ss == NULL) {
	PyErr_SetString(PyExc_MemoryError, "out of memory");
	return NULL;
    }
    ss->root = (void**) malloc(NUMENTRIES * sizeof(void*));
    if (ss->root == NULL) {
	FREE(ss);
	PyErr_SetString(PyExc_MemoryError, "out of memory");
	return NULL;
    }
    bzero(ss->root, NUMENTRIES * sizeof(void*));
    ss->population = 0;
    return ss;
}

static PyObject *atomset_size(struct set *ss)
{
    return Py_BuildValue("i", ss->population);
}

static void _atomset_cleanup(void **root, int layers)
{
    int i;
    if (layers == 0) {
	for (i = 0; i < NUMENTRIES; i++) {
	    PyObject *p = (PyObject *) root[i];
	    PYXDECREF(p);
	}
    } else {
	for (i = 0; i < NUMENTRIES; i++)
	    if (root[i] != NULL) {
		_atomset_cleanup((void**) root[i], layers - 1);
		FREE(root[i]);
	    }
    }
}

static void atomset_del(struct set *ss)
{
    _atomset_cleanup(ss->root, NUMLAYERS-1);
    FREE(ss->root);
}

static int _atomset_set(struct set *ss, unsigned int key, PyObject *obj)
{
    void **p = _findkey(ss, key, 1);
    if (p != NULL) {
	if (*p != NULL) {
	    PYDECREF((PyObject *) *p);
	    ss->population--;
	}
	Py_INCREF(obj);
	*((PyObject**) p) = obj;
	ss->population++;
	return 0;
    }
    return 1;
}

static PyObject *atomset_set(struct set *ss, unsigned int key, PyObject *obj)
{
    if (_atomset_set(ss, key, obj) != 0) {
	PyErr_SetString(PyExc_MemoryError, "out of memory");
	return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static void atomset_quickfill(struct set *ss, int n, int div, int pynone) {
    unsigned int x;
    if (pynone)
	for (x = 0; x < n; x++) {
	    _atomset_set(ss, x * div, Py_None);
	}
    else
	for (x = 0; x < n; x++) {
	    _atomset_set(ss, x * div, Py_BuildValue("i", x));
	}
}

static double atomset_set_performance(struct set *ss, int n)
{
    double t = now();
    atomset_quickfill(ss, n, 1, 1);
    return 1.0e9 * (now() - t) / n;
}


static void _atomset_remove(struct set *ss, unsigned int key)
{
    void **p = _findkey(ss, key, 0);
    if (p != NULL && *p != NULL) {
	PYDECREF((PyObject*) *p);
	ss->population--;
	*p = NULL;
    }
}

static PyObject *atomset_remove(struct set *ss, unsigned int key)
{
    _atomset_remove(ss, key);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *atomset_get(struct set *ss, unsigned int key)
{
    void **p = _findkey(ss, key, 0);
    if (p == NULL || *p == NULL) {
	Py_INCREF(Py_None);
	return Py_None;
    }
    PyObject *po = (PyObject *) *p;
    Py_INCREF(po);
    return po;
}

static int _atomset_contains(struct set *ss, unsigned int key)
{
    void **p = _findkey(ss, key, 0);
    return p != NULL && *p != NULL;
}

static PyObject *atomset_contains(struct set *ss, unsigned int key)
{
    return Py_BuildValue("i", _atomset_contains(ss, key));
}

static double atomset_contains_performance(struct set *ss, int n)
{
    int i;
    double t;
    for (i = 0; i < n; i++) {
	_atomset_set(ss, i, Py_None);
    }
    t = now();
    for (i = 0; i < n; i++) {
	_atomset_contains(ss, i);
    }
    return 1.0e9 * (now() - t) / n;
}

#if 0
static PyObject *atomset_asarray(struct set *ss)
{
    PyArrayObject *retval;
    unsigned int i, j, *data;
    import_array();
    retval = (PyArrayObject *)
	PyArray_FromDims(1, (int*)&ss->population, PyArray_UINT);
    data = (unsigned int *) retval->data;
    for (i = j = 0; i < ss->population; i++)
	if (_atomset_contains(ss, i)) {
	    data[j++] = i;
	}
    return PyArray_Return(retval);
}
#endif

static void _atomset_asarray_helper(unsigned int **dst, unsigned int *src,
				    int depth, unsigned int *count)
{
    int i;
    for (i = 0; i < NUMENTRIES; i++) {
	if (src[i] != 0) {
	    if (depth == 0) {
		*(*dst) = *count;
		(*dst)++;
		(*count)++;
	    } else
		_atomset_asarray_helper(dst, (unsigned int*) src[i],
					depth - 1, count);
	}
    }
}

static PyObject *atomset_asarray(struct set *ss)
{
    PyArrayObject *retval;
    unsigned int count = 0, *data;
    import_array(); /* NECESSARY */
    retval = (PyArrayObject *)
	PyArray_FromDims(1, (int*)&ss->population, PyArray_UINT);
    data = (unsigned int *) retval->data;
    _atomset_asarray_helper(&data, (unsigned int*) ss->root,
			    NUMLAYERS-1, &count);
    if (count != ss->population) {
	PyErr_SetString(PyExc_RuntimeError, "array size mismatch");
	return NULL;
    }
    return PyArray_Return(retval);
}

static double atomset_asarray_performance(struct set *ss, int n)
{
    PyObject *r;
    double time1, time2;
    time1 = now();
    r = atomset_asarray(ss);
    time2 = now();
    PYDECREF(r);
    return 1.0e9 * (time2 - time1) / n;
}

/*
 * AtomBase
 */

#define MAX_NUM_NEIGHBORS 12  // ask Damian for the real number

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
	PyErr_SetString(PyExc_MemoryError, "out of memory");
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
	PyErr_SetString(PyExc_MemoryError, "out of memory");
	return NULL;
    }
    cb->arraysize = 1000;
    cb->positions = malloc(cb->arraysize * sizeof(struct position));
    if (cb->positions == NULL) {
	PyErr_SetString(PyExc_MemoryError, "out of memory");
	return NULL;
    }
    cb->numatoms = 0;
    return cb;
}

void chunkbase_del(struct chunkbase *cb)
{
    if (cb && cb->positions) {
	FREE(cb->positions);
    }
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
