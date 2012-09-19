# == old comments, might be useful (e.g. the suggested formulas involving in_drag)

# I don't think Local and If can work until we get WEs to pass an env into their subexprs, as we know they need to do ####@@@@

# If will eval its cond in the env, and delegate to the right argument -- when needing to draw, or anything else
# Sensor is like Highlightable and Button code above
# Overlay is like Row with no offsetting
# Local will set up more in the env for its subexprs
# Will they be fed the env only as each method in them gets called? or by "pre-instantiation"?

##def Button(plain, highlighted, pressed_inside, pressed_outside, **actions):
##    # this time around, we have a more specific API, so just one glname will be needed (also not required, just easier, I hope)
##    return Local(__, Sensor( # I think this means __ refers to the Sensor() -- not sure... (not even sure it can work perfectly)
##        0 and Overlay( plain,
##                 If( __.in_drag, pressed_outside),
##                 If( __.mouseover, If( __.in_drag, pressed_inside, highlighted )) ),
##            # what is going to sort out the right pieces to draw in various lists?
##            # this is like "difference in what's drawn with or without this flag set" -- which is a lot to ask smth to figure out...
##            # so it might be better to just admit we're defining multiple different-role draw methods. Like this: ###@@@
##        DrawRoles( ##e bad name
##            plain, dict(
##                in_drag = pressed_outside, ### is this a standard role or what? do we have general ability to invent kinds of extras?
##                mouseover = If( __.in_drag, pressed_inside, highlighted ) # this one is standard, for a Sensor (its own code uses it)
##            )),
##        # now we tell the Sensor how to behave
##        **actions # that simple? are the Button actions so generic? I suppose they might be. (But they'll get more args...)
##    ))

# == old code

if 0:

    Column(
      Rect(1.5, 1, red),
      ##Button(Overlay(TextRect(18, 3, "line 1\nline 2...."),Rect(0.5,0.5,black)), on_press = print_Expr("zz")),
          # buggy - sometimes invis to clicks on the text part, but sees them on the black rect part ###@@@
          # (see docstring at top for a theory about the cause)

    ##                  Button(TextRect(18, 3, "line 1\nline 2...."), on_press = print_Expr("zztr")), #
    ##                  Button(Overlay(Rect(3, 1, red),Rect(0.5,0.5,black)), on_press = print_Expr("zzred")), # works
    ##                  Button(Rect(0.5,0.5,black), on_press = print_Expr("zz3")), # works
      Invisible(Rect(0.2,0.2,white)), # kluge to work around origin bug in TextRect ###@@@
      Ribbon2(1, 0.2, 1/10.5, 50, blue, color2 = green), # this color2 arg stuff is a kluge
      Highlightable( Ribbon2(1, 0.2, 1/10.5, 50, yellow, color2 = red), sbar_text = "bottom ribbon2" ),
      Rect(1.5, 1, green),
      gap = 0.2
    ## DrawThePart(),
    )

    # ... FilledSquare(color, color) ...

    Closer(Column(
        Highlightable( Rect(2, 3, pink),
                       # this form of highlight (same shape and depth) works from either front or back view
                       Rect(2, 3, orange), # comment this out to have no highlight color, but still sbar_text
                       # example of complex highlighting:
                       #   Row(Rect(1,3,blue),Rect(1,3,green)),
                       # example of bigger highlighting (could be used to define a nearby mouseover-tooltip as well):
                       #   Row(Rect(1,3,blue),Rect(2,3,green)),
                       sbar_text = "big pink rect"
                       ),
        #Highlightable( Rect(2, 3, pink), Closer(Rect(2, 3, orange), 0.1) ) # only works from front
            # (presumably since glpane moves it less than 0.1; if I use 0.001 it still works from either side)
        Highlightable( # rename? this is any highlightable/mouseoverable, cmenu/click/drag-sensitive object, maybe pickable
            Rect(1, 1, pink), # plain form, also determines size for layouts
            Rect(1, 1, orange), # highlighted form (can depend on active dragobj/tool if any, too) #e sbar_text?
            # [now generalize to be more like Button, but consider it a primitive, as said above]
            # handling_a_drag form:
            If( True, ## won't work yet: lambda env: env.this.mouseoverme , ####@@@@ this means the Highlightable -- is that well-defined???
                Rect(1, 1, blue),
                Rect(1, 1, lightblue) # what to draw during the drag
            ),
            sbar_text = "little buttonlike rect"
        )
    ))

# see also:
## ToggleShow-outtakes.py: 48:         on_press = ToggleAction(stateref)

