# -*- coding: utf-8 -*-

from cred.models import Cred
from cred.models import Tag
from django.contrib.auth.models import Group
from django.db import IntegrityError
from staff.importloaders import keepass
import django
import os


django.setup()

res = keepass(
    open(os.getenv("RATTIC_KEEPASS_FILE"), "rb"),
    os.getenv("RATTIC_KEEPASS_PASSWORD")
)

owner_group = Group.objects.get(name=os.getenv("RATTIC_KEEPASS_GROUP"))

print("=> import Tag")
for tag_name in res.get("tags", []):
    try:
        Tag(name=tag_name).save()
    except IntegrityError as e:
        if e.message.endswith(" is not unique"):
            pass
        else:
            print(tag_name, e)
    except Exception as e:
        print(tag_name, e)

print("=> import Entry")
for entry in res.get("entries", []):
    try:
        kwargs = {}
        tags = []
        for k, v in entry.items():
            if k == "tags":
                tags = v
                continue
            if k in ["filename", "filecontent"]:
                continue
            kwargs[k] = v

        kwargs["group"] = owner_group

        cred = Cred(**kwargs)
        cred.save()
        for tag_name in tags:
            cred.tags.add(Tag.objects.get(name=tag_name))
        cred.save()
    except IntegrityError as e:
        if e.message.endswith(" is not unique"):
            pass
        else:
            print(entry.get("title"), entry.get("name"), e)
    except Exception as e:
        print(entry.get("title"), entry.get("name"), e)
