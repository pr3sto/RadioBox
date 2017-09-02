import vlc
import urllib2
import threading


class Player:
    """Represent radio Player."""

    def __init__(self):
        self.vlc_player = vlc.MediaPlayer()
        self.current_station = None
        self.error_callback = None
        self.title_recieved_callback = None

    def play(self):
        """Play radio station if it is setted."""

        if self.vlc_player.get_media() is not None:
            self.vlc_player.play()

    def stop(self):
        """Stop radio station."""

        if self.is_playing():
            self.vlc_player.stop()

    def set_station(self, station):
        """Set station given in parameter.

        Args:
            station (Station): station to set.
        """

        self.current_station = station

        if self.is_playing():
            self.stop()
            self.vlc_player.set_mrl(self.current_station.url)
            self.vlc_player.get_media().event_manager().event_attach(
                vlc.EventType.MediaStateChanged, self._media_state_changed)
            self.play()
        else:
            self.vlc_player.set_mrl(self.current_station.url)
            self.vlc_player.get_media().event_manager().event_attach(
                vlc.EventType.MediaStateChanged, self._media_state_changed)

    def set_error_callback(self, callback):
        """Set callback when error appearin playing station.

        Args:
            callback (func): callback to set.
        """

        self.error_callback = callback

    def set_title_recieved_callback(self, callback):
        """Set callback when station title received.

        Args:
            callback (func): callback to set.
        """

        self.title_recieved_callback = callback

    def set_volume(self, value):
        """Set audio volume.

        Args:
            value (int): volume value.
        """

        if 0 <= value <= 100:
            self.vlc_player.audio_set_volume(value)

    def is_playing(self):
        """Is music playing.

        Returns:
            true - if music playing, false - otherwise.
        """

        return self.vlc_player.get_state() == vlc.State.Playing

    def get_stream_title(self):
        """Get radio stream title async. Calls title_recieved_callback when title received."""

        if self.is_playing():
            threading.Thread(target=self._get_stream_title_sync).start()

    def _media_state_changed(self, event):
        """Callback on state changed event.

        Args:
            event (Event): Event instance.
        """

        if self.vlc_player.get_state() == vlc.State.Error:
            if (self.error_callback is not None):
                self.error_callback(self.current_station.name)

    def _get_stream_title_sync(self):
        """Get radio stream title sync. Calls title_recieved_callback when title received."""

        request = urllib2.Request(self.current_station.url)
        request.add_header('Icy-MetaData', 1)

        try:
            response = urllib2.urlopen(request)
            icy_metaint_header = response.headers.get('icy-metaint')

            if icy_metaint_header is not None:
                metaint = int(icy_metaint_header)
                read_buffer = metaint+255
                content = response.read(read_buffer)
                title = content[metaint:].split("'")[1]

                if self.title_recieved_callback is not None:
                    self.title_recieved_callback(title)
            else:
                if self.title_recieved_callback is not None:
                    self.title_recieved_callback(' - ')
        except:
            if self.title_recieved_callback is not None:
                self.title_recieved_callback(' - ')
