from datetime import timedelta
from email.headerregistry import Address

from django.db.models import Count, Q, QuerySet
from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from sentry import roles
from sentry.api.base import region_silo_endpoint
from sentry.api.bases.organization import OrganizationEndpoint, OrganizationPermission
from sentry.api.serializers import Serializer, serialize
from sentry.models import Repository
from sentry.models.commitauthor import CommitAuthor
from sentry.models.organization import Organization
from sentry.search.utils import tokenize_query


class MissingOrgMemberSerializer(Serializer):
    def serialize(self, obj, attrs, user, **kwargs):
        return {"email": obj.email, "externalId": obj.external_id, "commitCount": obj.commit_count}


class MissingMembersPermission(OrganizationPermission):
    scope_map = {"GET": ["org:write"]}


@region_silo_endpoint
class OrganizationMissingMembersEndpoint(OrganizationEndpoint):
    permission_classes = (MissingMembersPermission,)

    def _get_missing_members(self, organization: Organization) -> QuerySet[CommitAuthor]:
        member_emails = set(
            organization.member_set.exclude(email=None).values_list("email", flat=True)
        )
        member_emails.update(
            set(
                organization.member_set.exclude(user_email=None).values_list(
                    "user_email", flat=True
                )
            )
        )
        nonmember_authors = CommitAuthor.objects.filter(organization_id=organization.id).exclude(
            email__in=member_emails
        )

        # currently for Github only
        org_repos = Repository.objects.filter(
            provider="integrations:github", organization_id=organization.id
        ).values_list("id", flat=True)

        return (
            nonmember_authors.filter(
                commit__repository_id__in=set(org_repos),
                commit__date_added__gte=timezone.now() - timedelta(days=30),
            )
            .annotate(commit_count=Count("commit"))
            .order_by("-commit_count")
        )

    def _get_email_domain(self, email: str) -> str:
        return Address(addr_spec=email).domain

    def get(self, request: Request, organization) -> Response:
        queryset = self._get_missing_members(organization)

        # if a member has user_email=None, then they have yet to accept an invite
        org_owners = organization.get_members_with_org_roles(
            roles=[roles.get_top_dog().id]
        ).exclude(user_email=None)

        owner_emails = {self._get_email_domain(owner.user_email) for owner in org_owners}

        if len(owner_emails) == 1:
            queryset = queryset.filter(email__endswith=owner_emails.pop())

        query = request.GET.get("query")
        if query:
            tokens = tokenize_query(query)
            if "query" in tokens:
                query_value = " ".join(tokens["query"])
                queryset = queryset.filter(
                    Q(email__icontains=query_value) | Q(external_id__icontains=query_value)
                )

        return Response(
            [
                {
                    "integration": "github",
                    "users": serialize(
                        list(queryset), request.user, serializer=MissingOrgMemberSerializer()
                    ),
                }
            ],
            status=status.HTTP_200_OK,
        )
