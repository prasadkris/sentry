from contextlib import contextmanager
from unittest.mock import patch

from django.http import HttpRequest
from rest_framework.response import Response

from sentry import features
from sentry.features.base import OrganizationFeature
from sentry.features.helpers import any_organization_has_feature, requires_feature
from sentry.testutils.cases import TestCase


class TestFeatureHelpers(TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.org = self.create_organization(owner=self.user)
        self.out_of_scope_org = self.create_organization(owner=self.user)

        self.request = HttpRequest()
        self.request.user = self.user

        features.add("foo", OrganizationFeature)

    def test_any_organization_has_feature(self):
        assert not any_organization_has_feature("foo", self.user.get_orgs())
        with org_with_feature(self.org, "foo"):
            assert any_organization_has_feature("foo", self.user.get_orgs())

    def test_org_missing_from_request_fails(self):
        @requires_feature("foo")
        def get(self, request):
            return Response()

        assert get(None, self.request).status_code == 404

    def test_org_without_feature_flag_fails(self):
        @requires_feature("foo")
        def get(self, request):
            return Response()

        assert get(None, self.request, organization=self.org).status_code == 404

    def test_org_with_feature_flag_succeeds(self):
        # The Org in scope of the request has the flag.
        with org_with_feature(self.org, "foo"):

            @requires_feature("foo")
            def get(self, request, *args, **kwargs):
                return Response()

            response = get(None, self.request, organization=self.org)
            assert response.status_code == 200

    def test_any_org_true_when_users_other_org_has_flag_succeeds(self):
        # The Org in scope of the request does not have the flag, but another
        # Org the User belongs to does.
        #
        with org_with_feature(self.out_of_scope_org, "foo"):

            @requires_feature("foo", any_org=True)
            def get(self, request, *args, **kwargs):
                return Response()

            response = get(None, self.request, organization=self.org)
            assert response.status_code == 200

    def test_any_org_false_when_users_other_org_has_flag_fails(self):
        with org_with_feature(self.out_of_scope_org, "foo"):

            @requires_feature("foo")
            def get(self, request, *args, **kwargs):
                return Response()

            response = get(None, self.request, organization=self.org)
            assert response.status_code == 404


@contextmanager
def org_with_feature(org, feature):
    with patch("sentry.features.has") as has:
        has.side_effect = lambda f, _org, *a, **k: f == feature and org == _org
        yield
