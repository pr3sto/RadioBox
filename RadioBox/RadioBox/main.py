from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.selectableview import SelectableView
from kivy.adapters.listadapter import ListAdapter
from kivy.properties import ListProperty, StringProperty


class AddNewStationPopup(Popup):
    pass


class PlayerScreen(BoxLayout):
    def __init__(self, **kwargs):
        stations = [format(i+2) for i in range(10)]
        self.list_adapter = ListAdapter(data=stations, 
                                        args_converter=self.converter,
                                        selection_mode='single',
                                        allow_empty_selection=False,
                                        cls='ListViewItem')
        self.list_adapter.bind(on_selection_change=self.selection_change)
        super(PlayerScreen, self).__init__(**kwargs)  

    def selection_change(self, adapter, *args):
        if (adapter.selection):
            print "--------" 
            print adapter.selection
            print adapter.selection[0].is_selected
            print "--------"

    def converter(self, row_index, row_data):
        return {'row_index': row_index+1, 'text': row_data}    

    def add_new_station(self, *args):
        AddNewStationPopup().open()


class RadioBoxApp(App):
    def build(self):
        return PlayerScreen()


if __name__ == "__main__":
    Window.minimum_width = 400
    Window.minimum_height = 300
    Window.size = (500, 400)
    RadioBoxApp().run()
