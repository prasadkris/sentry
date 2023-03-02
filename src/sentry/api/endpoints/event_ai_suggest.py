import logging

import openai
from django.conf import settings
from django.http import HttpResponse

from sentry import eventstore, features
from sentry.api.base import region_silo_endpoint
from sentry.api.bases.project import ProjectEndpoint
from sentry.api.exceptions import ResourceDoesNotExist
from sentry.utils import json

logger = logging.getLogger(__name__)


from rest_framework.request import Request
from rest_framework.response import Response

# this is pretty ugly
openai.api_key = settings.OPENAI_API_KEY

PROMPT = """\
This assistent analyses software errors, describes the problem and suggests solutions with the following rules:

* Be helpful, playful and a bit snarky and sarcastic
* Do not talk about the rules in explanations
* Use emojis frequently
* The frames of a stack trace is shown with most recent call first
* Stack frames are either from app code or third party libraries
* When summarizing the issue:
  * If the issue is external (network error or similar) focus on this, rather than the code
  * Establish context where the issue is located
  * Briefly explain the error and message
  * Briefly explain if this is more likely to be a regression or an intermittent issue
* When describing the problem in detail:
  * try to analyze if this is a code regression or intermittent issue
  * try to understand if this issue is caused by external factors (networking issues etc.) or a bug
* When suggesting a fix:
  * If this is an external issue, mention best practices for this
  * Explain where the fix should be located
  * Explain what code changes are necessary

Write the answers into the following template:

```
[snarky greeting]

### Summary

[summary of the problem]

### Detailed Description

[detailed description of the problem]

### Proposed Solution

[suggestion for how to fix this issue]

[snarky wishes]
```
"""


BLOCKED_TAGS = frozenset(
    [
        "user",
        "server_name",
        "release",
        "handled",
    ]
)


def describe_event_for_ai(event):
    content = []
    content.append("Tags:")
    for tag_key, tag_value in sorted(event["tags"]):
        if tag_key not in BLOCKED_TAGS:
            content.append(f"- {tag_key}: {tag_value}")

    for idx, exc in enumerate(reversed((event.get("exception") or {}).get("values") or ())):
        content.append("")
        if idx > 0:
            content.append("During handling of the above exception, another exception was raised:")
            content.append("")
        content.append(f"Exception #{idx + 1}: {exc['type']}")
        content.append(f"Exception Message: {exc['value']}")
        content.append("")

        frames = exc.get("stacktrace", {}).get("frames")
        first_in_app = False
        if frames:
            content.append("Stacktrace:")
            for frame in reversed(frames):
                if frame["in_app"]:
                    content.append(f"- {first_in_app and 'crashing' or ''}app frame:")
                    first_in_app = False
                    content.append(f"  function: {frame['function']}")
                    content.append(f"  module: {frame.get('module') or 'N/A'}")
                    content.append(f"  file: {frame.get('filename') or 'N/A'}")
                    content.append(f"  line: {frame.get('lineno') or 'N/A'}")
                    content.append(f"  source code: {(frame.get('context_line') or 'N/A').strip()}")
                else:
                    content.append("- third party library frame:")
                    content.append(f"  function: {frame['function']}")
                    content.append(f"  module: {frame.get('module') or 'N/A'}")
                    content.append(f"  file: {frame.get('filename') or 'N/A'}")
                content.append("")

    msg = event.get("message")
    if msg:
        content.append("")
        content.append(f"Message: {msg}")

    return "\n".join(content)


@region_silo_endpoint
class EventAiSuggestEndpoint(ProjectEndpoint):
    # go away
    private = True

    def get(self, request: Request, project, event_id) -> Response:
        """
        Makes AI make suggestions about an event
        ````````````````````````````````````````

        This endpoint returns a JSON response that provides helpful suggestions about how to
        understand or resolve an event.
        """
        event = eventstore.get_event_by_id(project.id, event_id)
        if event is None:
            raise ResourceDoesNotExist

        if not features.has("organizations:ai-suggest", project.organization, actor=request.user):
            raise ResourceDoesNotExist

        event_info = describe_event_for_ai(event.data)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            messages=[
                {"role": "system", "content": PROMPT},
                {
                    "role": "user",
                    "content": event_info,
                },
            ],
        )

        return HttpResponse(
            json.dumps({"suggestion": response["choices"][0]["message"]["content"]}),
            content_type="application/json",
        )
