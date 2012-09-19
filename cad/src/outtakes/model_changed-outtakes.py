    def selection_changed(self): #bruce 070925 [not used outside this file as of 080731, except in docstrings/comments]
        return

    def selobj_changed(self): #bruce 071116 [not mentioned outside this file as of 080731] 8
        return

    def view_changed(self): #bruce 071116 [not mentioned outside this file as of 080731]8
        return

    def something_changed(self): #bruce 071116 [not used outside this file as of 080731, except in comments]
        return








    def selection_changed(self): #bruce 070925 added this to Command API
        """
        Subclasses should extend this (or make sure their self.propMgr defines
        it) to check whether any selection state has changed that should be
        reflected in their UI, and if so, update their UI accordingly.

        """
        ### REVIEW: Decide whether highlighting (selobj) is covered by it
        # (guess yes -- all kinds of selection).
        ### maybe: call when entering/resuming the command, and say so,
        # and document order of call relative to update_gui. And deprecate
        # update_gui or make it more efficient. And add other methods that only
        # use usage-tracked state and are only called as needed.
        if self.propMgr:
            if hasattr( self.propMgr, 'selection_changed'):
                self.propMgr.selection_changed()
        return

    def selobj_changed(self):
        """
        Called whenever the glpane.selobj (object under mouse)
        may have changed, so that self can do UI updates in response to that.
        """
        if self.propMgr:
            if hasattr( self.propMgr, 'selobj_changed'):
                self.propMgr.selobj_changed()
        return

    def view_changed(self):
        """
        Called whenever the glpane's view (view center, direction, projection)
        may have changed, so that self can do UI updates in response to that.
        """
        # REVIEW: I'm not sure this gets called for Ortho/Perspective change,
        # but it should be! [bruce 071116]
        if self.propMgr:
            if hasattr( self.propMgr, 'view_changed'):
                self.propMgr.view_changed()
        return

    def something_changed(self):
        """
        Called once, immediately after any or all of the methods
        model_changed, selection_changed, selobj_changed, or view_changed
        were called.
        """
        if self.propMgr:
            if hasattr( self.propMgr, 'something_changed'):
                self.propMgr.something_changed()
        return

    _last_model_change_counter = None
    _last_selection_change_counter = None
    _last_selobj = -1 # not None, since that's a legal value of selobj
    _last_view_change_counter = None

    def state_may_have_changed_OBSOLETE(self): #bruce 070925 added this to command API; update 080731: WILL BE REVISED SOON
        """
        Call whichever we need to of the methods
        model_changed, selection_changed, selobj_changed, view_changed,
        in that order. The need is determined by whether the associated
        change counters or state has changed since this method
        (state_may_have_changed) was last called on self.

        Then if any of those was called, also call something_changed.
        This permits subclasses which just want to update after any change
        to define only one method, and be sure it's not called more than
        once per change. Or they can set specific change flags in the
        specific change methods, and then respond to those all at once
        or in a different order, in something_changed.

        Note: this method should not normally be overridden by subclasses.

        Note: the "only as needed" aspect is NIM, except when an
        experimental debug_pref is set, but it should become the usual case.

        FYI: This is called by env.do_post_event_updates() by a registered
        "post_event_ui_updater" set up by MWsemantics. [still true 080731]
        """
        if debug_pref("call model_changed (etc) only when needed?",
                      Choice_boolean_False,
                      ## non_debug = True,
                          #bruce 080416 hide this since the commands can't yet
                          # handle it properly, so it causes bugs
                          # (this change didn't make it into .rc2)
                      prefs_key = True):
            ### experimental, but will become the usual case soon [bruce 071116]:
            # call each method only when needed, using assy change counters, and a selobj test.
            counters = self.assy.all_change_counters()
            model_change_counter = counters[0] # MAYBE: make assy break them out for us?
            selection_change_counter = counters[1] # note: doesn't cover selobj changes
            view_change_counter = counters[2]
            selobj = self.glpane.selobj
            something_changed = False # will be updated if something changed

            # the following order must be maintained,
            # so that updating methods can assume it:

            if model_change_counter != self._last_model_change_counter:
                self._last_model_change_counter = model_change_counter
                self.model_changed()
                something_changed = True

            if selection_change_counter != self._last_selection_change_counter:
                self._last_selection_change_counter = selection_change_counter
                self.selection_changed()
                something_changed = True

            if selobj is not self._last_selobj:
                self._last_selobj = selobj
                self.selobj_changed() # will be renamed
                something_changed = True

            if view_change_counter != self._last_view_change_counter:
                self._last_view_change_counter = view_change_counter
                self.view_changed()
                something_changed = True

            if something_changed:
                self.something_changed()
            pass
        else:
            # current bad code: always call every method.
            self.model_changed()
            self.selection_changed()
            self.selobj_changed()
            self.view_changed()
            self.something_changed()
        return # end of an OBSOLETE method
