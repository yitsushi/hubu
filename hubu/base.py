import logging
import re
import threading
import unicodedata
from hubu.bucket_client import BucketClient

class Base(object):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.__bucket_client = None

    def slugify(self, value):
        """
        Convert to ASCII. Convert spaces to hyphens.
        Remove characters that aren't alphanumerics, underscores, or hyphens.
        Convert to lowercase. Also strip leading and trailing whitespace.

        Source: https://docs.djangoproject.com/en/2.1/_modules/django/utils/text/#slugify
        """
        value = str(value)
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value).strip().lower()
        return re.sub(r'[-\s]+', '-', value)

    def s3(self):
        if self.__bucket_client is None:
            self.log.info('Create bucket client')
            self.__bucket_client = BucketClient()
        return self.__bucket_client


class ThreadedBase(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.log = logging.getLogger(f'{self.__class__.__name__}#{thread_id}')
        self.__bucket_client = None

    def s3(self):
        if self.__bucket_client is None:
            self.log.info('Create bucket client')
            self.__bucket_client = BucketClient()
        return self.__bucket_client
