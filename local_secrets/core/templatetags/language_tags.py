from django import template

from local_secrets.languages.models import Language

register = template.Library()


@register.simple_tag
def get_languages():
    languages = Language.objects.all()
    result = []
    for language in languages:
        flag_code = language.code
        if language.code == 'en':
            flag_code = 'gb'
        result.append((f'{language.code}', f'{flag_code}'))
    return result


@register.simple_tag(takes_context=True)
def get_localized_admin_url(context, lang):
    path = '/'.join(context.request.path.split('/')[2:])
    return f'/{lang}/{path}'
