import pytest
from django.urls import reverse

from sentry.relay.config.measurements import BUILTIN_MEASUREMENTS, CUSTOM_MEASUREMENT_LIMIT
from sentry.relay.config.metric_extraction import HISTOGRAM_OUTLIER_RULES
from sentry.utils import json
from sentry.utils.pytest.fixtures import django_db_all


@pytest.fixture
def call_global_config(client, relay, private_key):
    def inner(version):
        path = reverse("sentry-api-0-relay-projectconfigs") + f"?version={version}"

        raw_json, signature = private_key.pack({"globalConfig": True})

        resp = client.post(
            path,
            data=raw_json,
            content_type="application/json",
            HTTP_X_SENTRY_RELAY_ID=relay.relay_id,
            HTTP_X_SENTRY_RELAY_SIGNATURE=signature,
        )

        return json.loads(resp.content), resp.status_code

    return inner


@pytest.mark.parametrize(
    ("version, expect_global_config"), [*((version, False) for version in (1, 2, 3)), (4, True)]
)
@django_db_all
def test_return_global_config(call_global_config, version, expect_global_config):
    result, status_code = call_global_config(version)
    assert status_code < 400
    if not expect_global_config:
        assert result.get("global") is None
    else:
        assert result.get("global") == {
            "measurements": {
                "builtinMeasurements": BUILTIN_MEASUREMENTS,
                "maxCustomMeasurements": CUSTOM_MEASUREMENT_LIMIT,
            },
            "metricsConditionalTagging": HISTOGRAM_OUTLIER_RULES,
        }
