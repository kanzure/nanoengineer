"""
rendering.py -- rendering loop control, etc

$Id$
"""

    iore drawkid def should be:
        
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

class _drawkid_oldfunc: # use ths to replace g,pane drawkid func used by iore drawkid ###
    "One of these becomes the temporary drawkid func ... " # other code is WRONG, oldfunc(parent, kid) is what we need to be able to call
    def __init__(self, drawkid_contrib_func, oldfunc):
        self.drawkid_contrib_func = drawkid_contrib_func
        self.oldfunc = oldfunc
    def parent_drawkid(self, parent, kid):
        "# when we're active, a bound method made from this is what gets called in place of usual drawkid (in oldfunc)"
        func = self.drawkid_contrib_func # what someone contributed... #doc better
        oldfunc = self.oldfunc
        func(oldfunc, parent, kid)
    pass

class SelectiveRedrawer(InstanceOrExpr): #070217 to make highlighting work in displists, someday [replaces "draw decorators"]
    """
    """
    def draw(self):
        self._parents_lists = {} # maps obj (drawn during us) to list of all its draw-parents (highest possible parent being self)
        self._later = {} # maps obj to list of funcs to call later in same GL state & coords as used to draw obj
        #e put self in dynenv if needed, to permit registration of selective redraw or point-finding (x,y,depth)
            #### QUESTION: (when is that done? for make of delegate?)
        #e begin having drawkid track parents in us (as well as in whatever objs it did before, in glpane linked list like for fix_color)
            ### WAIT, what about displists it calls? they'll need to have tracked parents ahead of time, i think... ####e
        self.drawkid(self.delegate)
        #e end
        # some of those kids/grandkids also entered things into our list of things needing redraw
        # figure out transclose of parents of things we need to redraw (or run code in their coords anyway -- redraw in modified way)
        objdict = dict([(obj,obj) for obj in self._later])
        junk, self._proper_parents = self._transclose_parents(objdict)
        #e begin modifying drawkid to filter... the method of mod is really to wrap it with our own code...
        self.drawkid(self.delegate)
        #e end
        # and repeat, if we have more than one redraw-pass
        return
    def _drawkid_collect_parents(self, oldfunc, parent, kid): ### CALL ME
        """This intercepts parent.drawkid(kid) when we're collecting parents,
        with oldfunc being the parent.drawkid as if we were not active in dynenv.
        """
        if 0:
            # this would be equiv to behavior we replace:
            oldfunc(kid)
            return
        # parent is a draw-parent of kid
        self._parents_lists.setdefault(kid, []).append(parent) #e could optim
        oldfunc(kid)
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
    def _drawkid_selective(self, oldfunc, parent, obj): ### CALL ME
        """This intercepts parent.drawkid(obj) when we're only drawing selected parents and leaf objects,
        with oldfunc being the parent.drawkid as if we were not active in dynenv.
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
            oldfunc(obj) ##k
        return
    pass
