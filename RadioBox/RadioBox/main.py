import kivy
kivy.require('1.10.0')

from radiobox import HoverBehavior
kivy.factory.Factory.register('HoverBehavior', HoverBehavior)

from radiobox import RadioBoxApp
if __name__ == "__main__":
    RadioBoxApp().run()
