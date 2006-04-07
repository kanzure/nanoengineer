#define RETURN_STACK_SIZE 100

typedef union {
    int ival;
    double dval;
} program_entry;

typedef struct _ig_thread
{
    PyObject_HEAD struct _ig_thread *prev, *next;
    double *data_stack;
    unsigned int return_stack[RETURN_STACK_SIZE];
    int stacksize, dspointer, rspointer, program_counter, program_size, finished;
    program_entry *program;
    PyObject *memory;
} iguana_thread_object;

typedef int (*igverbfunc) (iguana_thread_object *, int);

#define ASSERT(cond) \
if (!(cond)) \
{ \
  PyErr_SetString(PyExc_AssertionError, #cond); \
  return EVILRETURN; \
}

#define CHECK_UNDERFLOW(n) \
    ASSERT(self->dspointer >= n)
#define CHECK_OVERFLOW(n) \
    ASSERT(self->dspointer < self->stacksize - n)
#define R_CHECK_UNDERFLOW(n) \
    ASSERT(self->rspointer >= n)
#define R_CHECK_OVERFLOW(n) \
    ASSERT(self->rspointer < RETURN_STACK_SIZE - n)
