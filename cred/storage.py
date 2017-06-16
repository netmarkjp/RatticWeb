from database_files.storage import DatabaseStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class CredAttachmentStorage(DatabaseStorage):
    def url(self, name):
        return 'Not used in RatticDB. If you see this please raise a bug.'
