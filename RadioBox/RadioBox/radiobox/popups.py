from kivy.uix.popup import Popup
from kivy.core.window import Window

from stationutils import *


class AddNewStationPopup(Popup):
    """Popup for adding new stations."""

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
        self.list_adapter.data.append(Station(name, url))
        self.dismiss()

    def add_new_station_from_file(self, file_path, *args):
        stations = StationUtils.get_stations_list_from_file(file_path)
        self.list_adapter.data.extend(stations)
        self.dismiss()

    def on_file_drop(self, window, file_path):
        if self.parent is not None:
            self.is_add_from_file = True
            self.ids.drop_file_text.text = file_path.decode('utf-8')
            self.ids.del_drop_file.disabled = False
            self.ids.name_box_layout.disabled = True
            self.ids.url_box_layout.disabled = True

    def refresh_popup_content(self, *args):
        self.is_add_from_file = False
        self.ids.drop_file_text.text = 'Drag and drop m3u file here'
        self.ids.del_drop_file.disabled = True
        self.ids.name_text_input.text = ''
        self.ids.url_text_input.text = ''
        self.ids.name_box_layout.disabled = False
        self.ids.url_box_layout.disabled = False


class ErrorMessagePopup(Popup):
    """Popup with error message."""

    def __init__(self, error_messgage, **kwargs):
        self.error_message = error_messgage
        super(ErrorMessagePopup, self).__init__(**kwargs)
