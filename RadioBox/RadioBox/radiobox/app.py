from kivy.app import App
from kivy.core.window import Window
from kivy.adapters.listadapter import ListAdapter

from stationutils import StationUtils

from screens import PlayerScreen


class RadioBoxApp(App):
    """Main application class."""
    def build(self):
        self.title = 'RadioBox'

        # set app directory path
        StationUtils.radiobox_directory_path = self.user_data_dir

        # load stations
        saved_stations = StationUtils.get_saved_stations_list()
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
        self.bind(on_stop=self.save_stations_to_file)
        Window.minimum_width = 400
        Window.minimum_height = 300
        Window.size = (500, 400)

        return ps

    def converter(self, row_index, row_data):
        def delete_station(row_number):
            self.list_adapter.data.remove(self.list_adapter.data[row_number-1])
        return {
            'row_number': row_index+1,
            'name': row_data.name,
            'url': row_data.url,
            'func': delete_station
        }

    def save_stations_to_file(self, *args):
        StationUtils.save_stations_list(self.list_adapter.data)
