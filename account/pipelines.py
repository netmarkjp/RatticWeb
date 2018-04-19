# -*- coding: utf-8 -*-
"""pipelines for social auth"""

from .models import GOAUTH2GroupMapping
from logging import getLogger
import re


logger = getLogger("ratticweb")


def assign_groups(user, *args, **kwargs):  # pylint:disable=unused-argument
    """assign groups"""
    mappings = None
    try:
        mappings = GOAUTH2GroupMapping.objects.all()
    except Exception as e:
        logger.error(e)

    if not mappings:
        return

    for m in mappings:
        try:
            if user.email in [l.strip() for l in m.member_emails.split("\n")]:
                groups = m.groups.all()
                for g in groups:
                    g.user_set.add(user)
                    g.save()
        except Exception as e:
            logger.error(e)

        try:
            if not m.member_email_pattern:
                continue
            pattern = re.compile(m.member_email_pattern, re.I)
            if pattern and pattern.match(user.email):
                groups = m.groups.all()
                for g in groups:
                    g.user_set.add(user)
                    g.save()
        except Exception as e:
            logger.error(e)
