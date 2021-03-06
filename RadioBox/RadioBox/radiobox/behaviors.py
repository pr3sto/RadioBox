from kivy.properties import BooleanProperty, ObjectProperty
from kivy.core.window import Window


class HoverBehavior(object):
    """Hover behavior.
    :Events:
        `on_enter`
            Fired when mouse enter the box of the widget.
        `on_leave`
            Fired when the mouse exit the widget
    """

    hovered = BooleanProperty(False)
    border_point= ObjectProperty(None)
    '''Contains the last relevant point received by the Hoverable. This can
    be used in `on_enter` or `on_leave` in order to know where was dispatched the event.
    '''

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self._on_mouse_pos)
        Window.bind(on_cursor_leave=self._on_cursor_leave)
        super(HoverBehavior, self).__init__(**kwargs)

    def _on_mouse_pos(self, *args):
        if not self.get_root_window():
            return # do proceed if I'm not displayed <=> If have no parent
        pos = args[1]
        # next line to_widget allow to compensate for relative layout
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            # we have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

    def _on_cursor_leave(self, *args):
        if (self.hovered):
            self.hovered = False
            self.dispatch('on_leave')

    def on_enter(self):
        pass

    def on_leave(self):
        pass
