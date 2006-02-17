#include "Python.h"
#include "Numeric/arrayobject.h"

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

/****************************************************************
 * Set is an integer set which can be used for selections    *
 * and similar things.                                          *
 ****************************************************************/

/* (3 + 128) * 4 = 524 bytes */
struct node {
    struct node *next;
    int prefix;
    unsigned int data[128];
};

/* 3 * 4 = 12 bytes */
struct set {
    struct node *root;
    unsigned int population;
    int prevPrefix;
};

#if 0
static void intset_print(struct set *ss)
{
    struct node *r;
    fprintf(stderr, "---- Begin Set %p ----\n", ss);
    fprintf(stderr, "Population=%u, prevPrefix=%d\n", ss->population, ss->prevPrefix);
    r = ss->root;
    while (r != NULL) {
	int i, j, sum;
	fprintf(stderr, "Node %p, prefix=%d ", r, r->prefix);
	fprintf(stderr, "previous=%p, next=%p ", r->previous, r->next);
	sum = 0;
	for (i = 0; i < 128; i++)
	    for (j = 0; j < 32; j++)
		if ((r->data[i] & (1 << j)) != 0)
		    sum++;
	fprintf(stderr, "bits=%d\n", sum);
	r = r->next;
    }
    fprintf(stderr, "---- End Set %p ----\n", ss);
}
#endif

static struct set *intset_init(void)
{
    struct set *ss;
    ss = (struct set *) malloc(sizeof(struct set));
    if (ss == NULL) {
	problem = "Out of memory";
	return NULL;
    }
    bzero(ss, sizeof(struct set));
    return ss;
}

static struct node *_alloc_node(void)
{
    struct node *nd;
    nd = (struct node*) malloc(sizeof(struct node));
    if (nd == NULL) {
	problem = "Out of memory";
	return NULL;
    }
    bzero(nd, sizeof(struct node));
    return nd;
}

static struct node *_find_node_with_prefix(struct set *ss,
					   int prefix)
{
    struct node *A, *B = ss->root;
    A = NULL;
    while (1) {
	if (B == NULL) return NULL;
	if (B->prefix == prefix) {
	    if (ss->prevPrefix != prefix) {
		ss->prevPrefix = prefix;
	    } else if (A != NULL) {
		A->next = B->next;
		B->next = ss->root;
		ss->root = B;
	    }
	    return B;
	}
	A = B;
	B = B->next;
    }
}

static inline unsigned int *
getword(struct set *ss, int x, int grow, int *bit)
{
    int x0, x1, x2;
    struct node *C;
    if (ss == NULL) return NULL;
    x0 = (x >> 12) & 0xFFFFF;
    C = _find_node_with_prefix(ss, x0);
    if (grow && C == NULL) {
	C = _alloc_node();
	C->prefix = x0;
	C->next = ss->root;
	ss->root = C;
    }
    if (C == NULL)
	return NULL;
    /* Set the bit in C's data */
    x1 = (x >> 5) & 0x7F;
    x2 = x & 0x1F;
    *bit = 1 << x2;
    return &C->data[x1];
}

static int _intset_add(struct set *ss, int x)
{
    unsigned int *z;
    int bit;
    z = getword(ss, x, 1, &bit);
    if (z == NULL) return -1;
    if ((*z & bit) == 0) {
	*z |= bit;
	ss->population++;
    }
    return 0;
}

static PyObject *intset_add(struct set *ss, int x)
{
    if (_intset_add(ss, x) != 0) goto fail;
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static PyObject *intset_remove(struct set *ss, int x)
{
    unsigned int *z;
    int bit;
    z = getword(ss, x, 0, &bit);
    if (z != NULL && (*z & bit) != 0) {
	*z &= ~bit;
	ss->population--;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *intset_size(struct set *ss)
{
    if (ss == NULL) goto fail;
    return Py_BuildValue("i", ss->population);
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static int _intset_contains(struct set *ss, int x)
{
    unsigned int *z;
    int bit;
    z = getword(ss, x, 1, &bit);
    if (z == NULL) return 0;
    return (*z & bit) != 0;
}

static PyObject *intset_contains(struct set *ss, int x)
{
    return Py_BuildValue("i", _intset_contains(ss, x));
}

static double intset_contains_performance_test(struct set *ss, int n)
{
    int i;
    double t;
    t = now();
    for (i = 0; i < n; i++) {
	_intset_contains(ss, i);
    }
    return 1.0e9 * (now() - t) / n;
}

static int _partition(struct node *y[], int f, int l) {
    int up,down;
    struct node *temp;
    struct node *piv = y[f];
    up = f;
    down = l;
    do { 
        while (y[up]->prefix <= piv->prefix && up < l) {
            up++;
        }
        while (y[down]->prefix > piv->prefix) {
            down--;
        }
        if (up < down ) {
            temp = y[up];
            y[up] = y[down];
            y[down] = temp;
        }
    } while (down > up);
    y[f] = y[down];
    y[down] = piv;
    return down;
}

static void _quicksort(struct node *x[], int first, int last) {
    int pivIndex = 0;
    if(first < last) {
        pivIndex = _partition(x,first, last);
        _quicksort(x,first,(pivIndex-1));
        _quicksort(x,(pivIndex+1),last);
    }
}

static PyObject *intset_asarray(struct set *ss)
{
    int i, size;
    struct node *nd, **nodelist;
    unsigned int *data, *p;
    PyArrayObject *retval;
    if (ss == NULL) goto fail;
    import_array(); /* VERY NECESSARY */
    retval = (PyArrayObject *)
	PyArray_FromDims(1, (int*)&ss->population, PyArray_UINT);
    data = p = (unsigned int*) retval->data;
    for (nd = ss->root, size = 0; nd != NULL; nd = nd->next, size++);
    nodelist = (struct node **)
	malloc(size * sizeof(struct node *));
    if (nodelist == NULL) goto fail;
    for (nd = ss->root, i = 0; i < size; nd = nd->next, i++) {
	if (nd == NULL) goto fail;
	nodelist[i] = nd;
    }
    _quicksort(nodelist, 0, size - 1);
    for (i = 0; i < size; i++) {
	int M, j, k;
	nd = nodelist[i];
	M = nd->prefix << 12;
	for (j = 0; j < 128; j++) {
	    unsigned int w = nd->data[j];
	    for (k = 0; k < 32; k++) {
		if ((w & (1 << k)) != 0) {
		    *p++ = M + k;
		}
	    }
	    M += 32;
	}
    }
    /* If I've figured this out right, then p should be exactly at
     * the end of data.
     */
    if (((int) (p - data)) != ss->population) {
	PyErr_SetString(PyExc_RuntimeError, "array size mismatch");
	return NULL;
    }
    return PyArray_Return(retval);
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static double intset_asarray_performance_test(struct set *ss, int n)
{
    PyObject *r;
    double time1, time2;
    time1 = now();
    r = intset_asarray(ss);
    time2 = now();
    Py_DECREF(r);
    return 1.0e9 * (time2 - time1) / n;
}

static PyObject *intset_fromList(struct set *ss, PyObject *lst)
{
    unsigned int i, n;
    if (!PyList_Check(lst)) goto fail;
    n = PyList_Size(lst);
    for (i = 0; i < n; i++) {
	PyObject *z = PyList_GetItem(lst, i);
	if (!PyInt_Check(z)) goto fail;
	if (_intset_add(ss, PyInt_AsLong(z)) != 0) goto fail;
    }
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static PyObject *intset_addRange(struct set *ss, int m, int n)
{
    unsigned int x;
    for (x = m; x < n; x++)
	if (_intset_add(ss, x) != 0)
	    goto fail;
    Py_INCREF(Py_None);
    return Py_None;
 fail:
    PyErr_SetString(PyExc_RuntimeError, "ouch");
    return NULL;
}

static double intset_add_performance(struct set *ss, int n)
{
    unsigned int x;
    double t;
    t = now();
    for (x = 0; x < n; x++)
	_intset_add(ss, x);
    return 1.0e9 * (now() - t) / n;
}

static PyObject *intset_del(struct set *ss)
{
    struct node *p, *q;
    if (ss == NULL) goto fail;
    p = ss->root;
    while (1) {
	if (p == NULL) break;
	q = p->next;
	free(p);
	p = q;
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
