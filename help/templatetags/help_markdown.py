from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.simple_tag
def markdown_file(filename):
    base_url = reverse('help:home')
    with open(filename) as f:
        out = markdown.markdown(
            text=f.read(),
            extensions=[
                'fenced_code',
                'nl2br',
                'headerid',
                'wikilinks(base_url=' + base_url + ')'
            ],
            safe_mode='escape',
        )

    return mark_safe(out)
