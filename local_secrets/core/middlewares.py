from django.utils import translation


def localization(get_response):
    def middleware(request):
        return get_response(request)

    return middleware
