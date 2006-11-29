"""
DisplistChunk.py

$Id$
"""

from lvals import Lval ##reloadable

##e during devel -- see also some comments in lvals-outtakes.py (not in cvs)

class LvalForDisplistEffects(Lval): #stub -- see NewInval.py and paper notes; might put this in another file since it depends on OpenGL
    """Lval variant, for when the value in question is the total drawing effect of calling an OpenGL display list
    (which depends not only on the OpenGL commands in that display list, but on those in all display lists it calls,
    directly or indirectly).
       [The basic issues are the same as if the effect was of running an external subroutine, in a set of external subrs
    whose code we get to maintain, some of which call others. But there are a lot of OpenGL-specific details which affect
    the implementation. The analogous things (external Qt widgets, POV-Ray macros) are like that too, so it's unlikely
    a common superclass LvalForThingsLikeExternalSubroutines would be useful.]
    """
    def _compute_value(self):
        "[unlike in superclass Lval, we first make sure all necessary display list contents are up to date]"
        pass
    pass


##DelegatingWidget3D
DelegatingWidget # 2D or 3D -- I hope we don't have to say which one in the superclass! ###
# Can the Delegating part be a mixin? Even if it is, we still have to avoid having to say the 2D or 3D part... ###

class DisplistChunk(DelegatingWidget):
    def _init_instance(self):
        DelegatingWidget._init_instance(self)
        instance_of_arg1 # what is this? it needs to be set up by the prior statement, or by that time... see our make_in code... ###
        # allocate display list and its lval
        LvalForDisplistEffects # do what with this class? see below
        #e or could use _C_ rule for this kid-object, so it'd be lazy... but don't we need to pass it instantiation context? ####
        self.displist_lval = LvalForDisplistEffects( instance_of_arg1 )
        ####@@@@ like CLE, do we need to actually make one displist per instance of whatever we eval arg1 to??
        # problem is, there's >1 way to do that... so for now, assume no.
        pass
    def draw(self):
        """compile a call to our display list
        in a way which depends on whether we're compiling some other display list right now, in self.env.glpane --
        how to do that is handled by our displist owner / displist effects lval
        """
        self.displist_lval.call_displist() # this will call instance_of_arg1.draw() if it needs to compile that displist
    pass
