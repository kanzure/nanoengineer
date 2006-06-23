/* Copyright (c) 2006 Nanorex, Inc. All rights reserved. */
// gcc -I/usr/include/python2.4 -c -Wall atombasehelp.c 

#include "Python.h"
#include "Numeric/arrayobject.h"

//#define DEBUG

#ifdef DEBUG
#define XX(z)   z
#define MARK()  printf("%s:%d\n", __FUNCTION__, __LINE__)
#define HEX(x)  printf("%s:%d %s=%p\n", __FUNCTION__, __LINE__, #x, x)
#define INT(x)  printf("%s:%d %s=%u\n", __FUNCTION__, __LINE__, #x, x)
#define DBL(x)  printf("%s:%d %s=%le\n", __FUNCTION__, __LINE__, #x, x)
#define STR(x)  printf("%s:%d %s\n", __FUNCTION__, __LINE__, x)
#else
#define XX(z)
#define MARK()
#define HEX(x)
#define INT(x)
#define DBL(x)
#define STR(x)
#endif

/*
 * There is a kind of polymorphism available with structs, as long as the
 * first few fields are identical. In this case, the only commonality is
 * the "key" field.
 */
/* the "base class" */
struct key_thing {
    int key;
    PyObject *self;
};

/*
 * Linked lists are used for bonds, and also to track which
 * sets this atom is a member of.
 */
struct pointerlist {
    int size;
    struct key_thing **lst;
};

struct xyz {
    double x, y, z;
};

struct atomstruct {
    int key;
    PyObject *self;
    int _eltnum, _atomtype;
    struct xyz _posn;
    struct pointerlist *sets;

    /* This stuff comes from sim/src/part.h. There are redundancies. The
     * information in _eltnum and _atomtype is probably equivalent to the
     * information in type and hybridization, but EricM has one record-keeping
     * scheme and Bruce has another.
     */
    /* struct atomType * */ void *type;
    /* enum hybridization */ int hybridization;
  
    struct atom **vdwBucket;
    struct atom *vdwPrev;
    struct atom *vdwNext;
    double inverseMass;
    
    // non-zero if this atom is in any ground jigs
    int isGrounded;
    
    int index;
    int atomID;
    int num_bonds;
    /* struct bond ** */ void *bonds;
};

struct bondstruct {
    int key;
    PyObject *self;
    unsigned int atomkey1, atomkey2;
    int v6;
    struct pointerlist *sets;
};

struct setstruct {
    int key;
    PyObject *self;
    struct pointerlist *members;
};

static void print_pointerlist(struct pointerlist *L)
{
    int i;
    printf("POINTERLIST <<\n");
    for (i = 0; i < L->size; i++)
	if (L->lst[i] == NULL) {
	    printf("Entry %d, entry is NULL\n", i);
	} else {
	    printf("Entry %d, entry = %p, key = %d\n",
		   i, L->lst[i], L->lst[i]->key);
	}
    printf(">> POINTERLIST\n");
}

static struct pointerlist *new_pointerlist(void)
{
    struct pointerlist *p = (struct pointerlist *) malloc(sizeof(struct pointerlist));
    p->size = 0;
    p->lst = NULL;
    return p;
}

static struct key_thing *has_key(struct pointerlist *n, unsigned int key)
{
    int i;
    for (i = 0; i < n->size; i++) {
	if (n->lst[i]->key == key)
	    return n->lst[i];
    }
    return NULL;
}

PyObject * add_to_pointerlist(struct pointerlist *n, struct key_thing *other)
{
    HEX(other);
    INT(other->key);
    HEX(other->self);
    XX(print_pointerlist(n));
    if (other == NULL) {
	PyErr_SetString(PyExc_RuntimeError,
			"add_to_pointerlist: second arg is NULL");
	return NULL;
    }
    if (other->key == 0) {

	printf("BADNESS: ");
	PyObject_Print(other->self, stdout, 0);
	printf("\n");

	PyErr_SetString(PyExc_RuntimeError,
			"add_to_pointerlist: key is zero");
	return NULL;
    }
    if (has_key(n, other->key) == NULL) {
	n->size++;
	n->lst = (struct key_thing **) realloc(n->lst, n->size * sizeof(struct key_thing *));
	n->lst[n->size-1] = other;
	Py_INCREF(other->self);
    }
    XX(print_pointerlist(n));
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *remove_from_pointerlist(struct pointerlist *head, struct key_thing *other)
{
    int i, j;
    struct key_thing **tmp, **tmp2;
    XX(printf("\n"));
    HEX(other);
    INT(other->key);
    XX(print_pointerlist(head));
    if (head == NULL) {
	PyErr_SetString(PyExc_RuntimeError,
			"remove_from_pointerlist: empty list");
	return NULL;
    }
    if (has_key(head, other->key) == NULL) {
	PyErr_SetString(PyExc_RuntimeError,
			"remove_from_pointerlist: no such entry");
	return NULL;
    }
    tmp = (struct key_thing **) malloc((head->size - 1) * sizeof(void*));
    i = j = 0;
    while (i < head->size) {
	if (other->key != head->lst[i]->key) {
	    tmp[j++] = head->lst[i++];
	} else {
	    i++;
	}
    }
    if (j != i - 1) {
	PyErr_SetString(PyExc_RuntimeError,
			"remove size mismatch");
	return NULL;
    }
    tmp2 = head->lst;
    head->lst = tmp;
    head->size--;
    free(tmp2);
    MARK();
    XX(print_pointerlist(head));
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *pointerlist_lookup(struct pointerlist *root, unsigned int key)
{
    struct key_thing *r = has_key(root, key);
    if (r == NULL) {
	PyErr_SetString(PyExc_KeyError,
			"pointerlist_lookup: no such key");
	return NULL;
    }
    Py_INCREF(r->self);
    return r->self;
}

/* -------------------------------------------------------------------- */

static unsigned int qsort_partition(struct key_thing **y, unsigned int f, unsigned int l)
{
    unsigned int up, down;
    struct key_thing *piv = y[f];
    up = f;
    down = l;
    do { 
        while (y[up]->key <= piv->key && up < l) {
            up++;
        }
        while (y[down]->key > piv->key) {
            down--;
        }
        if (up < down) {
	    struct key_thing *temp;
            temp = y[up];
            y[up] = y[down];
            y[down] = temp;
        }
    } while (down > up);
    y[f] = y[down];
    y[down] = piv;
    return down;
}

static void quicksort(struct key_thing **x, unsigned int first, unsigned int last)
{
    if (first < last) {
        unsigned int pivIndex = qsort_partition(x, first, last);
        if (pivIndex > 0)
	    quicksort(x, first, pivIndex-1);
	quicksort(x, pivIndex+1, last);
    }
}

#if 0
static void idiotsort(struct key_thing **x, unsigned int first, unsigned int last)
{
    int i;
    if (first >= last)
	return;
    for (i = first; i < last; i++) {
	if (x[i]->key > x[last]->key) {
	    struct key_thing *tmp = x[last];
	    x[last] = x[i];
	    x[i] = tmp;
	}
    }
    idiotsort(x, first, last - 1);
}
#endif

static PyObject *extract_list(struct pointerlist *root, int values)
{
    PyObject *retval;
    int i;
    unsigned int *kdata;
    import_array();
    MARK();
    XX(print_pointerlist(root));
    if (root->size > 0) {
	quicksort(root->lst, 0, root->size-1);
    }
    if (values) {
	retval = PyList_New(0);
	for (i = 0; i < root->size; i++) {
	    PyList_Append(retval, root->lst[i]->self);
	    //PyObject_Print(root->lst[i]->self, stdout, 0);
	    //printf("\n");
	}
	return retval;
    }
    retval = PyArray_FromDims(1, (int*)&(root->size), PyArray_INT);
    kdata = (unsigned int *) ((PyArrayObject*) retval)->data;
    for (i = 0; i < root->size; i++) {
	kdata[i] = root->lst[i]->key;
    }
    return PyArray_Return((PyArrayObject*) retval);
}


/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
