from rest_framework.exceptions import APIException


class CustomApiException(APIException):
    detail = None
    status_code = None

    # create constructor
    def __init__(self, status_code, message):
        # override public fields
        self.status_code = status_code
        self.detail = message
