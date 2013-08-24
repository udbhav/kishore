import time

from storages.backends.s3boto import S3BotoStorage
from boto.utils import canonical_string

class SecureS3Storage(S3BotoStorage):
    def __init__(self, **kwargs):
        super(SecureS3Storage, self).__init__(**kwargs)

        self.querystring_auth = True
        self.querystring_expire = 3600
        self.default_acl = 'private'

    def download_url(self, name):
        k = self.bucket.get_key(name)
        return k.generate_url(self.querystring_expire, response_headers={'response-content-disposition':'attachment'})
