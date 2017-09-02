import kivy
kivy.require('1.10.0')

# kivy components
from kivy.app import App
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.adapters.listadapter import ListAdapter
from kivy.properties import BooleanProperty, ObjectProperty

# execute func by timer
import sched, time
import threading

from stationutils import *
from player import *


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
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
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

    def on_enter(self):
        pass

    def on_leave(self):
        pass


from kivy.factory import Factory
Factory.register('HoverBehavior', HoverBehavior)


class HoverButton(Button, HoverBehavior):
    def __init__(self, **kwargs):
        super(HoverButton, self).__init__(**kwargs)


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
        self.list_adapter.bind(on_selection_change=self.change_station)
        super(PlayerScreen, self).__init__(**kwargs)

        self.add_new_station_popup = None

        self.player = Player()
        self.player.set_volume(50)
        self.player.set_error_callback(self._show_error)
        self.player.set_title_recieved_callback(self._update_title)

        self.is_playing = property()
        self.is_playing = self.is_playing.getter(self.player.is_playing)

        self.title_update_sheduler = sched.scheduler(time.time, time.sleep)

    def open_new_station_popup(self, *args):
        if self.add_new_station_popup is None:
            self.add_new_station_popup = AddNewStationPopup(self.list_adapter)
        self.add_new_station_popup.open()

    def change_station(self, adapter, *args):
        if (adapter.selection):
            self.player.set_station(adapter.selection[0].ids.ctx)
            Window.set_title('RadioBox - {0}'.format(adapter.selection[0].ids.ctx.name))

    def change_state(self):
        if self.player.is_playing():
            self.player.stop()
            for event in self.title_update_sheduler.queue:
                self.title_update_sheduler.cancel(event)
        else:
            self.player.play()
            threading.Thread(target=self.update_title_launch).start()

    def change_volume(self, volume):
        self.player.set_volume(int(volume))

    def update_title_launch(self):
        self.title_update_sheduler.enter(5, 1, self._update_title_loop, ())
        self.title_update_sheduler.run()

    def _update_title_loop(self):
        self.player.get_stream_title()
        self.title_update_sheduler.enter(5, 1, self._update_title_loop, ())

    def _show_error(self, stream_name):
        err_msg = 'Error playing stream \'{0}\''.format(stream_name)
        ErrorMessagePopup(err_msg).open()

    def _update_title(self, title):
        self.ids.title_text.text = title


class RadioBoxApp(App):
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
            'f': delete_station
        }

    def save_stations_to_file(self, *args):
        StationUtils.save_stations_list(self.list_adapter.data)


if __name__ == "__main__":
    RadioBoxApp().run()
