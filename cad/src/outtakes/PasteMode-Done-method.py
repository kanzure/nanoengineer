    def Done(self, new_mode = None, suspend_old_mode = False):
        """
        Decides what to do after exiting the mode. If mode is left by clicking 
        on B{Done} button it will enter the previous mode the user was in. 
        
        @example: User invokes Paste mode while in 'Move' mode, and then 
        hits 'Done' button in the Paste mode, NE1 leaves Paste mode and enters 
        Move mode again.
        
        If instead of Done button, user clicks on a button that invokes a different 
        mode, it enters the mode user asked for. 
        
        @param new_mode: New mode user wants to enter. (A value 'None' means the 
                         user didn't ask for any specific mode , so NE1 should 
                         enter the previous mode (before the paste mode) the
                         user was in.
        @type  new_mode: L{basicMode} or None
        
        @param suspend_old_mode: See L{basicMode.Done} it needs to be documented 
                                 there. Flag that decides whether to suspend the 
                                 old mode user was in. [Ignored by this method --
                                 is that correct? ### REVIEW]
        @type  suspend_old_mode: boolean
        """
        resuming = False
        if new_mode is None:
            try:
                new_mode = self.o.prevMode
                resuming = True
            except:
                pass
        return depositMode.Done(self, new_mode, resuming = resuming)


and the one from Zoom/Rotate/Pan was essentially equivalent:


    # a safe way for now to override Done:
    def Done(self, new_mode = None):
        """
        [overrides basicMode.Done; this is deprecated, so doing it here
        is a temporary measure for Alpha, to be reviewed by Bruce ASAP after
        Alpha goes out; see also the removal of Done from weird_to_override
        in modes.py. [bruce and mark 050130]
        """
        ## [bruce's symbol to get him to review it soon: ####@@@@]
        resuming = False
        if new_mode is None:
            try:
                m = self.glpane.prevMode
                new_mode = m
                resuming = True
            except:
                pass

        #bruce 070813 added resuming arg
        return basicMode.Done(self, new_mode, resuming = resuming)

        
these have been subsumed by new behavior in default implem of Done, and/or something it calls in self or modeMixin.
