from demoapp.graphics.colors import thin_rubberband_color

from demoapp.geometry.vectors import A, get_pos, pos_and_size_from_obj_or_pos

class HighlightGraphics: # maybe rename
    """
    Subclasses implement the kinds of tooltip and highlight graphics needed by
    specific kinds of tools.
    """
    # subclasses can override these constants
    _default_obj_size = 5
    rubber_object_color = thin_rubberband_color
    def __init__(self, tool):
        self.tool = tool
    def _draw_tooltip_text(self, text, pos, size):
        """
        text is meant to be near an object (existing or potential)
        which is at position pos with size size
        """
        self.tool.pane.draw_tooltip_text( text, pos, size)
    def tip_text(self, text, obj_or_pos):
        pos, size = pos_and_size_from_obj_or_pos( obj_or_pos, default_size = self._default_obj_size)
        self._draw_tooltip_text( text, pos, size)
    pass
