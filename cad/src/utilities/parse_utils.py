# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
parse_utils.py -- utilities for general parsing, and for parsing streams of python tokens.
Also a prototype "description class" which can be used to represent results of parsing a "description".
Also an example grammar, which can be used for parsing "parameter-set description files".
(FYI: All these things are used to parse "parameter dialog description files", *.desc.)

@author: Bruce
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

TODO:

This ought to be split into several files, and generalized, and ThingData renamed
and cleaned up. And optimized (easy), since the parser is probably quadratic time
in input file size, at least when used in the usual way, on a list that comes
from generate_tokens.
"""

from tokenize import generate_tokens
from tokenize import tok_name
import sys

# == basic general parser

debug_grammar = False # set to True for more info about grammar in syntax error messages

class ParseFail(Exception): pass #e make it a more specific kind of exception?
class SyntaxError(Exception): pass

def parse(pat, rest):
    """
    either return (res, newrest), or raise ParseFail or SyntaxError
    """
##    if type(pat) == type(""):
##        pass
    #e other python types with special meanings, like list?
    try:
        retval = "<none yet>" # for debugging
        retval = pat.parse(rest)
        res, newrest = retval
    except ParseFail:
        raise
    except SyntaxError:
        raise
    except:
        print "retval at exception: %r" % (retval,)
        raise SyntaxError, "exception %s %s at %s" % (sys.exc_info()[0], sys.exc_info()[1], describe_where(rest)) ###k ##e need more info, about pat?
        ##e maybe also postprocess the results using another method of pat, or call pat.parse1 to do it all,
        # to support uniform keyword args for postprocess funcs (with access to rest's env)
    try:
        resultfunc = pat.kws.get('result') # this would be cleaner if some pat method did the whole thing...
    except:
        return res, newrest
    if resultfunc:
        try:
            return resultfunc(res), newrest
        except:
            print "resultfunc %r failed on res %r" % (resultfunc, res) # this seems often useful
            raise
    return res, newrest

def parse_top(pat, rest):
    try:
        return parse(pat, rest)
    except ParseFail:
        return "ParseFail", None
    except SyntaxError, e:
        return 'SyntaxError: ' + str(e), None
    pass

class ParseRule:
    """
    subclasses are specific parse-rule constructors; their instances are therefore parse rules
    """
    def __init__(self, *args, **kws):
        self.args = args
        self.kws = kws
        self.validate()
        return
    def validate(self):
        "subclasses can have this check for errors in args and kws, preprocess them, etc"
        #e the subclasses in this example might not bother to define this as an error checker
        pass
    #e need __str__ for use in syntax error messages
    pass

class Seq(ParseRule):
    def parse(self, rest):
        res = []
        for arg in self.args:
            try:
                res0, rest = parse(arg, rest)
            except ParseFail:
                if not res:
                    raise
                # this is mostly useless until we have sensible __str__ (and even then, is mainly only useful for debugging grammar):
                if debug_grammar:
                    msg = "Can't complete %s, stuck at arg %d = %s\nat %s" % (self, len(res) + 1, arg, describe_where(rest))
                else:
                    msg = "%s" % (describe_where(rest),)
                raise SyntaxError, msg
            res.append(res0)
        return res, rest
    pass

class Alt(ParseRule):
    def parse(self, rest):
        for arg in self.args:
            try:
                return parse(arg, rest)
            except ParseFail:
                continue
        raise ParseFail
    pass

# == higher-level general parser utilities

class ForwardDef(ParseRule):
    """
    For defining placeholders for recursive patterns;
    by convention, arg0 (optional) is some sort of debug name;
    self.pat must be set by caller before use
    """
    def parse(self, rest):
        return parse(self.pat, rest)
    pass

def ListOf(pat):
    """
    0 or more pats
    """
    res = ForwardDef()
    res.pat = Optional(Seq(pat, res,
                            result = lambda (p,r): [p] + r # fix retval format to be a single list (warning: quadratic time)
                               # note: this has value None: [p].extend(r)
                               # (and it too would make entire ListOf take quadratic time if it worked)
                           ))
    return res

def Optional(pat):
    return Alt(pat, Nothing)

class NothingClass(ParseRule):
    def parse(self, rest):
        return [], rest # the fact that this is [] (rather than e.g. None) is depended on by ListOf's result lambda
    pass

Nothing = NothingClass()

# == some things that are specific for rest being a list of 5-tuples coming from tokenize.generate_tokens

##e ideally, these would be methods of a class which represented this kind of input, and had an efficient .next method,
# and methods for other kinds of access into it; the current implem might be quadratic time in the number of tokens,
# depending on how python lists implement the [1:] operation.

def describe_where(rest):
    """
    assume rest is a list of token 5-tuples as returned by generate_tokens
    """
    if not rest:
        return "end of input"
    toktype, tokstring, (srow, scol), (erow, ecol), line = rest[0]
    res1 = "line %d, column %d:" % (srow, scol) # tested! exactly correct (numbering columns from 0, lines from 1)
    res2 = "*******>" + line.rstrip() ##e should also turn tabs to spaces -- until we do, use a prefix of length 8
    res3 = "*******>" + scol * ' ' + '^'
    return '\n'.join([res1,res2,res3])

def token_name(rest):
    if not rest:
        return None
    return tok_name[rest[0][0]]

IGNORED_TOKNAMES = ('NL', 'COMMENT') # this is really an aspect of our specific grammar
    # note: NL is a continuation newline, not a syntactically relevant newline
    # (for that see Newline below, based on tokentype NEWLINE)

class TokenType(ParseRule):
    def validate(self):
        toknames = self.args[0]
        # let this be a string (one name) or a list (multiple names) (list has been tested but might not be currently used)
        want_tokname_dflt = True
        if type(toknames) == type(""):
            want_tokname_dflt = False
            toknames = [toknames]
        self.want_tokname = self.kws.get('want_tokname', want_tokname_dflt)
        assert type(toknames) == type([])
        for tokname in toknames:
            assert type(tokname) == type("") and tokname in tok_name.itervalues(), \
                   "illegal tokname: %r (not found in %r)" % \
                   ( tokname, tok_name.values() )
        self.toknames = toknames
        try:
            self.cond = self.args[1]
        except IndexError:
            self.cond = lambda tokstring: True
    def parse(self, rest):
        """
        assume rest is a list of token 5-tuples as returned by generate_tokens
        """
        while rest and token_name(rest) in IGNORED_TOKNAMES:
            rest = rest[1:] # this might be inefficient for long inputs, and for that matter, so might everything else here be
            # note, this filtering is wasted (redone many times at same place) if we end up parsefailing, but that's tolerable for now
        if not rest or token_name(rest) not in self.toknames:
            raise ParseFail
        tokstring = rest[0][1]
        if self.want_tokname:
            res = (token_name(rest), tokstring)
        else:
            res = tokstring
        if not self.cond(res):
            raise ParseFail
        return res, rest[1:]
    pass

def Op( opstring):
    return TokenType('OP', lambda token: token == opstring)
        ### REVIEW: why doesn't this lambda need the "opstring = opstring" kluge?
        # Has notneeding this been tested? [bruce comment 070918]

# == the specific grammar of "parameter-set description files"

# TODO: split this grammar (including IGNORED_TOKNAMES above, somehow) into its own file

# thing = name : arglist
# optional indented things
# ignore everything else (some are errors) (easiest: filter the ok to ignore, stop at an error, print it at end)

def make_number(token, sign = 1): # other signs untested
    for type in (int, long, float):
        try:
            return type(token) * sign
        except:
            pass
    raise SyntaxError, "illegal number: %r" % (token,) ### flaw: this doesn't include desc of where it happened...

Name = TokenType('NAME')
Colon = Op(':')
Minus = Op('-')
End = TokenType('ENDMARKER')
Newline = TokenType('NEWLINE')
# Arg = TokenType(['NUMBER', 'STRING', 'NAME'])
Number = TokenType('NUMBER', result = make_number)
Name = TokenType('NAME')
String = TokenType('STRING', result = eval)
    # eval is to turn '"x"' into 'x'; it's safe since the tokenizer promises this is a string literal
# String, Name
Arg = Alt( Number,
           String,
           Name, #e do STRING & NAME results need to be distinguished?? We'll see...
           Seq( Minus, Number, result = lambda (m,n): - n )
        )
Arglist = ListOf(Arg) # not comma-sep; whitespace sep is ok (since ws is ignored by tokenizer) ##k test that!

def Indented(pat):
    return Seq(TokenType('INDENT'), pat, TokenType('DEDENT'), result = lambda (i,p,d): p )

Thing = ForwardDef("Thing")
Thing.pat = Seq( Name, Colon, Arglist, Newline, Optional(Indented(ListOf(Thing))),
                 result = lambda (name,c,args,nl,subthings): makeThing(name, args, subthings)
                 )

Whole = Seq(ListOf(Thing), End, result = lambda (lt,e): lt )

# ==

# Description objects (prototype)

class attr_interface_to_dict:
    # make sure all of our methods and data start with '_'!
    def __init__(self, _dict1):
        self._dict1 = _dict1
    def __getattr__(self, attr): # in class attr_interface_to_dict
        if attr.startswith('_'):
            raise AttributeError, attr
            # Something like this is needed, even if _dict1 contains such an attr,
            # so such an attr (if specially named) won't fool Python into giving us different semantics.
            # But if we decide _dict1 should be able to contain some names of this form, we could make
            # the prohibition tighter as long as it covered all Python special attrnames and our own attr/method names.
        try:
            return self._dict1[attr]
        except KeyError:
            raise AttributeError, attr
        pass
    pass

class Info:
    def __init__(self, *_args, **kws): # sort of like ParseRule -- unify them?
        self._args = _args
        self.kws = kws
        self.init()
    def init(self):
        pass
    def __repr__(self):
        return "%s%r" % (self.__class__.__name__, self._args) ##k crude approx.
    pass

class ThingData(Info):
    """
    #doc...
    the data in a thing
    """# could this be Thing -- that symbol's value would be both a constructor and a parserule... not sure...
    options = {} # save RAM & time by sharing this when surely empty... could cause bugs if it's altered directly by outside code
    option_attrs = attr_interface_to_dict(options) # also shared, also must be replaced if nonempty
    def init(self):
        self.name, self.thingargs, self.subthings = self._args # possible name conflict: .args vs .thingargs
        #070330 improving the internal documentation:
        ## print "debug ThingData: name = %r, thingargs = %r, subthings = %r" % self._args
        # for an option setting like "max = 9999.0":
        #   name = 'max', thingargs = [9999.0], subthings = []
        #   so name is the option name, thingargs contains one member which is the value, subthings is empty.
        # for a subobject:
        #   name = 'parameter', thingargs = ['L2'], subthings = [ThingData()...]
        #   so name is the type (or used by the parent to choose the type), thingargs has one (optional?) member which is the name,
        #   and subthings contains both actual subobjects and option settings.
        # for widget: combobox, two kluges are used: it acts as both a subthing and an option setting,
        # and its own subthings, which look like option settings, also have an order which is preserved (I think).
        # Both kluges apply to everything -- all option settings stay around in the subthings list,
        # and (I think) all subthing typenames get treated as options set to the subthing name.

        self.args = self.thingargs # already assumed twice, in the using code for desc... should translate remaining thingargs -> args
        if self.subthings:
            self.options = {}
            self.option_attrs = attr_interface_to_dict(self.options)
            ## self.optattrs = AttrHolder() # not yet needed... maybe better to make an obj providing attr interface to self.options
        for sub in self.subthings:
            sub.maybe_set_self_as_option_in(self.options)
        ## print "options:",self.options
        return
    def maybe_set_self_as_option_in(self, dict1):
        """
        If self is an option setting, set it in dict1
        """
        #e in future might need more args, like an env, or might need to store a formula
        # (which might indicate switching to getattr interface?)
        if not self.subthings and len(self.thingargs) == 1:
            dict1[self.name] = self.thingargs[0]
        elif len(self.thingargs) == 1:
            # this is the "simplest hack that could possibly work" to let widget=combobox work as a condition
            # even though it has subthings which further define the combobox. we'll see if doing it generally
            # causes any trouble and/or is useful in other cases. Note that we stored only 'combobox' as the value,
            # not a combobox datum extended with those subthings (its items). (As if the cond was really about the class of value?)
            dict1[self.name] = self.thingargs[0]
    def pprint(self, indent = ""):
        name, args, subthings = self._args
        print indent + name + ': ' + ', '.join(map(repr,args)) # works decently except for 1.4099999999999999 rather than 1.41
        for sub in subthings:
            sub.pprint( indent + '    ' )
    def kids(self, kinds):
        # kinds could already be a list
        if type(kinds) == type(''):
            kinds = (kinds,)
        res = []
        for kid in self.subthings:
            # could be a real kid, or just an assignment; use kinds to tell (assume caller knows what it's doing)
            #e (maybe we even permit multiple assignments and let the last one done *before a kid is made* control that kid????)
            if kid.name in kinds:
                res.append(kid)
        return res
    def isa(self, kind, **conds):
        """
        Predicate: are we of this kind, and do we match conditions like xxx=yyy for our option xxx being yyy?
        """
        #### LOGIC BUG: for symbolic options, the stored value is a string, the match is a string, all ok.
        # but for booleans, the stored val is 'true' or 'false' -- not ok. How do we get best of all these worlds?? ####
        if self.name != kind:
            return False
        for param, val in conds.items():
            #### LOGIC BUG 2 - do we match if we don't store param at all? who supplies defaults?
            # for now: let missing param be the same as a value of None. (this is used in matching widget = ('lineedit',None), etc)
            if self.matches( self.options.get(param, None), val):
                pass
            else:
                return False
            continue
        return True
    def matches(self, paramval, valpattern):
        return paramval == valpattern or (type(valpattern) == type(()) and paramval in valpattern)
            # note: 'in' is not using recursive match, just ==
    def as_expr(self):
        """
        Return an Expr form of self. (Only call after it's fully parsed, since parsing is destructive.)
        """
        # 070330, experimental. Will require exprs module. Not yet called. For now, advise don't call except when a debug_pref is set.
        #e name -> exprhead? using an env? via a Symbol?
        pass

    pass

def makeThing(name, args, subthings):
    """
    #doc...
    Note: we don't yet know if the ThingData we return will end up as a subobject
    or an option-value-setting of its parent... its parent will call
    thingdata.maybe_set_self_as_option_in(parent) to make and execute that decision.
    """
    if not args and not subthings:
        print "warning: \"%s:\" with no args or subthings" % (name,)
    return ThingData(name, args, subthings)

# == test code (might not be up to date)

if __name__ == '__main__':

    from pprint import pprint

    ## filename = "testui.txt"
    filename = "../plugins/CoNTub/HJ-params.desc"

    file = open(filename, 'rU')

    gentok = generate_tokens(file.readline)

    # print gentok # a generator object

    # pprint( list(gentok) ) # works

    if 0: # works
        res = []

        for toktype, tokstring, (srow, scol), (erow, ecol), line in gentok:
            # print toktype, tokstring
            res.append( (toktype, tok_name[toktype], tokstring) )

        res.sort()
        pprint(res)

    res, newrest = parse_top(Whole, list(gentok))
    print len(` res `), 'chars in res' #3924
    print res # might be an error message
    if newrest is not None:
        print newrest
        print res[0].pprint() #k

    print "test done"

# that might be working... now what?
# the language has an ambiguity... exprhead:args {moreargs}, vs option:val meaning option=val.
# we'll turn things into objects, recognize some subthings as those objects and others as assigments (perhaps with decorations).
# (or, we'll decide that all assignments use '=' not ':'. Tried it... decided too hard to casually write the file this way.)

#### possible bugs:
# - I never tried a negative or explicit-positive number -- now, negative works, explicit-positive doesn't but should ###
# - Won't work for args sep by comma or in parens (doesn't yet matter)

# end

