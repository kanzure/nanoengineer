# symbols to be imported by every module in this package

from VQT import V, A, Q

from debug import reload_once_per_event, print_compact_traceback

def reload_once(module):
    ###e should check whether it's been modified, if only to reduce console output
    # similar code is in test.py
    from testdraw import vv
    reload_once_per_event(module, always_print = True, never_again = False, counter = vv.reload_counter, check_modtime = True)
    
import py_utils
reload_once(py_utils)

from py_utils import *

#e maybe also the color names?

def stub(*args, **kws):
    assert 0, "stub called"

# end
