'''
py_utils.py

$Id$

simple utility functions for python built-in types
'''

# note: basic.py imports * from here.

def interleave(elts, gaps):
    """Return an interleaved list of the given elements and gaps --
    e.g. elt[0] gap[0] elt[1] gap[1] elt[2], for 3 elts and 2 gaps.
    (Error if input list lengths are not properly related; special case for no elts.)
    """
    if len(elts) <= 1: # btw, code below would also work for len(elts) == 1
        assert not gaps
        return elts
    assert len(gaps) + 1 == len(elts)
    def elt_or_gap(i):
        if i % 2 == 0:
            return elts[i / 2]
        else:
            return gaps[int(i / 2)]
    return map(elt_or_gap, range(len(elts) + len(gaps)))

def interleave_by_func(elts, gapfunc):
    gaps = [gapfunc(e1,e2) for e1,e2 in zip(elts[:-1],elts[0:])]
    return interleave(elts, gaps)

def dict_ordered_values(d1):
    items = d1.items()
    items.sort()
    return [v for (k,v) in items]

def printonce(msg, msg2 = None): #e refile
    """print msg (which should be a constant), but only once per session.
    If msg is *not* a constant, pass its constant part (a nonempty string --
    not checked, bad errors if violated) in msg2.
       WARNING: If you pass nonconstant msg and forget to pass msg2, or if msg2 is nonconstant or false,
    this might print msg on every call!
    """
    constpart = msg2 or msg
    from env import seen_before
    if not seen_before(constpart):
        print msg
    return

class MemoDict(dict): #k will inherit from dict work? ###e rename to extensibledict?? -- it doesn't have to memoize exactly...
    """Act like a transparently extensible dict,
    given a way to compute a new element (which we'll memoize) from the dict key;
    this way MUST NOT USE USAGE-TRACKED LVALS (WARNING: this error is not yet detected).
    WARNING: typical uses are likely to involve cyclic refs, causing memory leaks.
    """
    def __init__(self, way):
        self._way = way
        dict.__init__(self)
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            printonce("developer note: begin_disallowing_usage_tracking is still a stub")
            # begin_disallowing_usage_tracking()  ####IMPLEM #e pass explanation for use in error messages
            val = self._way(key)
                #e assert no usage gets tracked? for efficiency, do it by checking a counter before & after? or tmp hide tracker?
                # yes, temporarily delete the global dict seen when usage tracking, so whoever tries it will get an error! ####IMPLEM
            # end_disallowing_usage_tracking() ####IMPLEM; note, it needs to be legal for something during the above to reallow it for itself
            dict.__setitem__(self, key, val)
            return val
    pass

# end
