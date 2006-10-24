'''
basic.py -- define things to be imported by every module in this package (using import *)

$Id$
'''

from debug import reload_once_per_event, print_compact_traceback

def reload_once(module):
    """This function is used to support automatic runtime reloading of modules within this package,
    for developer convenience. To use it, add this code before any import of symbols from a module
    (or use this code in place of any direct import of a module):

      import module
      reload_once(module)

    Warning: not all modules support runtime reload. Those that don't should say so in their docstrings.
    
    Warning: this system does not yet properly handle indirect imports, when only the inner module has
    been modified. See code comments for details, especially the docstring of debug.reload_once_per_event().
    As a workaround, if A imports B and you edit B.py, also edit A.py in order to trigger the desired runtime reload of B.py.
    
    Note: this function's module (exprs.basic itself) is fast and harmless enough to reload that it can be
    reloaded on every use, without bothering to use reload_once. Therefore, external callers of anything
    in the exprs package can always "import basic;reload(basic)" first, and if they do, all modules within
    exprs can just start with "from basic import *". But for clarity, some of them call reload_once on basic too.
    """
    from testdraw import vv
    reload_once_per_event(module, always_print = True, never_again = False, counter = vv.reload_counter, check_modtime = True)

# ==

from VQT import V, A, Q

from state_utils import _UNSET_ # warning: not included in "import *"
from state_utils import transclose

# ==

import py_utils
reload_once(py_utils)

from py_utils import *

# == colors (constants and simple functions; import them everywhere to discourage name conflicts that show up only later)

#e maybe import the following from a different file, but for now we need to define some here
#k need to make sure none of these are defined elsewhere in this module
from constants import black, red, green, blue, purple, magenta, violet, yellow, orange, pink, white, gray
    # note: various defs of purple I've seen:
    # ave_colors( 0.5, red, blue), or (0.5, 0.0, 0.5), or (0.7,0.0,0.7), or (0.6, 0.1, 0.9) == violet in constants.py
from constants import aqua, darkgreen, navy, darkred, lightblue
from constants import ave_colors

#e define brown somewhere, and new funcs to lighten or darken a color

lightblue = ave_colors( 0.2, blue, white)
lightgreen = ave_colors( 0.2, green, white)
halfblue = ave_colors( 0.5, blue, white)

def translucent_color(color, opacity = 0.5): #e refile with ave_colors
    """Make color (a 3- or 4-tuple of floats) have the given opacity (default 0.5, might be revised);
    if it was already translucent, this multiplies the opacity it had.
    """
    if len(color) == 3:
        c1, c2, c3 = color
        c4 = 1.0
    else:
        c1, c2, c3, c4 = color
    return (c1, c2, c3, c4 * opacity)

trans_blue = translucent_color(halfblue)
trans_red = translucent_color(red)
trans_green = translucent_color(green)

# ==

def stub(*args, **kws):
    assert 0, "stub called"

from __Symbols__ import _self # (__Symbols__ module doesn't support reload) # warning: not included in "import *"

### PROBLEM: _self is not imported by import *. For now, just import it manually as needed... later, not sure. Same with _UNSET_.

# end
