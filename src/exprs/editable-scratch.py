"""
$Id$
"""


SimpleInsertCommand(Cylinder) -> something to put in a toolbar which can insert a Cylinder
it queries Cylinder for its args etc, as name/type pairs

Cylinder(__fakeopt__ = True)._e_query_args() -> list of Arg etc exprs

for example, Arg(type, dflt_expr, doc = ...)

(which we turn into a new kind of toplevel expr; not sure it can be instantiated; but it has a meaning)

Stateful(Cylinder) -> something that turned Cyl's args/opts into StateArgs; options control whether state can be a formula...
note for an ArgFormula we really have two levels of formula, one the real one and one the computed formula from that;
can it be computed by simplification? sometimes yes, but not only. eg it might be computed by being looked up in a file.

Editable(Stateful(Cylinder)) -- not sure what that means; does it mean adding a UI interface for editing the state it has?
or permitting one to be added, or autoadded, in the right context?

Editable(Arg(...)) -- any meaning?
Editable(State(...))

State(Editable(int), ...)

not sure if those have any meaning --- what is something not normally editable that we can make editable??
then editable(x) for that kind of x might have a meaning.

SimplePropertyManager(Cylinder) -> ...




class SimplePropertyManager(DelegatingInstanceOrExpr):
    # args
    forwhat = Arg(Type, doc = "the type of thing we are a property view/edit interface for")
        # is a pure expr turned into an Instance of Type?? guess: yes. not sure how that can be semantically clean. ###REVIEW
    # formulae
    delegate = MapListToExpr( _self.editfield_for_parameter,
                              forwhat.parameters,
                              KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleColumn) )
    def _CV_editfield_for_parameter(self, parameter):
        ###k _CV_ correct here?? and can we return expr and have it made? _CVE_ for that??
        ##e or does MapListToExpr do the make if needed?? if not, should it?
        return parameter.type.standard_editfield ### ???
        ###e even if so, doesn't it need some args? it needs some state to modify...
        # and something needs a way to make one of these things or get the user to find one...
        
    pass

nim in above:
- the coercion from expr to Instance of Type;
- the exprs (like Arg, but lots more) that need to appear in type1.parameters;
- parameter.type.standard_editfield with unspecified further args
- something unsaid above that can make a new thing of type forwhat --
  - and worse, can make it of Stateful(forwhat) if forwhat doesn't have state, or doesn't have enough (unclear)
  - and decisions of whether the state can be formulae

class SimpleInsertCommand(InstanceOrExpr):
    ##k super? should say the general type of command (so as to imply the interface we meet) -- CommandTool?????
    """Be an insert command for a given type, with a SimplePropertyManager for it,
    and the semantics of an insert command,
    and the metainfo which (when we are registered) leads a UI constructor to think it natural for us
    to have a toolbutton on an appropriate Insert toolbar/menu depending on the type of thing we insert
    and the type of parent (i mean container, not sure if that should be called parent) it might need
    (eg as a Line needs a Sketch, so should be on its flyout toolbar).
       Design Q: if we want to use this to do part of the work of making InsertPolyline,
    how do we mix it with the rest of work (incl a lot of Python methods)?
    - Can we subclass a customized expr? (not in a normal way anyway, though it might be possible and might make some sense)
    - Can we subclass it, and give values for its arg?
    - Can we add options that manage to make all additions/changes needed?
    - Should we delegate to it from something that adds its own outer layer? If so, how does outer thing
    modify the PM this makes, if it wants to modify its description before making it, but not by a lot?
    Can it customize an expr for it in a way that revises/groups/removes/reorders fields??
    """
    ###k Ambiguity: are our Instances permanent commands, or CommandRuns? Is CommandRun something generic with Command as arg???
    ### This relates to recent model/view separation discussions (with CommandRun of a command like one view of a model obj).
    # args
    forwhat = Arg(Type, doc = "the type of thing we are a simple insert command for")
    #
    property_manager = SimplePropertyManager( forwhat) ###e also pass a World, or an App (eg for prefs & selection state & world)?
        ###e maybe there is something in between -- much smaller than an App, sort of like an EditableModel... with sel state, history...
    toolname = "Insert " + forwhat.type_nickname ###WRONG if same button also edits
        ###e or cmdname, like for Undo -- varies depending, if we can act as Insert Line or Edit Line depending...
        #e also featurename?
    #e maybe some metainfo to help it get classified (for tool placement in UI)?
    # eg "Insert" (tho same button might also edit...)
    # eg topical stuff found from forwhat
    # eg this is a way of making type forwhat and a way of using types x,y,z which are major args to forwhat
    pass

