from django import template
from ..models import Settings

register = template.Library()

@register.simple_tag
def get_setting(request, name):
    return getattr(Settings(session=request.session), name)
