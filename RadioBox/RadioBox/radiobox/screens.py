from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window

# execute func by timer
import sched, time, threading

from player import Player

from popups import AddNewStationPopup, ErrorMessagePopup


class PlayerScreen(FloatLayout):
    """Main screen of player."""
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
