#include "Numeric/arrayobject.h"

/*
 * You can think of this as like a "base class" for any C structure that
 * has a key. The key always comes first, so we can cast any pointer to
 * any such struct to a (struct key_thing *), and then access the key
 * while not necessarily knowing what the original thing was.
 */
struct key_thing {
    unsigned int key;
};

/*
 * Linked lists are used for bonds, and also to track which
 * sets this atom is a member of.
 */
struct link {
    struct link *next;  // 4 bytes
    struct key_thing *other;  // 4 bytes
    float order;   // 4 bytes?
};

struct atominfo {
    unsigned int key;  // 4 bytes
    short int _eltnum;  // 2 bytes
    short int _atomtype; // 2 bytes

    //double x, y, z;  // 12 bytes
    // double *array;   // 4 bytes
    unsigned int arrayIndex;  // 4 bytes

    struct link *bonds;  // 4 bytes
    struct link *sets;  // 4 bytes
};

static unsigned int qsort_partition(unsigned int y[], int f, int l) {
    int up, down, temp;
    unsigned int piv = y[f];
    up = f;
    down = l;
    do { 
        while (y[up] <= piv && up < l) {
            up++;
        }
        while (y[down] > piv  ) {
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

static void quicksort(unsigned int x[], int first, int last)
{
    int pivIndex = 0;
    if (first < last) {
        pivIndex = qsort_partition(x, first, last);
        quicksort(x, first, pivIndex-1);
        quicksort(x, pivIndex+1, last);
    }
}

static PyObject *order_numeric_intarray(PyArrayObject *array)
{
    unsigned int size;
    unsigned int *data = (unsigned int *) array->data;
    if (array->nd != 1) {
	PyErr_SetString(PyExc_RuntimeError,
			"order_numeric_intarray: array must be 1-dimensional");
	return NULL;
    }
    size = array->dimensions[0];
    quicksort(data, 0, size-1);
    Py_INCREF(Py_None);
    return Py_None;
}

static int has_link(struct link *n, struct key_thing *other)
{
    if (other == NULL) return 0;
    while (1) {
	if (n == NULL) return 0;
	if (n->other->key == other->key) return 1;
	n = n->next;
    }
}

static PyObject *add_to_linked_list(struct link **head, struct key_thing *other, float order)
{
    struct link *n;
    if (has_link(*head, other)) {
	PyErr_SetString(PyExc_RuntimeError,
			"add_to_linked_list: already have this entry");
	return NULL;
    }
    n = (struct link *) malloc(sizeof(struct link));
    n->next = *head;
    *head = n;
    n->other = other;
    n->order = order;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *remove_from_linked_list(struct link **head, struct key_thing *other)
{
    struct link *n;
    if (!has_link(*head, other)) {
	PyErr_SetString(PyExc_RuntimeError,
			"remove_from_linked_list: no such entry");
	return NULL;
    }
    while ((*head)->other->key != other->key) {
	head = &((*head)->next);
    }
    n = *head;
    *head = (*head)->next;
    free(n);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *make_link_list(struct link *root, unsigned int key, int unique)
{
    struct link *n;
    PyArrayObject *retval;
    unsigned int i, size=0, *data;
    import_array();
    for (size = 0, n = root; n != NULL; n = n->next) {
	if (!unique || n->other->key > key) {
            size++;
	}
    }
    retval = (PyArrayObject *) PyArray_FromDims(1, (int*)&size, PyArray_INT);
    data = (unsigned int *) retval->data;
    for (i = 0, n = root; i < size; n = n->next) {
	if (!unique || n->other->key > key) {
            data[i++] = n->other->key;
	}
    }
    if (order_numeric_intarray(retval) == NULL)
	return NULL;
    return PyArray_Return(retval);
}



/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
