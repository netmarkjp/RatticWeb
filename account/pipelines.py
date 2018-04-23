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
            matched = False
            if not m.member_email_pattern:
                continue

            if m.pattern_is_regex:
                pattern = re.compile(m.member_email_pattern, re.I)
                matched = pattern and pattern.match(user.email)
            else:
                matched = user.email == m.member_email_pattern

            if not matched:
                continue

            groups = m.groups.all()
            for g in groups:
                g.user_set.add(user)
                g.save()
        except Exception as e:
            logger.error((e, m))
