import vlc
import urllib2
import threading


class Player:
    """Represent radio Player."""

    def __init__(self):
        self.vlc_player = None
        self.error_callback = None
        self.title_recieved_callback = None
        self.media_state_changed_callback = None
        self._init_vlc_player()

    def _init_vlc_player(self):
        """Init player instance."""

        if self.vlc_player is not None:
            self.vlc_player.release()

        self.vlc_player = vlc.MediaPlayer()
        self.current_station = None

        if self.media_state_changed_callback is not None:
            self.media_state_changed_callback(self.vlc_player.get_state())

    def _media_state_changed(self, event):
        """Callback on state changed event.

        Args:
            event (Event): Event instance.
        """

        if self.vlc_player is not None and self.media_state_changed_callback is not None:
            self.media_state_changed_callback(self.vlc_player.get_state())

        if self.vlc_player is not None and self.vlc_player.get_state() == vlc.State.Error:
            if (self.error_callback is not None):
                if self.current_station is not None:
                    self.error_callback('Error playing stream \'{0}\''.format(self.current_station.name))
                else:
                    self.error_callback('Unknown error')

    def _get_stream_title_sync(self):
        """Get radio stream title sync. Calls title_recieved_callback when title received."""

        if self.current_station is None:
            return

        request = urllib2.Request(self.current_station.url)
        request.add_header('Icy-MetaData', 1)

        try:
            response = urllib2.urlopen(request)
            icy_metaint_header = response.headers.get('icy-metaint')
            icy_description_header = response.headers.get('icy-description')

            if icy_metaint_header is not None:
                metaint = int(icy_metaint_header)
                read_buffer = metaint+255
                content = response.read(read_buffer)
                title = content[metaint:].split("'")[1].encode('utf8')

                if self.title_recieved_callback is not None:
                    self.title_recieved_callback(title)
            elif icy_description_header is not None:
                if self.title_recieved_callback is not None:
                    self.title_recieved_callback(icy_description_header.encode('utf8'))
            else:
                if self.title_recieved_callback is not None:
                    self.title_recieved_callback(' - ')
        except:
            if self.title_recieved_callback is not None:
                self.title_recieved_callback(' - ')

    def is_playing(self):
        """Is music playing.

        Returns:
            true - if music playing, false - otherwise.
        """

        if self.vlc_player is None:
            self._init_vlc_player()

        return self.vlc_player.get_state() == vlc.State.Playing

    def play(self):
        """Play radio station if it is setted."""

        if self.vlc_player is None:
            self._init_vlc_player()

        if self.vlc_player.get_media() is not None:
            self.vlc_player.play()

    def stop(self):
        """Stop radio station."""

        if self.vlc_player is None:
            self._init_vlc_player()

        if self.is_playing():
            self.vlc_player.stop()

    def set_station(self, station):
        """Set station given in parameter.

        Args:
            station (Station): station to set.
        """

        self.current_station = station

        if self.current_station is None:
            self._init_vlc_player()
        else:
            if self.vlc_player is None:
                self._init_vlc_player()

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

    def set_volume(self, value):
        """Set audio volume.

        Args:
            value (int): volume value.
        """

        if 0 <= value <= 100:
            if self.vlc_player is None:
                self._init_vlc_player()

            self.vlc_player.audio_set_volume(value)

    def get_stream_title(self):
        """Get radio stream title async. Calls title_recieved_callback when title received."""

        if self.is_playing():
            threading.Thread(target=self._get_stream_title_sync).start()

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

    def set_media_state_changed_callback(self, callback):
        """Set callback when media state changed.

        Args:
            callback (func): callback to set.
        """

        self.media_state_changed_callback = callback
