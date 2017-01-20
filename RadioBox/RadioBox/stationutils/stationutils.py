import os


class Station:
    """Represent radio station

    Args:
        name (str): name of radio station.
        url (str): url of radio station.
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url


class StationUtils:
    radiobox_directory_path = ''
    radiobox_stations_save_file_name = 'stations.m3u'

    @staticmethod
    def _get_stations_save_file_path():
        """Forms path to stations file.
    
        Returns:
            path to stations file as string.
        """

        # create if not exist
        if not os.path.exists(StationUtils.radiobox_directory_path):
            os.makedirs(StationUtils.radiobox_directory_path)
        # full path to file
        stations_file_path = os.path.join(StationUtils.radiobox_directory_path, StationUtils.radiobox_stations_save_file_name)

        return stations_file_path

    @staticmethod
    def get_saved_stations_list():
        """Gets list of saved stations from save file.
    
        Returns:
            list of Station objects.
        """

        return StationUtils.get_stations_list_from_file(StationUtils._get_stations_save_file_path())

    @staticmethod
    def get_stations_list_from_file(stations_file_path):
        """Gets list of stations from given file.
    
        Args:
            stations_file_path (str): path to m3u file.

        Returns:
            list of Station objects.
        """

        stations = []
        try:
            with open(stations_file_path, 'r') as f:
                while True:
                    line = f.next().strip()
                
                    if line == '':
                        continue
                    # m3u header
                    elif '#EXTM3U' in line:
                        continue
                    # url with info (example: #EXTINF:duration,title)
                    elif '#EXTINF' in line:
                        url = f.next().strip()
                        stations.append(
                            Station(
                                line.replace("#EXTINF:", "").split(',', 1)[1],
                                url
                            )
                        )
                    # url without info
                    else:
                        stations.append(Station('', line))
        except StopIteration:
            return stations
        except IOError:
            return []

    @staticmethod
    def save_stations_list(stations):
        """Saves stations to save file.
    
        Args:
            stations (list(Station)): list of Station objects.
        """

        try:
            with open(StationUtils._get_stations_save_file_path(), 'w') as f:
                f.write('#EXTM3U\n\n')
                for station in stations:
                    f.write('#EXTINF:0,{0}\n{1}\n\n'.format(station.name, station.url))
        except:
            pass
