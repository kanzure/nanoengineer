'''
$Id$
'''

# as of 061106 the setup looks obs, but it might as well be revived and tested before Column is worked on much

class TestIterator(HelperClass):
    "simple iterator which makes two instances of the same WE arg"
    def _make(self, place):
        arg = self._e_args[0] # 061106 args -> _e_args (guess)
        self._define_kid(1, arg) # lexenvfunc can be default (identity), I think
        self._define_kid(2, arg)
        #####@@@@@ what about drawing coords? and layout? layout can be stubbed, but coords should differ.
        # do our kid instances even need to know about their coords? I doubt it.
        return
    def _move(self, kid1, kid2):
        "move between coords for kid1 (an index) and coords for kid2; either can be None to indicate self" ### guess, not yet called
        # algorithm: pretend we're Column, but in some trivial form.
        if kid1 is None: kid1 = 1
        if kid2 is None: kid2 = 1
        assert kid1 in (1,2) and kid2 in (1,2)
        glTranslate3fv(V((kid2 - kid1) * 2.0, 0, 0)) #####@@@@@
        return
    def draw(self):
        self._move(None, 1)
        self._draw_kid(1)
        self._move(1, 2)
        self._draw_kid(2)
        self._move(2, None) #k needed?
        return
    def _draw_kid(self, index):
        # might be in HelperClass
        self._kids[index].draw() # this might lazily create the kid, as self._kid_lvals[index].value or so
        return
    pass

goal1 = TestIterator(Rect(1,1,black))

goal2 = TestIterator(If(_enclosing_If.index[0] == 1, Rect(1,1,black), Rect(1,1,red))) #####@@@@@ _enclosing_If IMPLEM, part of lexenv

goal3 = TestIterator(ToggleShow(Rect(1,1,red))) # with a def for ToggleShow

# not reviewed recently, was part of NewInval
