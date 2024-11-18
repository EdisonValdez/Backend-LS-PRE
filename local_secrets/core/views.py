from django.http import FileResponse, HttpResponse
from django.template.loader import get_template
from django.utils import translation
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework_social_oauth2.views import TokenView
from django.utils.translation import gettext_lazy as _

from local_secrets.operations.models import PrivacyPolicies
from local_secrets.users.models import CustomUser


class CustomTokenView(TokenView):
    def post(self, request, *args, **kwargs):
        request.data['password'] = request.data['password'].rstrip()
        if 'email' in request.data:
            try:
                user = CustomUser.objects.get(email=request.data.get('email').rstrip())
                request.data['username'] = user.username
            except CustomUser.DoesNotExist:
                    raise AuthenticationFailed(detail=_('There is no user with such email'))

        response = super().post(request, *args, **kwargs)

        return response


class PoliciesViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], permission_classes=(AllowAny,))
    def terms_and_conditions(self, request):
        # filename = 'static/terms_and_conditions.pdf'
        filename = PrivacyPolicies.objects.get(title='terms_and_conditions').file
        if not request.user.is_anonymous:
            if request.user.language and request.user.language.code.lower() != 'es':
                # filename = 'static/en_terms_and_conditions.pdf'
                filename = PrivacyPolicies.objects.get(title='en_terms_and_conditions').file
        return FileResponse(filename, content_type='application/pdf')

    @action(detail=False, methods=['get'], permission_classes=(AllowAny,), url_path='es/privacy_policies')
    def privacy_policies_es(self, request):
        # filename = 'static/privacy_policies.pdf'
        # filename = PrivacyPolicies.objects.get(title='privacy_policies').file.url
        # if not request.user.is_anonymous:
        #     if request.user.language and request.user.language.code.lower() != 'es':
        #         # filename = 'static/en_privacy_policies.pdf'
        #         filename = PrivacyPolicies.objects.get(title='en_privacy_policies').file.url
        context = {}

        template_path = 'info/policies_info.html'
        template = get_template(template_path)
        html = template.render(context)
        return HttpResponse(html)

        # return FileResponse(filename, content_type='application/pdf')

    @action(detail=False, methods=['get'], permission_classes=(AllowAny,), url_path='en/privacy_policies')
    def privacy_policies_en(self, request):
        context = {}

        template_path = 'info/en_policies_info.html'
        template = get_template(template_path)
        html = template.render(context)
        return HttpResponse(html)


class InfoViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    @action(
        detail=False,
        methods=['get'],
    )
    def deletion(self, request, *args, **kwargs):
        context = {}
        template_path = 'info/deletion_info.html'
        template = get_template(template_path)
        html = template.render(context)

        return HttpResponse(html)
