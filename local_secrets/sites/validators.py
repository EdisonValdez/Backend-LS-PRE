from django.core.exceptions import ValidationError

from local_secrets.sites.models import VideoSize


def video_size(value):
    db_video_size = VideoSize.objects.first()
    print(value.size)
    size = value.size / 1024 / 1024
    if size > db_video_size.max_size:
        raise ValidationError(f'File too large. Size should not exceed {db_video_size.max_size} MB.')
    if size < db_video_size.min_size:
        raise ValidationError(f'File too small. Size should be greater than {db_video_size.min_size} MB.')
