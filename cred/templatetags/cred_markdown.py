from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.simple_tag
def markdown_cred(description):
    out = markdown.markdown(
        text=description,
        extensions=[
            'fenced_code',
            'nl2br',
        ],
        safe_mode='escape',
    )

    return mark_safe(out)
