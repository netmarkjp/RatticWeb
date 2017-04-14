from keepassdb import Database
from django.utils.encoding import smart_text


def keepass(filep, password):
    groups = []
    entries = []
    groupstack = []

    db = Database(filep, password)

    _walkkeepass(groups, entries, groupstack, db.root)

    return {'tags': groups, 'entries': entries}


def _walkkeepass(groups, entries, groupstack, root):
    for n in root.children:
        t = smart_text(n.title, errors='replace')
        groupstack.append(t)
        groups.append(t)
        base_titles = []
        for gs in groupstack:
            if isinstance(gs, unicode):
                base_titles.append(gs.encode("utf-8"))
            elif isinstance(gs, str):
                base_titles.append(gs)
            else:
                base_titles.append(str(gs))
        for e in n.entries:
            if e.title != 'Meta-Info':
                title = smart_text(e.title, errors='replace')
                if isinstance(title, unicode):
                    title = title.encode("utf-8")
                entries.append({
                    'title': "{0} {1}".format(" ".join(base_titles), title),
                    'username': smart_text(e.username, errors='replace'),
                    'password': smart_text(e.password, errors='replace'),
                    'description': smart_text(e.notes, errors='replace'),
                    'url': smart_text(e.url, errors='replace'),
                    'tags': list(groupstack),
                    'filecontent': e.binary,
                    'filename': smart_text(e.binary_desc, errors='replace'),
                })
        _walkkeepass(groups, entries, groupstack, n)
        groupstack.pop()
