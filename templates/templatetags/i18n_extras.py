from django import template
from django.utils import translation

register = template.Library()


@register.simple_tag
def get_localized_name(obj, language=None):
    """Get the localized name of an object based on current language."""
    if language is None:
        language = translation.get_language()
    lang_code = language[:2] if language else 'ru'

    if hasattr(obj, 'get_localized_name'):
        return obj.get_localized_name(lang_code)

    if lang_code == 'en':
        if hasattr(obj, 'name_en') and obj.name_en:
            return obj.name_en
        if hasattr(obj, 'title_en') and obj.title_en:
            return obj.title_en

    if hasattr(obj, 'name'):
        return obj.name
    if hasattr(obj, 'title'):
        return obj.title
    return str(obj)


@register.simple_tag
def get_localized_field(obj, field_name, language=None):
    """Get a localized field value (e.g., name_en, description_en)."""
    if language is None:
        language = translation.get_language()
    lang_code = language[:2] if language else 'ru'

    if lang_code == 'en':
        en_field = f'{field_name}_en'
        if hasattr(obj, en_field):
            value = getattr(obj, en_field)
            if value:
                return value

    return getattr(obj, field_name, '')


@register.filter
def localized(obj, language=None):
    """Template filter: {{ city|localized }} returns localized name."""
    if language is None:
        language = translation.get_language()
    lang_code = language[:2] if language else 'ru'

    if hasattr(obj, 'get_localized_name'):
        return obj.get_localized_name(lang_code)

    if lang_code == 'en':
        if hasattr(obj, 'name_en') and obj.name_en:
            return obj.name_en
        if hasattr(obj, 'title_en') and obj.title_en:
            return obj.title_en

    if hasattr(obj, 'name'):
        return obj.name
    if hasattr(obj, 'title'):
        return obj.title
    return str(obj)


@register.filter
def localized_field(obj, field_name):
    """Template filter: {{ faq|localized_field:'question' }} returns localized field."""
    language = translation.get_language()
    lang_code = language[:2] if language else 'ru'

    if lang_code == 'en':
        en_field = f'{field_name}_en'
        if hasattr(obj, en_field):
            value = getattr(obj, en_field)
            if value:
                return value

    return getattr(obj, field_name, '')
