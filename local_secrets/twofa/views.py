import base64

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .providers import TwoFAProvider
from .renderers import SVGRenderer


class TwoFAViewset(viewsets.ViewSet):
    # This secret must be unique per user
    secret = base64.b32encode('myhardcodedsecret'.encode())
    provider = TwoFAProvider(secret)

    @action(detail=False, methods=['get', 'post'], url_path='create', renderer_classes=[SVGRenderer])
    def request_qr_code(self, request):
        qr = self.provider.qr_code('rudotestqr', 'david@rudo.es')
        return Response(qr)

    @action(detail=False, methods=['post'], url_path='validate')
    def validate_qr_code(self, request):
        token = request.data.get('token')

        return Response(
            {
                'valid': self.provider.valid(token),
            },
            content_type='application/json',
        )
