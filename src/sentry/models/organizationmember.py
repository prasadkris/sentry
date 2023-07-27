from __future__ import annotations

import datetime
from collections import defaultdict
from datetime import timedelta
from enum import Enum
from hashlib import md5
from typing import TYPE_CHECKING, FrozenSet, List, Mapping, MutableMapping, Set, TypedDict
from urllib.parse import urlencode
from uuid import uuid4

from django.conf import settings
from django.db import models, router, transaction
from django.db.models import Q, QuerySet
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from structlog import get_logger

from bitfield.models import typed_dict_bitfield
from sentry import features, roles
from sentry.db.models import (
    BoundedPositiveIntegerField,
    FlexibleForeignKey,
    Model,
    region_silo_only_model,
    sane_repr,
)
from sentry.db.models.fields.hybrid_cloud_foreign_key import HybridCloudForeignKey
from sentry.db.models.manager import BaseManager
from sentry.exceptions import UnableToAcceptMemberInvitationException
from sentry.models.organizationmemberteam import OrganizationMemberTeam
from sentry.models.outbox import OutboxCategory, OutboxScope, RegionOutbox, outbox_context
from sentry.models.team import TeamStatus
from sentry.roles import organization_roles
from sentry.roles.manager import OrganizationRole
from sentry.services.hybrid_cloud import extract_id_from
from sentry.services.hybrid_cloud.user.service import user_service
from sentry.signals import member_invited
from sentry.utils.http import absolute_uri

if TYPE_CHECKING:
    from sentry.models.organization import Organization
    from sentry.services.hybrid_cloud.integration import RpcIntegration
    from sentry.services.hybrid_cloud.user import RpcUser

_OrganizationMemberFlags = TypedDict(
    "_OrganizationMemberFlags",
    {
        "sso:linked": bool,
        "sso:invalid": bool,
        "member-limit:restricted": bool,
        "idp:provisioned": bool,
        "idp:role-restricted": bool,
    },
)


INVITE_DAYS_VALID = 30


class InviteStatus(Enum):
    APPROVED = 0
    REQUESTED_TO_BE_INVITED = 1
    REQUESTED_TO_JOIN = 2

    @classmethod
    def as_choices(cls):
        return (
            (InviteStatus.APPROVED.value, _("Approved")),
            (
                InviteStatus.REQUESTED_TO_BE_INVITED.value,
                _("Organization member requested to invite user"),
            ),
            (InviteStatus.REQUESTED_TO_JOIN.value, _("User requested to join organization")),
        )


invite_status_names = {
    InviteStatus.APPROVED.value: "approved",
    InviteStatus.REQUESTED_TO_BE_INVITED.value: "requested_to_be_invited",
    InviteStatus.REQUESTED_TO_JOIN.value: "requested_to_join",
}


ERR_CANNOT_INVITE = "Your organization is not allowed to invite members."
ERR_JOIN_REQUESTS_DISABLED = "Your organization does not allow requests to join."


class OrganizationMemberManager(BaseManager):
    def get_contactable_members_for_org(self, organization_id: int) -> QuerySet:
        """Get a list of members we can contact for an organization through email."""
        # TODO(Steve): check member-limit:restricted
        return self.filter(
            organization_id=organization_id,
            invite_status=InviteStatus.APPROVED.value,
            user_id__isnull=False,
        )

    def delete_expired(self, threshold: datetime.datetime) -> None:
        """Delete un-accepted member invitations that expired `threshold` days ago."""
        from sentry.services.hybrid_cloud.auth import auth_service

        orgs_with_scim = auth_service.get_org_ids_with_scim()
        for member in (
            self.filter(
                token_expires_at__lt=threshold,
                user_id__exact=None,
            )
            .exclude(email__exact=None)
            .exclude(organization_id__in=orgs_with_scim)
        ):
            member.delete()

    def get_for_integration(
        self, integration: RpcIntegration | int, user: RpcUser, organization_id: int | None = None
    ) -> QuerySet:
        # This can be moved into the integration service once OrgMemberMapping is completed.
        # We are forced to do an ORM -> service -> ORM call to reduce query size while avoiding
        # cross silo queries until we have a control silo side to map users through.
        from sentry.services.hybrid_cloud.integration import integration_service

        if organization_id is not None:
            if (
                integration_service.get_organization_integration(
                    integration_id=extract_id_from(integration), organization_id=organization_id
                )
                is None
            ):
                return self.filter(Q())
            return self.filter(organization_id=organization_id, user_id=user.id)

        org_ids = list(self.filter(user_id=user.id).values_list("organization_id", flat=True))
        org_ids = [
            oi.organization_id
            for oi in integration_service.get_organization_integrations(
                organization_ids=org_ids, integration_id=extract_id_from(integration)
            )
        ]
        return self.filter(user_id=user.id, organization_id__in=org_ids).select_related(
            "organization"
        )

    def get_member_invite_query(self, id: int) -> QuerySet:
        return self.filter(
            invite_status__in=[
                InviteStatus.REQUESTED_TO_BE_INVITED.value,
                InviteStatus.REQUESTED_TO_JOIN.value,
            ],
            user_id__isnull=True,
            id=id,
        )

    def get_teams_by_user(self, organization: Organization) -> Mapping[int, List[int]]:
        user_teams: MutableMapping[int, List[int]] = defaultdict(list)
        queryset = self.filter(organization_id=organization.id).values_list("user_id", "teams")
        for user_id, team_id in queryset:
            user_teams[user_id].append(team_id)
        return user_teams

    def get_members_by_email_and_role(self, email: str, role: str) -> QuerySet:
        users_by_email = user_service.get_many(
            filter=dict(
                emails=[email],
                is_active=True,
            )
        )

        # may be empty
        team_members = set(
            OrganizationMemberTeam.objects.filter(
                team_id__org_role=role,
                organizationmember__user_id__in=[u.id for u in users_by_email],
            ).values_list("organizationmember_id", flat=True)
        )

        org_members = set(
            self.filter(role=role, user_id__in=[u.id for u in users_by_email]).values_list(
                "id", flat=True
            )
        )

        # use union of sets because a subset may be empty
        return self.filter(id__in=org_members.union(team_members))


@region_silo_only_model
class OrganizationMember(Model):
    """
    Identifies relationships between organizations and users.

    Users listed as team members are considered to have access to all projects
    and could be thought of as team owners (though their access level may not)
    be set to ownership.
    """

    __include_in_export__ = True

    objects = OrganizationMemberManager()

    organization = FlexibleForeignKey("sentry.Organization", related_name="member_set")

    user_id = HybridCloudForeignKey("sentry.User", on_delete="CASCADE", null=True, blank=True)
    # This email indicates the invite state of this membership -- it will be cleared when the user is set.
    # it does not necessarily represent the final email of the user associated with the membership, see user_email.
    email = models.EmailField(null=True, blank=True, max_length=75)
    role = models.CharField(max_length=32, default=str(organization_roles.get_default().id))

    flags = typed_dict_bitfield(_OrganizationMemberFlags, default=0)

    token = models.CharField(max_length=64, null=True, blank=True, unique=True)
    date_added = models.DateTimeField(default=timezone.now)
    token_expires_at = models.DateTimeField(default=None, null=True)
    has_global_access = models.BooleanField(default=True)
    teams = models.ManyToManyField(
        "sentry.Team", blank=True, through="sentry.OrganizationMemberTeam"
    )
    inviter_id = HybridCloudForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete="SET_NULL",
    )
    invite_status = models.PositiveSmallIntegerField(
        choices=InviteStatus.as_choices(),
        default=InviteStatus.APPROVED.value,
        null=True,
    )

    # Deprecated -- no longer used
    type = BoundedPositiveIntegerField(default=50, blank=True)

    # These attributes are replicated via USER_UPDATE category outboxes for the user object associated with the user_id
    # when it exists.
    user_is_active = models.BooleanField(
        null=False,
        default=True,
    )
    # Note, this is the email of the user that may or may not be associated with the member, not the email used to
    # invite the user.
    user_email = models.CharField(max_length=75, null=True, blank=True)

    class Meta:
        app_label = "sentry"
        db_table = "sentry_organizationmember"
        unique_together = (("organization", "user_id"), ("organization", "email"))

    __repr__ = sane_repr("organization_id", "user_id", "email", "role")

    # Used to reduce redundant queries
    __org_roles_from_teams = None

    def delete(self, *args, **kwds):
        with outbox_context(transaction.atomic(using=router.db_for_write(OrganizationMember))):
            self.save_outbox_for_update()
            return super().delete(*args, **kwds)

    def save(self, *args, **kwargs):
        assert (self.user_id is None and self.email) or (
            self.user_id and self.email is None
        ), "Must set either user or email"

        with outbox_context(transaction.atomic(using=router.db_for_write(OrganizationMember))):
            if self.token and not self.token_expires_at:
                self.refresh_expires_at()
            super().save(*args, **kwargs)
            self.save_outbox_for_update()
            self.__org_roles_from_teams = None

    def refresh_from_db(self, *args, **kwargs):
        super().refresh_from_db(*args, **kwargs)
        self.__org_roles_from_teams = None

    def set_user(self, user_id: int):
        self.user_id = user_id
        self.email = None
        self.token = None
        self.token_expires_at = None

    def remove_user(self):
        self.email = self.get_email()
        self.user_id = None
        self.token = self.generate_token()

    def regenerate_token(self):
        self.token = self.generate_token()
        self.refresh_expires_at()

    def outbox_for_update(self) -> RegionOutbox:
        return RegionOutbox(
            shard_scope=OutboxScope.ORGANIZATION_SCOPE,
            shard_identifier=self.organization_id,
            category=OutboxCategory.ORGANIZATION_MEMBER_UPDATE,
            object_identifier=self.id,
            payload=dict(user_id=self.user_id),
        )

    def save_outbox_for_update(self) -> RegionOutbox:
        outbox = self.outbox_for_update()
        outbox.save()
        return outbox

    def refresh_expires_at(self):
        now = timezone.now()
        self.token_expires_at = now + timedelta(days=INVITE_DAYS_VALID)

    def approve_invite(self):
        self.invite_status = InviteStatus.APPROVED.value
        self.regenerate_token()

    def get_invite_status_name(self):
        if self.invite_status is None:
            return
        return invite_status_names[self.invite_status]

    @property
    def invite_approved(self):
        return self.invite_status == InviteStatus.APPROVED.value

    @property
    def requested_to_join(self):
        return self.invite_status == InviteStatus.REQUESTED_TO_JOIN.value

    @property
    def requested_to_be_invited(self):
        return self.invite_status == InviteStatus.REQUESTED_TO_BE_INVITED.value

    @property
    def is_pending(self):
        return self.user_id is None

    @property
    def token_expired(self):
        # Old tokens don't expire to preserve compatibility and not require
        # a backfill migration.
        if self.token_expires_at is None:
            return False
        if self.token_expires_at > timezone.now():
            return False
        return True

    @property
    def legacy_token(self):
        email = self.get_email()
        if not email:
            return ""
        checksum = md5()
        checksum.update(str(self.organization_id).encode("utf-8"))
        checksum.update(email.encode("utf-8"))
        checksum.update(force_bytes(settings.SECRET_KEY))
        return checksum.hexdigest()

    def generate_token(self):
        return uuid4().hex + uuid4().hex

    def get_invite_link(self):
        if not self.is_pending or not self.invite_approved:
            return None
        path = reverse(
            "sentry-accept-invite",
            kwargs={
                "member_id": self.id,
                "token": self.token or self.legacy_token,
            },
        )
        return self.organization.absolute_url(path)

    def send_invite_email(self):
        from sentry.utils.email import MessageBuilder

        context = {
            "email": self.email,
            "organization": self.organization,
            "url": self.get_invite_link(),
        }

        msg = MessageBuilder(
            subject="Join %s in using Sentry" % self.organization.name,
            template="sentry/emails/member-invite.txt",
            html_template="sentry/emails/member-invite.html",
            type="organization.invite",
            context=context,
        )

        try:
            msg.send_async([self.get_email()])
        except Exception as e:
            logger = get_logger(name="sentry.mail")
            logger.exception(e)

    def send_sso_link_email(self, user_id: int, provider):
        from sentry.utils.email import MessageBuilder

        link_args = {"organization_slug": self.organization.slug}

        email = ""
        user = user_service.get_user(user_id=user_id)
        if user:
            email = user.email

        context = {
            "organization": self.organization,
            "email": email,
            "provider": provider,
            "url": absolute_uri(reverse("sentry-auth-organization", kwargs=link_args)),
        }

        msg = MessageBuilder(
            subject=f"Action Required for {self.organization.name}",
            template="sentry/emails/auth-link-identity.txt",
            html_template="sentry/emails/auth-link-identity.html",
            type="organization.auth_link",
            context=context,
        )
        msg.send_async([self.get_email()])

    def send_sso_unlink_email(self, disabling_user: RpcUser, provider):
        from sentry.services.hybrid_cloud.lost_password_hash import lost_password_hash_service
        from sentry.utils.email import MessageBuilder

        email = self.get_email()

        recover_uri = "{path}?{query}".format(
            path=reverse("sentry-account-recover"), query=urlencode({"email": email})
        )

        # Nothing to send if this member isn't associated to a user
        if not self.user_id:
            return

        user = user_service.get_user(user_id=self.user_id)
        if not user:
            return

        has_password = user.has_usable_password()

        context = {
            "email": email,
            "recover_url": absolute_uri(recover_uri),
            "has_password": has_password,
            "organization": self.organization,
            "disabled_by_email": disabling_user.email,
            "provider": provider,
        }

        if not has_password:
            password_hash = lost_password_hash_service.get_or_create(user_id=self.user_id)
            context["set_password_url"] = password_hash.get_absolute_url(mode="set_password")

        msg = MessageBuilder(
            subject=f"Action Required for {self.organization.name}",
            template="sentry/emails/auth-sso-disabled.txt",
            html_template="sentry/emails/auth-sso-disabled.html",
            type="organization.auth_sso_disabled",
            context=context,
        )
        msg.send_async([email])

    def get_display_name(self):
        if self.user_id:
            user = user_service.get_user(user_id=self.user_id)
            if user:
                return user.get_display_name()
        return self.email

    def get_label(self):
        if self.user_id:
            user = user_service.get_user(user_id=self.user_id)
            if user:
                return user.get_label()
        return self.email or self.id

    def get_email(self):
        if self.user_id:
            if self.user_email:
                return self.user_email
            user = user_service.get_user(user_id=self.user_id)
            if user and user.email:
                return user.email
        return self.email

    def get_avatar_type(self):
        if self.user_id:
            user = user_service.get_user(user_id=self.user_id)
            if user:
                return user.get_avatar_type()
        return "letter_avatar"

    def get_audit_log_data(self):
        from sentry.models import OrganizationMemberTeam, Team

        teams = list(
            Team.objects.filter(
                id__in=OrganizationMemberTeam.objects.filter(
                    organizationmember=self, is_active=True
                ).values_list("team", flat=True)
            ).values("id", "slug")
        )

        return {
            "email": self.get_email(),
            "user": self.user_id,
            "teams": [t["id"] for t in teams],
            "teams_slugs": [t["slug"] for t in teams],
            "has_global_access": self.has_global_access,
            "role": self.role,
            "invite_status": invite_status_names[self.invite_status],
        }

    def get_teams(self):
        from sentry.models import OrganizationMemberTeam, Team

        return Team.objects.filter(
            status=TeamStatus.ACTIVE,
            id__in=OrganizationMemberTeam.objects.filter(
                organizationmember=self, is_active=True
            ).values("team"),
        )

    def get_scopes(self) -> FrozenSet[str]:
        # include org roles from team membership
        all_org_roles = self.get_all_org_roles()
        scopes = set()

        for role in all_org_roles:
            role_obj = organization_roles.get(role)
            scopes.update(self.organization.get_scopes(role_obj))
        return frozenset(scopes)

    def get_org_roles_from_teams(self) -> Set[str]:
        if self.__org_roles_from_teams is None:
            # Store team_roles so that we don't repeat this query when possible.
            team_roles = set(
                self.teams.all().exclude(org_role=None).values_list("org_role", flat=True)
            )
            self.__org_roles_from_teams = team_roles
        return self.__org_roles_from_teams

    def get_all_org_roles(self) -> List[str]:
        all_org_roles = self.get_org_roles_from_teams()
        all_org_roles.add(self.role)
        return list(all_org_roles)

    def get_org_roles_from_teams_by_source(self) -> List[tuple[str, OrganizationRole]]:
        org_roles = list(self.teams.all().exclude(org_role=None).values_list("slug", "org_role"))

        sorted_org_roles = sorted(
            [(slug, organization_roles.get(role)) for slug, role in org_roles],
            key=lambda r: r[1].priority,
            reverse=True,
        )
        return sorted_org_roles

    def get_all_org_roles_sorted(self) -> List[OrganizationRole]:
        return organization_roles.get_sorted_roles(self.get_all_org_roles())

    def validate_invitation(self, user_to_approve, allowed_roles):
        """
        Validates whether an org has the options to invite members, handle join requests,
        and that the member role doesn't exceed the allowed roles to invite.
        """
        organization = self.organization
        if not features.has("organizations:invite-members", organization, actor=user_to_approve):
            raise UnableToAcceptMemberInvitationException(ERR_CANNOT_INVITE)

        if (
            organization.get_option("sentry:join_requests") is False
            and self.invite_status == InviteStatus.REQUESTED_TO_JOIN.value
        ):
            raise UnableToAcceptMemberInvitationException(ERR_JOIN_REQUESTS_DISABLED)

        # members cannot invite roles higher than their own
        all_org_roles = self.get_all_org_roles()
        if not len(set(all_org_roles) & {r.id for r in allowed_roles}):
            highest_role = organization_roles.get_sorted_roles(all_org_roles)[0].id
            raise UnableToAcceptMemberInvitationException(
                f"You do not have permission to approve a member invitation with the role {highest_role}."
            )
        return True

    def approve_member_invitation(
        self, user_to_approve, api_key=None, ip_address=None, referrer=None
    ):
        """
        Approve a member invite/join request and send an audit log entry
        """
        from sentry import audit_log
        from sentry.utils.audit import create_audit_entry_from_user

        with transaction.atomic(using=router.db_for_write(OrganizationMember)):
            self.approve_invite()
            self.save()

        if settings.SENTRY_ENABLE_INVITES:
            self.send_invite_email()
            member_invited.send_robust(
                member=self,
                user=user_to_approve,
                sender=self.approve_member_invitation,
                referrer=referrer,
            )

        create_audit_entry_from_user(
            user_to_approve,
            api_key,
            ip_address,
            organization_id=self.organization_id,
            target_object=self.id,
            data=self.get_audit_log_data(),
            event=audit_log.get_event_id("MEMBER_INVITE")
            if settings.SENTRY_ENABLE_INVITES
            else audit_log.get_event_id("MEMBER_ADD"),
        )

    def reject_member_invitation(
        self,
        user_to_approve,
        api_key=None,
        ip_address=None,
    ):
        """
        Reject a member invite/join request and send an audit log entry
        """
        from sentry import audit_log
        from sentry.utils.audit import create_audit_entry_from_user

        if self.invite_status == InviteStatus.APPROVED.value:
            return

        self.delete()

        create_audit_entry_from_user(
            user_to_approve,
            api_key,
            ip_address,
            organization_id=self.organization_id,
            target_object=self.id,
            data=self.get_audit_log_data(),
            event=audit_log.get_event_id("INVITE_REQUEST_REMOVE"),
        )

    def get_allowed_org_roles_to_invite(self):
        """
        Return a list of org-level roles which that member could invite
        Must check if member member has member:admin first before checking
        """
        highest_role_priority = self.get_all_org_roles_sorted()[0].priority
        return [r for r in organization_roles.get_all() if r.priority <= highest_role_priority]

    def is_only_owner(self) -> bool:
        if organization_roles.get_top_dog().id not in self.get_all_org_roles():
            return False

        # check if any other member has the owner role, including through a team
        is_only_owner = not (
            self.organization.get_members_with_org_roles(roles=[roles.get_top_dog().id])
            .exclude(id=self.id)
            .exists()
        )
        return is_only_owner
