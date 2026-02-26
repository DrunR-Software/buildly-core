import logging

from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.conf import settings

from core.models import CoreGroup, CoreSites, Organization

logger = logging.getLogger(__name__)


def set_username_from_email(details, *args, **kwargs):
    """Use the provider email as the Django username."""
    return {'username': details.get('email', '')}


def assign_social_auth_organization(user=None, is_new=False, *args, **kwargs):
    """
    Assign newly created social auth users to the default organization
    and add them to that organization's default Users CoreGroup.
    """
    if not user or not is_new:
        return

    try:
        organization = Organization.objects.get(name__iexact='drunr')
    except Organization.DoesNotExist:
        organization = Organization.objects.create(name='drunr')

    user.organization = organization
    user.save()

    default_group = CoreGroup.objects.filter(
        organization=organization, is_default=True
    ).first()
    if default_group:
        user.core_groups.add(default_group)


def create_organization(core_user=None, *args, **kwargs):
    """
    Create or retrieve an organization and associate it to the core user
    """
    if not core_user or not kwargs.get('is_new_core_user', None):
        return

    # create or get an organization and associate it to the core user
    if settings.DEFAULT_ORG:
        organization, created = Organization.objects.get_or_create(
            name=settings.DEFAULT_ORG
        )
    else:
        organization, created = Organization.objects.get_or_create(
            name=core_user.username
        )

    core_user.organization = organization
    core_user.save()

    return {'is_new_org': created, 'organization': organization}


def auth_allowed(backend, details, response, *args, **kwargs):
    """
    Verifies that the current auth process is valid. Emails,
    domains whitelists and organization domains are applied (if defined).
    """
    allowed = False
    static_url = settings.STATIC_URL

    # Get whitelisted domains and emails defined in the settings
    whitelisted_emails = backend.setting('WHITELISTED_EMAILS', [])
    whitelisted_domains = backend.setting('WHITELISTED_DOMAINS', [])

    # Get the whitelisted domains defined in the CoreSites
    site = get_current_site(None)

    core_site = CoreSites.objects.filter(site=site).first()
    if core_site and core_site.whitelisted_domains:
        core_domains = ','.join(core_site.whitelisted_domains.split())
        core_domains = core_domains.split(',')
        whitelisted_domains += core_domains

    try:
        email = details['email']
    except KeyError:
        logger.warning('No email was passed in the details.')
        allowed = False
    else:
        domain = email.split('@', 1)[1]
        if whitelisted_emails or whitelisted_domains:
            allowed = email in whitelisted_emails or domain in whitelisted_domains

        # Check if the user email domain matches with one of the org oauth
        # domains and add the organization uuid in the details
        if allowed:
            org_uuid = Organization.objects.values_list(
                'organization_uuid', flat=True
            ).get(name=settings.DEFAULT_ORG)
            details.update({'organization_uuid': org_uuid})
        else:
            try:
                org_uuid = Organization.objects.values_list(
                    'organization_uuid', flat=True
                ).get(oauth_domains__contains=[domain])
                details.update({'organization_uuid': org_uuid})
                allowed = True
            except Organization.DoesNotExist:
                pass
            except Organization.MultipleObjectsReturned as e:
                logger.warning(
                    'There is more than one Organization with '
                    'the domain {}.\n{}'.format(domain, e)
                )

    if not allowed:
        return render(
            'unauthorized.html',
            context={'STATIC_URL': static_url}
        )
