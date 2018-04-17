from django.conf.urls import url
from django.conf import settings
from cred.views import list as list_view, search, detail, ssh_key_fingerprint, downloadattachment, downloadsshkey, edit, delete, otp, add, qr, addtoqueue, bulkaddtoqueue, bulkdelete, bulkundelete, bulktagcred, tags, tagadd, tagedit, tagdelete, download

urlpatterns = [
    # New list views
    url(r'^list/$', list_view, name="list"),
    url(r'^list-by-(?P<cfilter>\w+)/(?P<value>[^/]*)/$', list_view, name="list"),
    url(r'^list-by-(?P<cfilter>\w+)/(?P<value>[^/]*)/sort-(?P<sortdir>ascending|descending)-by-(?P<sort>\w+)/$', list_view, name="list"),
    url(r'^list-by-(?P<cfilter>\w+)/(?P<value>[^/]*)/sort-(?P<sortdir>ascending|descending)-by-(?P<sort>\w+)/page-(?P<page>\d+)/$', list_view, name="list"),

    # Search dialog for mobile
    url(r'^search/$', search, name="search"),

    # Single cred views
    url(r'^detail/(?P<cred_id>\d+)/$', detail, name="detail"),
    url(r'^detail/(?P<cred_id>\d+)/fingerprint/$', ssh_key_fingerprint, name="ssh_key_fingerprint"),
    url(r'^detail/(?P<cred_id>\d+)/download/$', downloadattachment, name="downloadattachment"),
    url(r'^detail/(?P<cred_id>\d+)/ssh_key/$', downloadsshkey, name="downloadsshkey"),
    url(r'^edit/(?P<cred_id>\d+)/$', edit, name="edit"),
    url(r'^delete/(?P<cred_id>\d+)/$', delete, name="delete"),
    url(r'^otp/(?P<cred_id>\d+)/$', otp, name="otp"),
    url(r'^add/$', add, name="add"),
    url(r'^qr/$', qr, name="qr"),

    # Adding to the change queue
    url(r'^addtoqueue/(?P<cred_id>\d+)/$', addtoqueue, name="addtoqueue"),

    # Bulk views (for buttons on list page)
    url(r'^addtoqueue/bulk/$', bulkaddtoqueue, name="bulkaddtoqueue"),
    url(r'^delete/bulk/$', bulkdelete, name="bulkdelete"),
    url(r'^undelete/bulk/$', bulkundelete, name="bulkundelete"),
    url(r'^addtag/bulk/$', bulktagcred, name="bulktagcred"),

    # Tags
    url(r'^tag/$', tags, name="tags"),
    url(r'^tag/add/$', tagadd, name="tagadd"),
    url(r'^tag/edit/(?P<tag_id>\d+)/$', tagedit, name="tagedit"),
    url(r'^tag/delete/(?P<tag_id>\d+)/$', tagdelete, name="tagdelete"),
]

if not settings.RATTIC_DISABLE_EXPORT:
    urlpatterns += [
        # Export views
        url(r'^export.kdb$', download, name="download"),
        url(r'^export-by-(?P<cfilter>\w+)/(?P<value>[^/]*).kdb$', download, name="download"),
    ]
