// gcc -I/usr/include/python2.4 -c -Wall atombasehelp.c 

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

/*
 * Linked lists are used for bonds, and also to track which
 * sets this atom is a member of.
 */
struct link {
    struct link *next;  // 4 bytes
    struct key_thing *other;  // 4 bytes
};

/*
 * There is a kind of polymorphism available with structs, as long as the
 * first few fields are identical. In this case, the only commonality is
 * the "key" field.
 */
struct atomstruct {
    int _eltnum, _atomtype;
    double x, y, z;
    struct link *sets;
};

/* the "base class" */
struct key_thing {
    int key;
    PyObject *self;
};

struct bondstruct {
    int v6;
};

struct atomsetstruct {
    struct link *atoms;
};

static void print_linked_list(struct link *L)
{
    int i, indent;
    indent = 1;
    fprintf(stderr, "LINKED LIST <<\n");
    while (L != NULL) {
	for (i = 0; i < indent; i++)
	    fprintf(stderr, "    ");
#if 0
	PyObject_Print((PyObject*) L->other->self, stderr, 0);
	fprintf(stderr, "\n");
#else
	fprintf(stderr, "L = %p, L->other = %p, L->other->key = %d, L->next = %p\n",
		L, L->other, L->other->key, L->next);
#endif
	L = L->next;
	indent++;
    }
    fprintf(stderr, ">> LINKED LIST\n");
}

static struct link *has_link(struct link *n, unsigned int key)
{
    while (1) {
	if (n == NULL) return NULL;
	if (n->other->key == key) return n;
	n = n->next;
    }
}

static PyObject *add_to_linked_list(struct link **head, struct key_thing *other)
{
    struct link *n;
    XX(fprintf(stderr, "\n"));
    HEX(other);
    INT(other->key);
    XX(print_linked_list(*head));
    if (has_link(*head, other->key) != NULL) {
	PyErr_SetString(PyExc_RuntimeError,
			"add_to_linked_list: already have this entry");
	return NULL;
    }
    n = (struct link *) malloc(sizeof(struct link));
    n->next = *head;
    HEX(n->next);
    *head = n;
    Py_INCREF(other->self);
    n->other = other;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *remove_from_linked_list(struct link **head, struct key_thing *other)
{
    struct link *prev, *here;
    XX(fprintf(stderr, "\n"));
    HEX(other);
    INT(other->key);
    XX(print_linked_list(*head));
    if (*head == NULL) {
	PyErr_SetString(PyExc_RuntimeError,
			"remove_from_linked_list: empty list");
	return NULL;
    }
    if (has_link(*head, other->key) == NULL) {
	PyErr_SetString(PyExc_RuntimeError,
			"remove_from_linked_list: no such entry");
	return NULL;
    }
    here = *head;
    if (here->other->key == other->key) {
#if 0
	PyErr_SetString(PyExc_RuntimeError,
			"remove_from_linked_list: Segfault happens here");
	return NULL;
#endif
	//Py_DECREF(here->other->self);
	*head = here->next;
	free(here);
	goto fini;
    }
    while (here->other->key != other->key) {
	prev = here;
	here = here->next;
    }
    prev->next = here->next;
    HEX(prev->next);
    //Py_DECREF(here->other->self);
    free(here);
 fini:
    MARK();
    XX(print_linked_list(*head));
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *linked_list_lookup(struct link *root, unsigned int key)
{
    root = has_link(root, key);
    if (root == NULL) {
	PyErr_SetString(PyExc_KeyError,
			"linked_list_lookup: no such key");
	return NULL;
    }
    Py_INCREF(root->other->self);
    return root->other->self;
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

static PyObject *extract_list(struct link *root, int values)
{
    struct link *n;
    PyObject *retval;
    unsigned int i, size=0;
    struct key_thing **data;
    unsigned int *kdata;
    import_array();
    MARK();
    XX(print_linked_list(root));
    for (size = 0, n = root; n != NULL; n = n->next) {
	size++;
    }
    data = (struct key_thing **)
	malloc(size * sizeof(struct key_thing *));
    if (data == NULL) {
	PyErr_SetString(PyExc_MemoryError,
			"extract_list");
	return NULL;
    }
    for (i = 0, n = root; i < size; i++, n = n->next) {
	data[i] = n->other;
    }
    if (size > 0) {
	quicksort(data, 0, size-1);
    }
    if (values) {
	retval = PyList_New(0);
	for (i = 0; i < size; i++) {
	    PyList_Append(retval, data[i]->self);
	    //PyObject_Print(n->other->self, stderr, 0);
	    //fprintf(stderr, "\n");
	}
	return retval;
    }
    retval = PyArray_FromDims(1, (int*)&size, PyArray_INT);
    kdata = (unsigned int *) ((PyArrayObject*) retval)->data;
    for (i = 0; i < size; i++) {
	kdata[i] = data[i]->key;
    }
    return PyArray_Return((PyArrayObject*) retval);
}



/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
