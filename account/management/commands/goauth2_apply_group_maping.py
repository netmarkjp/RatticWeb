from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from account.models import GOAUTH2GroupMapping
from logging import getLogger
import re


logger = getLogger("commands")


class Command(BaseCommand):
    help = """apply GOAUTH2GroupMapping to existing users.
    Default behavior is dry-run.
    When need to apply to join groups, use --apply-join
    When need to apply to leave groups, use --apply-leave
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply-join",
            dest="apply_join",
            action="store_true",
            default=False,
            help="check mapping and apply join groups")
        parser.add_argument(
            "--apply-leave",
            dest="apply_leave",
            action="store_true",
            default=False,
            help="check mapping and apply leave groups")

    def handle(self, *args, **options):
        mappings = None
        try:
            mappings = GOAUTH2GroupMapping.objects.all()
        except Exception as e:
            logger.error(e)

        if not mappings:
            return

        for user in get_user_model().objects.all():
            # aggregate mapping results
            mapped_user_groups = set()
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
                        mapped_user_groups.add(g)

                except Exception as e:
                    logger.error((e, m))

            user_groups = set([g for g in user.groups.all()])

            # join
            groups_to_join = mapped_user_groups - user_groups
            if groups_to_join:
                logger.warn("%s will join groups %s" % (user, groups_to_join))
                if options["apply_join"]:
                    try:
                        for g in groups_to_join:
                            g.user_set.add(user)
                            g.save()
                            logger.warn("%s joined to %s" % (user, g))
                    except Exception as e:
                        logger.error((e, m))

            # leave
            groups_to_leave = user_groups - mapped_user_groups
            if groups_to_leave:
                logger.warn("%s will leave groups %s" % (user, groups_to_leave))
                if options["apply_leave"]:
                    try:
                        for g in groups_to_leave:
                            g.user_set.remove(user)
                            g.save()
                            logger.warn("%s leaved from %s" % (user, g))
                    except Exception as e:
                        logger.error((e, m))
