# from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


# noinspection PyAbstractClass
class MediaStorage(S3Boto3Storage):
    bucket_name = 'media'  # f'{settings.AWS_STORAGE_BUCKET_NAME}'
    location = 'media'


# noinspection PyAbstractClass
class StaticStorage(S3Boto3Storage):
    # bucket_name = f'{settings.BASE_DIR.name}-spaces'
    location = 'static'
    default_acl = 'public-read'
