from django.conf.urls import url
from django.conf import settings
from views import NewUser, UpdateUser
from staff.views import home, userdetail, removetoken, groupdetail, audit, upload_keepass, import_overview, import_process, import_ignore, credundelete, groupadd, groupedit, groupdelete, userdelete

urlpatterns = [
    # Views in views.py
    url(r'^$', home, name="home"),

    # User/Group Management
    url(r'^userdetail/(?P<uid>\d+)/$', userdetail, name="userdetail"),
    url(r'^removetoken/(?P<uid>\d+)/$', removetoken, name="removetoken"),
    url(r'^groupdetail/(?P<gid>\d+)/$', groupdetail, name="groupdetail"),

    # Auditing
    url(r'^audit-by-(?P<by>\w+)/(?P<byarg>\d+)/$', audit, name="audit"),

    # Importing
    url(r'^import/keepass/$', upload_keepass, name="upload_keepass"),
    url(r'^import/process/$', import_overview, name="import_overview"),
    url(r'^import/process/(?P<import_id>\d+)/$', import_process, name="import_process"),
    url(r'^import/process/(?P<import_id>\d+)/ignore/$', import_ignore, name="import_ignore"),

    # Undeletion
    url(r'^credundelete/(?P<cred_id>\d+)/$', credundelete, name="credundelete"),
]

# URLs we remove if using LDAP groups
if not settings.USE_LDAP_GROUPS:
    urlpatterns += [
        # Group Management
        url(r'^groupadd/$', groupadd, name="groupadd"),
        url(r'^groupedit/(?P<gid>\d+)/$', groupedit, name="groupedit"),
        url(r'^groupdelete/(?P<gid>\d+)/$', groupdelete, name="groupdelete"),
        url(r'^useredit/(?P<pk>\d+)/$', UpdateUser.as_view(), name="user_edit"),
        url(r'^userdelete/(?P<uid>\d+)/$', userdelete, name="userdelete"),
    ]

# User add is disabled only when LDAP config exists
if not settings.LDAP_ENABLED:
    urlpatterns += [
        # User Management
        url(r'^useradd/$', NewUser.as_view(), name="user_add"),
    ]
