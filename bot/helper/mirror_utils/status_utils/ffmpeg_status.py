from time import time
from bot.helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time, MirrorStatus
from bot.helper.ext_utils.fs_utils import get_path_size

class FFMpegStatus:
    def __init__(self, listener, name, size, gid, status):
        self._listener = listener
        self._name = name
        self._size = size
        self._gid = gid
        self._status = status
        self._start_time = time()

    def progress(self):
        """
        Returns progress percentage
        """
        return 0

    def speed(self):
        """
        Returns speed of the download
        """
        return 0

    def name(self):
        """
        Returns name of the download
        """
        return self._name

    def size(self):
        """
        Returns size of the download
        """
        return get_readable_file_size(self._size)

    def eta(self):
        """
        Returns eta of the download
        """
        return "0s"

    def status(self):
        """
        Returns status of the download
        """
        if self._status == "direct":
            return MirrorStatus.STATUS_DOWNLOADING
        return self._status

    def processed_bytes(self):
        return 0

    def gid(self):
        return self._gid

    def listener(self):
        return self._listener
