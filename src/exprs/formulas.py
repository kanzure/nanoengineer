# Formulas - on request, they (re)compute something for a client (perhaps using args passed each time by client),
# and store usage (record of what's used by that recomputation) in client;
# different kinds (subclasses of FormulaSuperclass) might accept different kinds of formulas
# (e.g. whether they take client args, how they return value (eg retval or side effects),
#  whether they offer version number of value),
# or might store usage in client in different ways (eg ordered or not, store input values or not),
# or offer more features (e.g. diff old and current input values, recompute trivially if no change).

class FormulaSuperclass:
    """superclass for different kinds of formulas, which vary in how they compute a value (and how they track it? not sure)
    [will there be more than one kind? not sure.]
    """
    def get_value(self, where_to_track):
        #e set up where_to_track into dynenv ie env.track (or so)
        val = self._C_value() ###e catch exceptions
        #e bla
        return val
    def _C_value(self): #e no provision yet for passing args or not returning value
        assert 0, "subclass must implem"
    pass
    
class FormulaFromCallable(FormulaSuperclass):
    """Turn any python callable (presumed to do standard usage tracking of what it uses, into the dynenv)
    into a formula object (which does usage tracking into an argument of get_value). [??]
    """
    def __init__(self, callable1):
        self._callable = callable1
        pass
    def _C_value(self):
        "called by superclass get_value; should usage_track into dynenv"
        self._callable()
    pass
