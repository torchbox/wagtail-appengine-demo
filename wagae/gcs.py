# Create new static storage classes for storing media and static directories
# on Google Cloud Storage.  This is required to set the root path for each
# type of file, otherwise they would end up mixed into the root directory.

# This is taken from
# https://www.caktusgroup.com/blog/2014/11/10/Using-Amazon-S3-to-store-your-Django-sites-static-and-media-files/

# We are using GCS in S3-compatible mode (with S3Boto3Storage) because the
# django-storages GCS backend doesn't seem to support setting the location.

from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage

class GCSStaticStorage(GoogleCloudStorage):
    bucket_name = settings.GS_BUCKET_PREFIX + '-static'

class GCSMediaStorage(GoogleCloudStorage):
    bucket_name = settings.GS_BUCKET_PREFIX + '-media'
