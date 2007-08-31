"""
$Id$
"""
# experimental, bruce 070814

class StatelessExpr: # probably not IorE... but might be if these are not needed to define that
    _e_stateless_expr = True # should be F in super
    pass

class AttrDeclExpr(StatelessExpr):
    #e special behavior in the metaclass, or when used as a descriptor --
    # expr objects *are* descriptors? or can make them on request by metaclass?
    pass

class Instance(AttrDeclExpr):
    pass

class ArgOrOption(AttrDeclExpr):
    pass

class Arg(AttrDeclExpr):
    pass

class Option(AttrDeclExpr):
    pass

# etc

# add code to turn them into equiv exprs... metaclass can use that code
# and if we want it can be defined using existing code... then cleaned up later

