from kivy.uix.button import Button

from behaviors import HoverBehavior


class HoverButton(Button, HoverBehavior):
    """Button with hover events."""

    def __init__(self, **kwargs):
        super(HoverButton, self).__init__(**kwargs)
