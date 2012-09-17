# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
rendering.py -- rendering loop control, etc

$Id$

"""

    IorE drawkid def should be sort of like:

    def drawkid(self, kid):
        warpfuncs = getattr(self.env.glpane, '_exprs__drawkid_funcs', None) #070218 or so new feature
        while warpfuncs:
            func, warpfuncs = warpfuncs
            try:
                color0 = '?' # for error message in case of exception
                color0 = func(color) # don't alter color itself until we're sure we had no exception in this try clause
                color = normalize_color(color0)
            except:
                print_compact_traceback("exception in %r.fix_color(%r) warping color %r with func %r (color0 = %r): " % \
                                        ( self, color_orig, color, func, color0 ) )
                pass
            continue
        return color

    and is now: (except it doesn't really contain that _exprs__whatever line):

    def drawkid(self, kid): # note: supersedes nim _e_decorate_draw [070210]
        #e plans: protect from exceptions, debug_pref for no-coord-change enforcement (for testing),
        # and most importantly, make possible a drawing pass which draws only a specified subset of drawables
        # but in their coord- or glstate- transforming containers, e.g. for a highlight-drawing pass.
        # (that last is what we're doing now, with _exprs__whatever 070218)
        oldfunc = getattr(glpane, '_exprs__whatever', None) #e rename attr
        if kid is not None:
            kid.draw()
        return


class _drawkid_oldfunc: # use this to replace glpane drawkid func called inside IorE drawkid ###implem
    "One of these becomes the temporary drawkid func ... " # other code is WRONG, oldfunc(parent, kid) is what we need to be able to call
    def __init__(self, drawkid_contrib_func, oldfunc):
        self.drawkid_contrib_func = drawkid_contrib_func # public for set? if not, need a set method too
        self.oldfunc = oldfunc or noop # oldfunc might be None
    def parent_draw_kid(self, parent, kid):
        "when self is active in dynenv, a bound method made from this method is what gets called in place of (or by?) usual drawkid (in oldfunc)"
        func = self.drawkid_contrib_func # what someone contributed... #doc better
        oldfunc = self.oldfunc
        func(oldfunc, parent, kid)
    def set_drawkid_contrib_func(self, func): # (a rare case where I think a set method is better (clearer) than a public settable attr)
        self.drawkid_contrib_func = func
    pass

class SelectiveRedrawer(InstanceOrExpr): #070217 to make highlighting work in displists, someday [replaces "draw decorators"]
    """
    """
    def draw(self):
        self._parents_lists = {} # maps obj (drawn during us) to list of all its draw-parents (highest possible parent being self)
        self._later = {} # maps obj to list of funcs to call later in same GL state & coords as used to draw obj
        #e put self in dynenv if needed, to permit registration of selective redraw or point-finding (x,y,depth)
            #### QUESTION: (when is that done? for make of delegate?? or right now, in glpane? (if so, restore prior, or reg with all???)
        # begin having drawkid track parents in us
        # (as well as in whatever objs it did before, in glpane linked list like for fix_color)
            ###### WAIT, what about displists it calls? they'll need to have tracked parents ahead of time, i think... ####e
        glpane = self.env.glpane
        oldfunc = getattr(glpane, '_exprs__whatever', None) #e rename attr
        newfunc = _drawkid_oldfunc( self._drawkid_collect_parents, oldfunc) #e rename _drawkid_oldfunc and maybe the args passed
        setattr(glpane, '_exprs__whatever', newfunc) # this means IorE.drawkid will call it ###IMPLEM
        try:
            self.drawkid(self.delegate) # has try/except, so we don't need our own around just this call
                ###k make sure what it has is not try/finally
            # end having drawkid track that (see below)
            # some of those kids/grandkids also entered things into our list of things needing redraw
            # figure out transclose of parents of things we need to redraw (or run code in their coords anyway -- redraw in modified way)
            objdict = dict([(obj,obj) for obj in self._later])
            junk, self._proper_parents = self._transclose_parents(objdict)
            # begin modifying drawkid to filter... the method of mod is really to wrap it with our own code...
            newfunc.set_drawkid_contrib_func( self._drawkid_selective )
            #
            self.drawkid(self.delegate)
        except:
            msg = "bug: exception somewhere in %r.draw(), delegate %r; len(parents_lists) = %d, len(_later) = %d" % \
                      (self, self.delegate, len(self._parents_lists), len(self._later))
            print_compact_traceback( msg + ": ")
            pass
        # end
        setattr(glpane, '_exprs__whatever', oldfunc)
        #e and repeat, if we have more than one redraw-pass
        return
    def _drawkid_collect_parents(self, oldfunc, parent, kid):
        """This intercepts (a func called by) parent.drawkid(kid) when we're collecting parents,
        with oldfunc being (a func called inside) parent.drawkid as if we were not active in dynenv.
        """
        if 0:
            # this would be equiv to behavior we replace:
            oldfunc(parent, kid)
            return
        # parent is a draw-parent of kid
        self._parents_lists.setdefault(kid, []).append(parent) #e could optim
        oldfunc(parent, kid)
        return
    def redraw_later(self, obj, func): ### PUT SELF in env so i can be called
        """This should be called during self.draw (by something we're drawing). obj should be that something, or anything else
        we might draw during self.draw. This registers func to be called (in our later special selective-redrawing pass)
        once for each time obj was drawn in the main pass, in the same local coords and OpenGL state obj was drawn in at the time
        (but not inside any display lists being called or compiled, whether or not obj was drawn into one).
           Typical values for func are obj.draw(), modified(obj).draw(), a lambda that calls gluProject or so....
        [#e we might add ways to ask for more args to be passed to func (none are now), like the draw-parent, self, etc.]
        """
        self._later.setdefault(obj, []).append(func) #e could optim
        return
    def _transclose_parents(self, objdict):
        """Given a dict from obj to obj, for some objs to redraw-modifiedly,
        return two things: a dict including them & all their parents (recursively),
        and a dict including only the ones that were parents.
        """
        proper_parents = {} # proper parents (objdict objs not in there unless they are also parents)
        def collect_parents(obj, dict1):
            for parent in self._parents_lists[obj]:
                dict1[parent] = parent
                proper_parents[parent] = parent
            return
        res1 = transclose(objdict, collect_parents)
        return res1, proper_parents #k no need to return res1?
    def _drawkid_selective(self, oldfunc, parent, obj):
        """Called using same interface as _drawkid_collect_parents.
        What we do:
        - for objs registered in _later, call their func (or funcs). GL state and coords will be same as when obj.draw was called.
        - for objs which are draw-parents of other objs, call their .draw (so as to get called for their kids, in GL state they set up).
          (If they also do direct drawing, this should not hurt; they can also check a flag and not do it, someday. #e)
        - for other objs, do nothing.
        """
        for func in self._later.get(obj, ()):
            try:
                func()
            except:
                msg = "bug: %r._drawkid_selective() ignoring exception in func %r for %r (parent %r)" % \
                      (self, func, obj, parent)
                print_compact_traceback( msg + ": ")
            continue
        if obj in self._proper_parents:
            oldfunc(parent, obj) ##k
        return
    pass
