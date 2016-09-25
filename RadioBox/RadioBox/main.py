import kivy
kivy.require('1.9.1')

#kivy components
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.adapters.listadapter import ListAdapter
from kivy.properties import StringProperty

# for playing streams
import vlc

# for working with stations
import stationutils


class AddNewStationPopup(Popup):
    def __init__(self, list_adapter, **kwargs):
        self.list_adapter = list_adapter
        self.is_add_from_file = False
        # bindings
        Window.bind(on_dropfile=self.on_file_drop)
        self.bind(on_dismiss=self.refresh_popup_content)
        
        super(AddNewStationPopup, self).__init__(**kwargs)
        # set default values
        self.refresh_popup_content()

    def add_new_station(self, name, url, *args):
        self.list_adapter.data.append(stationutils.Station(name, url))
        self.dismiss()
    
    def add_new_station_from_file(self, file_path, *args):
        stations = stationutils.get_stations_list_from_file(file_path)
        self.list_adapter.data.extend(stations)
        self.dismiss()

    def on_file_drop(self, window, file_path):
        if self.parent is not None:
            self.is_add_from_file = True
            self.ids.drop_file_text.text = file_path.decode('utf-8')
            self.ids.del_drop_file.disabled = False
            self.ids.name_box.disabled = True
            self.ids.url_box.disabled = True

    def refresh_popup_content(self, *args):
        self.is_add_from_file = False
        self.ids.drop_file_text.text = 'Drag and drop m3u file here'
        self.ids.del_drop_file.disabled = True
        self.ids.name_textinput.text = ''
        self.ids.url_textinput.text = ''
        self.ids.name_box.disabled = False
        self.ids.url_box.disabled = False


class ErrorMessagePopup(Popup):
    def __init__(self, error_messgage, **kwargs):
        self.error_message = error_messgage
        super(ErrorMessagePopup, self).__init__(**kwargs)


class PlayerScreen(FloatLayout):
    def __init__(self, list_adapter, **kwargs):
        self.list_adapter = list_adapter
        self.list_adapter.bind(on_selection_change=self.station_changed)
        super(PlayerScreen, self).__init__(**kwargs)  
        
        self.add_new_station_popup = None
        self.player = vlc.MediaPlayer()

    def station_changed(self, adapter, *args):
        if (adapter.selection):
            self.player.stop()
            self.player.set_mrl(adapter.selection[0].ids.ctx.url)
            self.player.get_media().event_manager().event_attach(
                vlc.EventType.MediaStateChanged, self.media_state_changed, adapter.selection[0].ids.ctx.name)
            self.player.play()
            Window.set_title('RadioBox - {0}'.format(adapter.selection[0].ids.ctx.name))

    def media_state_changed(self, event, name):
        if self.player.get_state() == vlc.State.Error:
            err_msg = 'Error playing stream \'{0}\''.format(name)
            ErrorMessagePopup(err_msg).open()

    def open_new_station_popup(self, *args):
        if self.add_new_station_popup is None:
            self.add_new_station_popup = AddNewStationPopup(self.list_adapter)
        self.add_new_station_popup.open()
    

class RadioBoxApp(App):
    def build(self):
        self.title = 'RadioBox'
        
        # set app directory path
        stationutils.radiobox_directory_path = self.user_data_dir
        
        # load stations
        saved_stations = stationutils.get_saved_stations_list()
        for i in range(len(saved_stations)):
            if saved_stations[i].name == '':
                saved_stations[i].name = 'station #{0}'.format(i+1)

        # create list adapter
        self.list_adapter = ListAdapter(
            data=saved_stations, 
            args_converter=self.converter,
            selection_mode='single',
            allow_empty_selection=True,
            cls='ListItem'
        )
        
        # create main screen
        ps = PlayerScreen(self.list_adapter)
        
        # bindings
        self.bind(on_stop=self.save_stations)       
        Window.minimum_width = 400
        Window.minimum_height = 300
        Window.size = (500, 400)
        
        return ps

    def converter(self, row_index, row_data):
        return {
            'row_number': row_index+1, 
            'name': row_data.name,
            'url': row_data.url
        }

    def save_stations(self, *args):
        stationutils.save_stations_list(self.list_adapter.data)


if __name__ == "__main__":
    RadioBoxApp().run()    
