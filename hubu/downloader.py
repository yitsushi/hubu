import urllib
import tempfile
import threading
import time
from hubu.base import ThreadedBase

class Downloader(ThreadedBase):
    def __init__(self, thread_id, manager):
        super(__class__, self).__init__(thread_id)
        self.thread_id = thread_id
        self.manager = manager
        self._target_size = 0
        self._downloaded_bytes = 0

    def progress(self):
        if self._downloaded_bytes == 0:
            return 0.0
        return self._downloaded_bytes / self._target_size

    def run(self):
        self.log.info(f'--- Start #{self.thread_id}')
        self.process()
        self.log.info(f'--- Stop #{self.thread_id}')

    def process(self):
        while True:
            self.manager.lock().acquire()
            if self.manager.queue().empty():
                self.manager.lock().release()
                time.sleep(1)
                continue

            item = self.manager.queue().get()
            self.manager.lock().release()
            if item == -1:
                break

            size = self.s3().file_size(item.path())
            if size == item.size:
                self.log.info(f'{item.path()} already in there')
                self.manager.queue().task_done()
                continue

            if size != 0 and size != item.size:
                self.delete_object(path)

            self._target_size = item.size
            self._downloaded_bytes = 0
            fp = tempfile.TemporaryFile()
            self.save(source=item.url, dest=fp)
            fp.seek(0)
            self.upload(source=fp, dest=item.path())
            fp.close()

            self.manager.queue().task_done()

    def save(self, source, dest, blockSize=200):
        try:
            url = urllib.request.urlopen(source)
        except:
            print("SKIP", source, fullPath)
            return

        block_size = (1024*blockSize)
        while True:
            buf = url.read(block_size)
            if not buf:
                break
            self._downloaded_bytes += len(buf)
            dest.write(buf)

    def upload(self, source, dest):
        self.log.info(f"Upload {dest}")
        self.s3().put_object(source, dest)
