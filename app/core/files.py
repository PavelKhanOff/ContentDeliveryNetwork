import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import UploadFile, HTTPException
from streaming_form_data.targets import FileTarget, BaseTarget

uploadDir = '/compress_dir/'


def abspath(name: str):
    return os.path.join(uploadDir, os.path.basename(name))


class UploadFileTarget(FileTarget):
    def __init__(self, dir: str, *args, **kwargs):
        super().__init__(None, *args, **kwargs)

        self.file = UploadFile(None, file=NamedTemporaryFile(delete=False, dir=dir))
        self._fd = self.file.file

    def on_start(self):
        suffix = Path(self.multipart_filename).suffix
        self.file.filename = self.filename = self.file.file.name + suffix
        if os.path.exists(abspath(self.filename)):
            raise HTTPException(409, "File already exists")


class FileTarget2(BaseTarget):
    def __init__(self, filename: str, allow_overwrite: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filename = filename

        self._mode = 'wb' if allow_overwrite else 'xb'
        self._fd = None

    def on_start(self):
        self._fd = open(self.filename, "ab+")

    def on_data_received(self, chunk: bytes):
        if self._fd:
            self._fd.write(chunk)

    def on_finish(self):
        if self._fd:
            self._fd.close()

    def get_size(self):
        return os.path.getsize(self.filename)
