import vlc

class Player:
    def __init__(self):
        self.vlc_player = vlc.MediaPlayer()
        self.current_station = None
        self.error_callback = None

    def play(self):
        self.vlc_player.play()

    def stop(self):
        self.vlc_player.stop()

    def set_station(self, station):
        self.current_station = station        

        if self.vlc_player.get_state() == vlc.State.Playing:
            self.stop()
            self.vlc_player.set_mrl(self.current_station.url)
            self.vlc_player.get_media().event_manager().event_attach(
                vlc.EventType.MediaStateChanged, self.media_state_changed)
            self.play()
        else:
            self.vlc_player.set_mrl(self.current_station.url)
            self.vlc_player.get_media().event_manager().event_attach(
                vlc.EventType.MediaStateChanged, self.media_state_changed)
        
    def set_error_callback(self, callback):
        self.error_callback = callback

    def media_state_changed(self, event):
        if self.vlc_player.get_state() == vlc.State.Error:
            if (self.error_callback is not None):
                self.error_callback(self.current_station.name)
