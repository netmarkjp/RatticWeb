from django.conf.urls import url
from help.views import home, markdown

urlpatterns = [
    url(r'^$', home, name="home"),
    url(r'^(?P<page>[\w\-]+)/$', markdown, name="markdown"),
]
