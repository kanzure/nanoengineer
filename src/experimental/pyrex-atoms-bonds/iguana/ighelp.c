/*
 * C code for the multithreaded Iguana virtual machine
 * Copyright (c) 2006 Nanorex, Inc. All rights reserved.
 */

#include "Python.h"
#include "ighelp.h"

#define DEBUG 0

#if DEBUG
#define MARK()  \
  fprintf(stderr, __FILE__ ":%d\n", __LINE__); fflush(stderr)
#define DBGPRINTF(fmt)  \
  fprintf(stderr, __FILE__ ":%d " fmt, __LINE__); fflush(stderr)
#define DBGPRINTF1(fmt,a)  \
  fprintf(stderr, __FILE__ ":%d " fmt, __LINE__, a); fflush(stderr)
#define DBGPRINTF2(fmt,a,b)  \
  fprintf(stderr, __FILE__ ":%d " fmt, __LINE__, a, b); fflush(stderr)
#define DBGPRINTF3(fmt,a,b,c)  \
  fprintf(stderr, __FILE__ ":%d " fmt, __LINE__, a, b, c); fflush(stderr)
#else
#define MARK()
#define DBGPRINTF(fmt)
#define DBGPRINTF1(fmt,a)
#define DBGPRINTF2(fmt,a,b)
#define DBGPRINTF3(fmt,a,b,c)
#endif

static unsigned int xrand, yrand, zrand;        /* steal from whrandom.py */
static iguana_thread_object root_thread;        /* never actually runs
                                                 * code, just the anchor
                                                 * for a doubly-linked
                                                 * list */
static int task_switch_enable = 1;
PyObject *IguanaError;
static void igthread_dealloc(iguana_thread_object * thr);
static PyObject *igthread_getattr(iguana_thread_object * a, char *name);
static int igthread_setattr(iguana_thread_object * self, char *name,
                            PyObject * v);
static int igverb_lit(iguana_thread_object * self, int pc);

#define EVILRETURN NULL

PyTypeObject iguana_thread_type = {
    PyObject_HEAD_INIT(&PyType_Type)
    0,
    "iguana_thread",
    sizeof(iguana_thread_object),
    0,
    (destructor) igthread_dealloc,      /* tp_dealloc */
    0,                          /* tp_print */
    (getattrfunc) igthread_getattr,     /* tp_getattr */
    (setattrfunc) igthread_setattr,     /* tp_setattr */
    0,                          /* tp_compare */
    0,                          /* tp_repr */
    0,                          /* tp_as_number */
    0,                          /* tp_as_sequence */
    0,                          /* tp_as_mapping */
    0,                          /* tp_hash */
};

#define IguanaThread_Check(op) ((op)->ob_type == &iguana_thread_type)

static PyObject *
new_iguana_thread(PyObject *self, PyObject *args)
{
    int stack_size = 100, i, n;
    PyObject *prog, *mem = NULL, *z;
    iguana_thread_object *thr, *prev, *next;
    if (!PyArg_ParseTuple(args, "OO|i", &prog, &mem, &stack_size))
        return NULL;
    if (mem == Py_None) {
        mem = NULL;
    }
    if (mem != NULL && mem->ob_type->tp_as_sequence == NULL) {
        PyErr_SetString(IguanaError,
                        "memory must be a subscriptable object");
        return NULL;
    }
    if (!PyList_Check(prog)) {
        PyErr_SetString(IguanaError, "Iguana programs must be lists");
        return NULL;
    }
    iguana_thread_type.ob_type = &PyType_Type;
    thr = PyObject_NEW(iguana_thread_object, &iguana_thread_type);
    thr->data_stack = malloc(stack_size * sizeof(double));
    if (thr->data_stack == NULL)
        return PyErr_NoMemory();
    thr->program_size = n = PyList_Size(prog);
    thr->program = (program_entry *) malloc(n * sizeof(program_entry));
    if (thr->program == NULL) {
        PyErr_SetString(PyExc_MemoryError, "out of memory");
        return NULL;
    }
    for (i = 0; i < n; i++) {
	int x;
	z = PyList_GetItem(prog, i);
	if (!PyInt_Check(z)) {
	    PyErr_SetString(PyExc_TypeError, "program entries should be ints");
	    return NULL;
	}
	thr->program[i].ival = x = PyInt_AsLong(z);
	if (x == (int) igverb_lit) {
	    i++;
	    z = PyList_GetItem(prog, i);
	    if (!PyFloat_Check(z)) {
		PyErr_SetString(PyExc_TypeError, "argument to LIT should be a float");
		return NULL;
	    }
	    thr->program[i].dval = PyFloat_AsDouble(z);
	}
    }

    Py_XINCREF(mem);
    thr->memory = mem;
    thr->program_counter = thr->finished = 0;
    thr->stacksize = stack_size;
    thr->dspointer = thr->rspointer = 0;
    /*
     * When we include a thread in the doubly-linked list of active
     * threads, we INCREF it. When the thread finishes, we DECREF it. 
     */
    prev = root_thread.prev;
    next = &root_thread;
    thr->next = &root_thread;
    thr->prev = prev;
    prev->next = thr;
    next->prev = thr;
    Py_INCREF(thr);
    return (PyObject *) thr;
}

static void
igthread_dealloc(iguana_thread_object * thr)
{
    Py_XDECREF(thr->memory);
    PyMem_DEL(thr->program);
    PyMem_DEL(thr->data_stack);
    PyMem_DEL(thr);
}

static char push_doc[] = "push (x)\n\
\n\
Push a float onto the data stack.";

static PyObject *
igthread_push(iguana_thread_object * self, PyObject * args)
{
    double x;
    if (!PyArg_ParseTuple(args, "d", &x))
        return NULL;
    CHECK_OVERFLOW(1);
    self->data_stack[self->dspointer] = x;
    self->dspointer++;
    Py_INCREF(Py_None);
    return Py_None;
}

static char pop_doc[] = "pop ()\n\
\n\
Pop a float from the data stack.";

static PyObject *
igthread_pop(iguana_thread_object * self, PyObject * args)
{
    if (!PyArg_ParseTuple(args, ""))
        return NULL;
    CHECK_UNDERFLOW(1);
    self->dspointer--;
    return PyFloat_FromDouble(self->data_stack[self->dspointer]);
}

static double
my_rand(void)
{
    double d;
    xrand = (171 * xrand) % 30269;
    yrand = (172 * yrand) % 30307;
    zrand = (170 * zrand) % 30323;
    d = xrand / 30269.0 + yrand / 30307.0 + zrand / 30323.0;
    while (d < 0.0)
        d += 1.0;
    while (d >= 1.0)
        d -= 1.0;
    return d;
}

/****************************************************/

PyObject *verb_dict;

#undef EVILRETURN
#define EVILRETURN -1

static int
igverb_rand(iguana_thread_object * self, int pc)
{
    CHECK_OVERFLOW(1);
    self->data_stack[self->dspointer] = my_rand();
    self->dspointer++;
    return pc;
}

static int
igverb_lit(iguana_thread_object * self, int pc)
{
    CHECK_OVERFLOW(1);
    if (pc > self->program_size - 2) {
        PyErr_SetString(IguanaError, "badly compiled program");
        return -1;
    }
    self->data_stack[self->dspointer] = self->program[pc].dval;
    self->dspointer++;
    return pc + 1;
}

static int
igverb_call(iguana_thread_object * self, int pc)
{
    if (self->rspointer > RETURN_STACK_SIZE - 1) {
        PyErr_SetString(IguanaError, "return stack overflow");
        return -1;
    }
    self->return_stack[self->rspointer] = pc + 1;
    self->rspointer++;
    return self->program[pc].ival;
}

static int
igverb_exit(iguana_thread_object * self, int pc)
{
    if (self->rspointer == 0) {
        PyErr_SetString(IguanaError, "thread finished");
        return -1;
    }
    self->rspointer--;
    return self->return_stack[self->rspointer];
}

static int
igverb_zjump(iguana_thread_object * self, int pc)
{
    CHECK_UNDERFLOW(1);
    self->dspointer--;
    if (self->data_stack[self->dspointer] == 0.0)
        return self->program[pc].ival;
    return pc + 1;
}

static int
igverb_jump(iguana_thread_object * self, int pc)
{
    return self->program[pc].ival;
}

static int
igverb_fetch(iguana_thread_object * self, int pc)
{
    int n;
    PyObject *q;
    if (self->memory == NULL) {
        PyErr_SetString(IguanaError, "fetching from non-existent memory");
        return -1;
    }
    CHECK_UNDERFLOW(1);
    n = (int) self->data_stack[self->dspointer - 1];
    q = PyObject_GetItem(self->memory, PyInt_FromLong(n));
    if (q == NULL)
        return -1;
    if (PyFloat_Check(q))
        self->data_stack[self->dspointer - 1] = PyFloat_AsDouble(q);
    else if (PyInt_Check(q))
        self->data_stack[self->dspointer - 1] = (double) PyInt_AsLong(q);
    else {
        PyErr_SetString(IguanaError,
                        "things in memory must be ints or floats");
        return -1;
    }
    return pc;
}

static int
igverb_store(iguana_thread_object * self, int pc)
{
    int n;
    double d;
    if (self->memory == NULL) {
        PyErr_SetString(IguanaError, "storing to non-existent memory");
        return -1;
    }
    CHECK_UNDERFLOW(2);
    self->dspointer -= 2;
    n = (int) self->data_stack[self->dspointer + 1];
    d = self->data_stack[self->dspointer];
    if (PyObject_SetItem(self->memory, PyInt_FromLong(n),
                         PyFloat_FromDouble(d)) == -1)
        return -1;
    return pc;
}

static int
igverb_do(iguana_thread_object * self, int pc)
{
    int index, limit;
    CHECK_UNDERFLOW(2);
    R_CHECK_OVERFLOW(2);
    self->dspointer -= 2;
    index = (int) self->data_stack[self->dspointer + 1];
    limit = (int) self->data_stack[self->dspointer];
    self->return_stack[self->rspointer] = limit;
    self->return_stack[self->rspointer + 1] = index;
    self->rspointer += 2;
    return pc;
}

static int
igverb_loop(iguana_thread_object * self, int pc)
{
    unsigned int index, limit;
    R_CHECK_UNDERFLOW(2);
    index = self->return_stack[self->rspointer - 1] + 1;
    limit = self->return_stack[self->rspointer - 2];
    if (index >= limit) {
        self->rspointer -= 2;
        return pc + 1;
    }
    self->return_stack[self->rspointer - 1] = index;
    return self->program[pc].ival;
}

static int
igverb_i(iguana_thread_object * self, int pc)
{
    unsigned int index;
    R_CHECK_UNDERFLOW(2);
    CHECK_OVERFLOW(1);
    index = self->return_stack[self->rspointer - 1];
    self->data_stack[self->dspointer] = (double) index;
    self->dspointer++;
    return pc;
}

static int
igverb_j(iguana_thread_object * self, int pc)
{
    unsigned int index;
    R_CHECK_UNDERFLOW(4);
    CHECK_OVERFLOW(1);
    index = self->return_stack[self->rspointer - 3];
    self->data_stack[self->dspointer] = (double) index;
    self->dspointer++;
    return pc;
}

static int
igverb_k(iguana_thread_object * self, int pc)
{
    unsigned int index;
    R_CHECK_UNDERFLOW(6);
    CHECK_OVERFLOW(1);
    index = self->return_stack[self->rspointer - 5];
    self->data_stack[self->dspointer] = (double) index;
    self->dspointer++;
    return pc;
}

static int
igverb_spawn(iguana_thread_object * self, int pc)
{
    iguana_thread_object *newguy;
    PyObject *args;
    int n;
    args = Py_BuildValue("(OO)", self->program, self->memory);
    newguy = (iguana_thread_object *) new_iguana_thread(NULL, args);
    if (newguy == NULL)
        return -1;
    CHECK_UNDERFLOW(1);
    self->dspointer--;
    n = (int) self->data_stack[self->dspointer];
    CHECK_UNDERFLOW(n);
    self->dspointer -= n;
    memcpy(newguy->data_stack,
           &(self->data_stack[self->dspointer]), n * sizeof(double));
    newguy->dspointer = n;
    newguy->program_counter = self->program[pc].ival;
    return pc + 1;
}

static int
igverb_atomic_on(iguana_thread_object * self, int pc)
{
    task_switch_enable = 0;
    return pc;
}

static int
igverb_atomic_off(iguana_thread_object * self, int pc)
{
    task_switch_enable = 1;
    return pc;
}

static struct predef {
    char *forth_name;
    int (*function) (iguana_thread_object * self, int pc);
} predefined[] = {
    { "rand", igverb_rand },
    { "lit", igverb_lit },
    { "call", igverb_call },
    { "exit", igverb_exit },
    { "jump", igverb_jump },
    { "zjump", igverb_zjump },
    { "store", igverb_store },
    { "fetch", igverb_fetch },
    { "do", igverb_do },
    { "loop", igverb_loop },
    { "i", igverb_i },
    { "j", igverb_j },
    { "k", igverb_k },
    { "spawn", igverb_spawn },
    { "<atomic", igverb_atomic_on },
    { "atomic>", igverb_atomic_off },
    { NULL, NULL }
};

static void
add_verbs(void)
{
    extern void add_more_verbs(PyObject *);
    struct predef *pr;
    for (pr = predefined; pr->forth_name; pr++)
        PyDict_SetItemString(verb_dict, pr->forth_name,
                             PyInt_FromLong((long) pr->function));
    add_more_verbs(verb_dict);
}

/****************************************************/

PyMethodDef iguana_thread_methods[] = {
    {"push", (PyCFunction) igthread_push, 1, push_doc},
    {"pop", (PyCFunction) igthread_pop, 1, pop_doc},
    {NULL, NULL}                /* sentinel */
};

static PyObject *
igthread_getattr(iguana_thread_object *self, char *name)
{
    if (strcmp(name, "pc") == 0)
        return PyInt_FromLong(self->program_counter);
    return Py_FindMethod(iguana_thread_methods, (PyObject *) self, name);
}

static int
igthread_setattr(iguana_thread_object *self, char *name, PyObject * v)
{
    if (v == NULL) {
        PyErr_SetString(PyExc_AttributeError,
                        "can't delete attributes of an iguana thread");
        return -1;
    }
    if (strcmp(name, "pc") == 0) {
        if (!PyInt_Check(v)) {
            PyErr_SetString(PyExc_AttributeError,
                            "program counter must be an integer");
            return -1;
        }
        self->program_counter = PyInt_AsLong(v);
        return 0;
    }
    PyErr_SetString(PyExc_AttributeError, name);
    return -1;
}

/**************************************************************/

static PyObject *
ig_active_threads(PyObject * self, PyObject * args)
{
    long n;
    iguana_thread_object *P;
    if (!PyArg_ParseTuple(args, ""))
        return NULL;
    for (n = 0, P = root_thread.next; P != &root_thread; P = P->next, n++);
    return PyInt_FromLong(n);
}

static int igverb_exit(iguana_thread_object * self, int pc);

static PyObject *
ig_threads_step(PyObject * self, PyObject * args)
{
    int num_steps = 1;
    iguana_thread_object *P, *Q, *R;
    if (!PyArg_ParseTuple(args, "|i", &num_steps))
        return NULL;
    while (num_steps--) {
        if (root_thread.next == &root_thread)
            break;
        P = root_thread.next;
        while (P != &root_thread) {
            int pc;
            igverbfunc func;
            // printf("Now serving thread %p\n", P);
            pc = P->program_counter;
            if (pc >= P->program_size) {
                PyErr_SetString(IguanaError, "program ran off the end");
                return NULL;
            }
            func = (igverbfunc) P->program[pc].ival;
            if (func == igverb_exit && P->rspointer == 0) {
                /*
                 * this thread has finished its job 
                 */
                Q = P->next;
                R = P->prev;
                R->next = Q;
                Q->prev = R;
                P->next = P->prev = NULL;
                Py_DECREF(P);
                P = Q;
                task_switch_enable = 1;
            } else {
                pc = (*func) (P, pc + 1);
                if (pc < 0) {
                    /*
                     * the function will set up its own error string 
                     */
                    return NULL;
                }
                P->program_counter = pc;
            }
            if (task_switch_enable)
                P = P->next;
        }
    }
    Py_INCREF(Py_None);
    return Py_None;
}

/*
 * List of methods defined in the module 
 */

static struct PyMethodDef ighelp_methods[] = {
    {"thread", (PyCFunction) new_iguana_thread, 1},
    {"active_threads", (PyCFunction) ig_active_threads, 1},
    {"step", (PyCFunction) ig_threads_step, 1},
    {NULL, NULL}
};

static char ighelp_doc[] = "\
This module defines a Forth-esque virtual machine called an Iguana\n\
thread. Iguana threads are small and independent so they'll be good\n\
for massive-multithreading hacks.\n\
\n\
thread(p)  ==> p is a list representing an Iguana program\n\
               the return value is a thread\n\
thread(p,n)  ==> p is a list representing an Iguana program\n\
                 n is an integer representing a stack depth\n\
                 the return value is a thread\n\
Default stack depth is 100.";

void
initighelp()
{
    PyObject *m, *d;
    time_t T;
    int i;

    /*
     * initialize doubly-linked list of active threads 
     */
    root_thread.next = root_thread.prev = &root_thread;
    /*
     * set up a random number generator 
     */
    time(&T);
    xrand = T & 255;
    yrand = (T >> 8) & 255;
    zrand = (T >> 16) & 255;
    for (i = 0; i < 5; i++) my_rand();
    /*
     * Create the module and add the functions 
     */
    m = Py_InitModule3("ighelp", ighelp_methods, ighelp_doc);
    /*
     * Add some symbolic constants to the module 
     */
    d = PyModule_GetDict(m);
    IguanaError = PyString_FromString("IguanaError");
    PyDict_SetItemString(d, "IguanaError", IguanaError);
    verb_dict = PyDict_New();
    add_verbs();
    PyDict_SetItemString(d, "verbs", verb_dict);
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
