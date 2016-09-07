from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

class PlayerScreen(BoxLayout):
    pass

class RadioBoxApp(App):
    def build(self):
        return PlayerScreen()

if __name__ == "__main__":
    from kivy.core.window import Window
    Window.minimum_width = 400
    Window.minimum_height = 300
    Window.size = (500, 400)

    RadioBoxApp().run()