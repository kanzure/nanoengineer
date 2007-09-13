$Id$


## DraggableHandle(appearance = whatever, behavior = whatever, dragged_position = whatever)



    # formulae
    drag_behavior = Option( DragBehavior, SimpleDragBehavior,
                           doc = "our drag behavior (not including a stateref to dragged position)")
    state = Option(StateRef, None,
                   doc = "ref to the position-related state which dragging us should change, according to our drag_behavior") ###k
    _value = Highlightable( appearance, drag_behavior = drag_behavior(state) ) ###k
    pass
