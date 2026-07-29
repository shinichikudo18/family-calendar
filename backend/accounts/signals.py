import logging
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Family, FamilyMember

logger = logging.getLogger(__name__)

IGNORED_GROUPS = {'lldap_admin', 'lldap_password_manager', 'lldap_strict_readonly'}

@receiver(user_logged_in)
def sync_ldap_groups_to_families(sender, user, request, **kwargs):
    ldap_user = getattr(user, 'ldap_user', None)
    if not ldap_user:
        return

    try:
        group_names = ldap_user.group_names
    except Exception:
        group_names = []

    for group_name in group_names:
        if group_name in IGNORED_GROUPS or group_name.startswith('lldap_'):
            continue

        family, created = Family.objects.get_or_create(
            name=group_name,
            defaults={'description': f'Familia sincronizada desde LDAP: {group_name}'}
        )

        member, member_created = FamilyMember.objects.get_or_create(
            family=family,
            user=user,
            defaults={'role': 'admin' if created else 'member'}
        )

        if created:
            from events.models import Calendar as FamilyCalendar
            FamilyCalendar.objects.get_or_create(
                family=family,
                name=f'Calendario de {group_name}',
                defaults={'description': f'Calendario principal de {group_name}'}
            )
            logger.info(f'Created family "{group_name}" with calendar and admin {user.username}')
        elif member_created:
            logger.info(f'Added user {user.username} to family "{group_name}"')
