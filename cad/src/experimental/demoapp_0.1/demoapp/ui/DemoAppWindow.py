"""
DemoAppWindow.py

$Id$
"""

import pyglet

from pyglet.gl import *

from pyglet import font

from demoapp.tools.TrivalentGraphDrawingTool import TrivalentGraphDrawingTool

from demoapp.tools.DeleteNodeTool import DeleteNodeTool

from demoapp.models.TrivalentGraphModel import TrivalentGraphModel

from demoapp.widgets.controls import TextButton
from demoapp.widgets.ChildHolder import EventDistributorToChildren

from pyglet.window import key

from demoapp.geometry.vectors import A, V

# ==

class AppWindow(pyglet.window.Window): ## REFILE
    # tooltip text object [modified from soundspace.py]
    # todo: on main window only, not every pane
    # todo: put text into a nice rectangle with translucent bg color
    # todo: user pref to position it, rel to object or in std corner of screen or in user-movable window
    _tip_text_object = font.Text(font.load('', 10),
                                      '',
                                      color = (0, 0, 0, 1),
                                      halign = 'center',
                                      valign = 'top' )
        # note: self._tip_text_object.text gets reset by other code as needed;
        # tip .x .y get reset as part of drawing it
    def draw_tip_and_highlight(self, stuff, instance):
        try:
            if type(stuff) == type([]):
                for thing in stuff:
                    self.draw_tip_and_highlight(thing, instance)
            elif type(stuff) == type(()):
                # a drawing cmd desc...
                ## name, args = stuff[0], stuff[1:]
                name, args = stuff ## nonstandard structure, args already a tuple... change? put in a class? #####DECIDE
                method = getattr(instance, name)
                ## print "draw_tip_and_highlight got method %r for args %r len %d" % (method, args, len(args))
                method(*args)
                    # this can indirectly call e.g. self.draw_tooltip_text
            return
        except:
            print "following exception is in x.draw_tip_and_highlight(%r, %r):" % \
                  (stuff, instance)
            raise
        pass
    def draw_tooltip_text( self, text, pos, size):
        #doc
        # todo: use size
        text_object = self._tip_text_object
        if text_object.text != text:
            text_object.text = text
        text_object.x, text_object.y = pos + V(10, -20) # assume LL corner of text
            # GUESS and stub;
            # maybe be smarter, let caller pass offset directions to avoid;
            # future: transform from model to pane coords
        text_object.draw()
    pass

## from pyglet.event import EVENT_HANDLED
##class controls_handler(object): # OBS?
##    def __init__(self, window, attr):
##        self.window = window
##        self.attr = attr
##    @property
##    def controls(self):
##        return getattr(self.window, self.attr)
##    def on_mouse_press(self, x, y, button, modifiers):
##        ### BUG from when this was in self.window: [### TEST if fixed now]
##        # it was never called, since tool covers this area, captures all mouse presses...
##        # how can we divide self into panes and give them separate handlers? ####
##        # (and colors, so we can see the white controls on the bottom.)
##        for control in self.controls:
##            if control.hit_test(x, y):
##                if control.on_mouse_press(x, y, button, modifiers):
##                    return EVENT_HANDLED
##        return None
##    pass

class ToolPane(pyglet.event.EventDispatcher):
    x = y = 0 # KLUGE, hides some bugs -- opengl and tooltip drawing need transforms #####
    model = None
    event_types = list(pyglet.window.Window.event_types) # kluge?
    _last_tool = None
    def __init__(self, parent):
        self.parent = parent
    def find_object(self, x, y, excluding = ()):
        for obj in self.model.hit_test_objects():
            if obj.hit_test(x, y) and not obj in excluding:
                return obj
        return None
    def draw_tip_and_highlight(self, stuff, instance):
        return self.parent.draw_tip_and_highlight(stuff, instance)
    def draw_tooltip_text(self, text, pos, size):
        return self.parent.draw_tooltip_text(text, pos, size)
    def set_tool(self, tool):
        if self._last_tool:
            self._last_tool.deactivate()
        self._last_tool = tool
        tool.activate()
    pass

ToolPane.register_event_type('on_draw_handle')


class DemoAppWindow(AppWindow):
    GUI_WIDTH = 400
    GUI_HEIGHT = 40
    GUI_PADDING = 4
    GUI_BUTTON_HEIGHT = 16
    def __init__(self, *args, **kws):
        super(DemoAppWindow, self).__init__(*args, **kws)
        toolpane = ToolPane(self)
        toolpane.model = TrivalentGraphModel()
        self.tool1 = TrivalentGraphDrawingTool(toolpane)
        self.tool2 = DeleteNodeTool(toolpane)
        # done in gui_update_state:
        ## toolpane.set_tool(tool1) # this activates the tool
        self.toolpane = toolpane

        self.children_besides_controls = [toolpane] # not counting self.controls... (kluge)
        self._event_distributor = EventDistributorToChildren(self.find_child) # finds both kinds of children
        self.push_handlers( self._event_distributor)

        ## self.push_handlers(tool) # todo: more than one tool, let them be alternative states...
            # if the tools have substates (as they do), they may need a fake whole-tool event handler
            # to remain in each of those states, just so they can know how to remove themselves in the end.
            # or we may need a new feature to remove a specific handler-frame...
            # actually this is not hard -- the tool knows its state, so it knows what handler to remove.
            # maybe the tool is two handler frames (self and its state), that's ok too.
            #
            # nim: GraphSelectionTool
##        self.controls_handler = controls_handler(self, 'controls') # sees self.controls
##        self.push_handlers(self.controls_handler)

        # view transform [modified from soundspace.py] ###@@@ USE ME
        self.zoom = 40 # pixels per unit
        self.tx = self.width/2 #k review: 2.0?
        self.ty = self.height/2

        # from controls.py test code, aka media_player.py pyglet example code
        self.play_pause_button = TextButton(self)
        self.play_pause_button.x = self.GUI_PADDING
        self.play_pause_button.y = self.GUI_PADDING
        self.play_pause_button.height = self.GUI_BUTTON_HEIGHT
        self.play_pause_button.width = 45
        self.play_pause_button.on_press = self.on_play_pause

        win = self
        self.window_button = TextButton(self)
        self.window_button.x = self.play_pause_button.x + \
                               self.play_pause_button.width + self.GUI_PADDING
        self.window_button.y = self.GUI_PADDING
        self.window_button.height = self.GUI_BUTTON_HEIGHT
        self.window_button.width = 90
        self.window_button.text = 'Windowed'
        self.window_button.on_press = lambda: win.set_fullscreen(False)

        self.controls = [
            # self.slider, 
            self.play_pause_button, # demo
            self.window_button, # useful
        ]

        x = self.window_button.x + self.window_button.width + self.GUI_PADDING
        i = 0
        for screen in self.display.get_screens():
            screen_button = TextButton(self)
            screen_button.x = x
            screen_button.y = self.GUI_PADDING
            screen_button.height = self.GUI_BUTTON_HEIGHT
            screen_button.width = 80
            screen_button.text = 'Screen %d' % (i + 1)
            screen_button.on_press = \
                (lambda s: lambda: win.set_fullscreen(True, screen=s))(screen)
            self.controls.append(screen_button)
            i += 1
            x += screen_button.width + self.GUI_PADDING
            break ### KLUGE -- avoid bug, 2nd screen button on my silver mac gets this when tried:
                # CarbonException: invalid drawable

        self.gui_update_state()

    def find_child(self, x, y):
        if 1:
            # this was causing a bug with drags:
            # - the controls already got these events from their capture_events pushed handler [fix: it's disabled]
            #   - which failed to return EVENT_HANDLED [fixed]
            # - then this makes EventDistributor give them the events [still true], but with transformed coords [fixed]
            #   which they don't want (maybe that should be an option for children, F for them).
            # BUT this is required for them to feel the press in front of the tool. [080616 714p; fixed 930p]
            for control in self.controls:
                if control.hit_test(x, y):
                    return control
        #e could test y, no real need; should generalize the following
        assert len(self.children_besides_controls) == 1
        return self.children_besides_controls[0]

    def gui_update_state(self):
        if self.playing:
            self.play_pause_button.text = 'Tool2'
            self.toolpane.set_tool(self.tool2)
        else:
            self.play_pause_button.text = 'Tool1'
            self.toolpane.set_tool(self.tool1)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.on_play_pause()
        elif symbol == key.ESCAPE:
            self.dispatch_event('on_close')

    def on_close(self):
        self.close()

    playing = False
    def on_play_pause(self):
        if self.playing:
            self.playing = False
        else:
            self.playing = True
        self.gui_update_state()

    def on_draw(self):
        glClearColor(0.95, 0.95, 0.95, 1)
        ## glClearColor(1, 1, 1, 1) # see if this fixes button text color -- nope.
        
        self.clear()
        ## self.model.draw()
        for child in self.children_besides_controls:
            child.model.draw() ### BUG: WRONG COORDS ### REFACTOR, child.draw do this
            child.dispatch_event('on_draw_handle') # my own event, to draw the handle rubberbands etc for the ones that need that
        ## call the drawing functions of the handlers on the stack?? have a "draw overlay event" they can pass down?
        # issue: they probably want to call the behind-stuff recursively...

        for control in self.controls:
            control.draw()
        return

    pass

# end

