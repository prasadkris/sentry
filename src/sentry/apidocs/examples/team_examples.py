from drf_spectacular.utils import OpenApiExample


class TeamExamples:
    CREATE_TEAM = [
        OpenApiExample(
            "Create a new team",
            value={
                "id": "5151492858",
                "slug": "ancient-gabelers",
                "name": "Ancient Gabelers",
                "dateCreated": "2021-06-12T23:38:54.168307Z",
                "isMember": True,
                "teamRole": "admin",
                "flags": {"idp:provisioned": False},
                "access": [
                    "project:write",
                    "member:read",
                    "event:write",
                    "team:admin",
                    "alerts:read",
                    "project:releases",
                    "alerts:write",
                    "org:read",
                    "team:read",
                    "project:admin",
                    "project:read",
                    "org:integrations",
                    "event:read",
                    "event:admin",
                    "team:write",
                ],
                "hasAccess": True,
                "isPending": False,
                "memberCount": 1,
                "avatar": {"avatarType": "letter_avatar", "avatarUuid": None},
            },
            status_codes=["201"],
            response_only=True,
        ),
    ]

    LIST_ORG_TEAMS = [
        OpenApiExample(
            "Get list of organization's teams",
            value=[
                {
                    "id": "48531",
                    "slug": "ancient-gabelers",
                    "name": "Ancient Gabelers",
                    "dateCreated": "2018-11-06T21:20:08.115Z",
                    "isMember": False,
                    "teamRole": None,
                    "flags": {"idp:provisioned": False},
                    "access": [
                        "member:read",
                        "alerts:read",
                        "org:read",
                        "event:read",
                        "project:read",
                        "project:releases",
                        "event:write",
                        "team:read",
                    ],
                    "hasAccess": True,
                    "isPending": False,
                    "memberCount": 2,
                    "avatar": {"avatarType": "letter_avatar", "avatarUuid": None},
                },
                {
                    "id": "100253",
                    "slug": "powerful-abolitionist",
                    "name": "Powerful Abolitionist",
                    "dateCreated": "2018-10-03T17:47:50.745447Z",
                    "isMember": False,
                    "teamRole": None,
                    "flags": {"idp:provisioned": False},
                    "access": [
                        "member:read",
                        "alerts:read",
                        "org:read",
                        "event:read",
                        "project:read",
                        "project:releases",
                        "event:write",
                        "team:read",
                    ],
                    "hasAccess": True,
                    "isPending": False,
                    "memberCount": 5,
                    "avatar": {"avatarType": "letter_avatar", "avatarUuid": None},
                    "projects": [
                        {
                            "id": "6403534",
                            "slug": "prime-mover",
                            "name": "Prime Mover",
                            "platform": None,
                            "dateCreated": "2019-04-06T00:02:40.468175Z",
                            "isBookmarked": False,
                            "isMember": False,
                            "features": [
                                "alert-filters",
                                "custom-inbound-filters",
                                "data-forwarding",
                                "discard-groups",
                                "minidump",
                                "race-free-group-creation",
                                "rate-limits",
                                "servicehooks",
                                "similarity-indexing",
                                "similarity-indexing-v2",
                                "similarity-view",
                                "similarity-view-v2",
                                "releases",
                            ],
                            "firstEvent": "2019-04-06T02:00:21Z",
                            "firstTransactionEvent": True,
                            "access": [
                                "alerts:read",
                                "event:write",
                                "org:read",
                                "project:read",
                                "member:read",
                                "team:read",
                                "event:read",
                                "project:releases",
                            ],
                            "hasAccess": True,
                            "hasMinifiedStackTrace": False,
                            "hasMonitors": True,
                            "hasProfiles": False,
                            "hasReplays": False,
                            "hasSessions": True,
                            "isInternal": False,
                            "isPublic": False,
                            "avatar": {"avatarType": "letter_avatar", "avatarUuid": None},
                            "color": "#6d3fbf",
                            "status": "active",
                        },
                        {
                            "id": "6403599",
                            "slug": "the-spoiled-yoghurt",
                            "name": "The Spoiled Yoghurt",
                            "platform": "",
                            "dateCreated": "2022-06-24T17:55:27.304367Z",
                            "isBookmarked": False,
                            "isMember": False,
                            "features": [
                                "alert-filters",
                                "custom-inbound-filters",
                                "data-forwarding",
                                "discard-groups",
                                "minidump",
                                "race-free-group-creation",
                                "rate-limits",
                                "servicehooks",
                                "similarity-indexing",
                                "similarity-indexing-v2",
                                "similarity-view",
                                "similarity-view-v2",
                            ],
                            "firstEvent": "2022-07-13T18:17:56.197351Z",
                            "firstTransactionEvent": False,
                            "access": [
                                "alerts:read",
                                "event:write",
                                "org:read",
                                "project:read",
                                "member:read",
                                "team:read",
                                "event:read",
                                "project:releases",
                            ],
                            "hasAccess": True,
                            "hasMinifiedStackTrace": False,
                            "hasMonitors": True,
                            "hasProfiles": False,
                            "hasReplays": False,
                            "hasSessions": False,
                            "isInternal": False,
                            "isPublic": False,
                            "avatar": {"avatarType": "letter_avatar", "avatarUuid": None},
                            "color": "#6e3fbf",
                            "status": "active",
                        },
                    ],
                },
            ],
            status_codes=["200"],
            response_only=True,
        )
    ]

    LIST_TEAM_PROJECTS = [
        OpenApiExample(
            "Get list of team's projects",
            value=[
                {
                    "team": {
                        "id": "2349234102",
                        "name": "Prime Mover",
                        "slug": "prime-mover",
                    },
                    "teams": [
                        {
                            "id": "2349234102",
                            "name": "Prime Mover",
                            "slug": "prime-mover",
                        },
                        {
                            "id": "47584447",
                            "name": "Powerful Abolitionist",
                            "slug": "powerful-abolitionist",
                        },
                    ],
                    "id": "6758470122493650",
                    "name": "the-spoiled-yoghurt",
                    "slug": "The Spoiled Yoghurt",
                    "isBookmarked": False,
                    "isMember": True,
                    "access": [
                        "project:read",
                        "event:read",
                        "team:read",
                        "alerts:read",
                        "org:read",
                        "event:write",
                        "project:releases",
                        "member:read",
                    ],
                    "hasAccess": True,
                    "dateCreated": "2023-03-29T15:25:21.344565Z",
                    "environments": ["production"],
                    "eventProcessing": {"symbolicationDegraded": False},
                    "features": [
                        "alert-filters",
                        "custom-inbound-filters",
                        "data-forwarding",
                        "discard-groups",
                        "minidump",
                        "race-free-group-creation",
                        "rate-limits",
                        "servicehooks",
                        "similarity-indexing",
                        "similarity-indexing-v2",
                        "similarity-view",
                        "similarity-view-v2",
                    ],
                    "firstEvent": None,
                    "firstTransactionEvent": True,
                    "hasSessions": False,
                    "hasProfiles": False,
                    "hasReplays": False,
                    "hasMonitors": False,
                    "hasMinifiedStackTrace": False,
                    "platform": "node-express",
                    "platforms": [],
                    "latestRelease": None,
                    "hasUserReports": False,
                    "latestDeploys": None,
                },
                {
                    "team": {
                        "id": "2349234102",
                        "name": "Prime Mover",
                        "slug": "prime-mover",
                    },
                    "teams": [
                        {
                            "id": "2349234102",
                            "name": "Prime Mover",
                            "slug": "prime-mover",
                        }
                    ],
                    "id": "1829334501859481",
                    "name": "Pump Station",
                    "slug": "pump-station",
                    "isBookmarked": False,
                    "isMember": True,
                    "access": [
                        "project:read",
                        "event:read",
                        "team:read",
                        "alerts:read",
                        "org:read",
                        "event:write",
                        "project:releases",
                        "member:read",
                    ],
                    "hasAccess": True,
                    "dateCreated": "2023-03-29T15:21:49.943746Z",
                    "environments": ["production"],
                    "eventProcessing": {"symbolicationDegraded": False},
                    "features": [
                        "alert-filters",
                        "custom-inbound-filters",
                        "data-forwarding",
                        "discard-groups",
                        "minidump",
                        "race-free-group-creation",
                        "rate-limits",
                        "servicehooks",
                        "similarity-indexing",
                        "similarity-indexing-v2",
                        "similarity-view",
                        "similarity-view-v2",
                    ],
                    "firstEvent": "2023-04-05T21:02:08.054000Z",
                    "firstTransactionEvent": False,
                    "hasSessions": False,
                    "hasProfiles": False,
                    "hasReplays": False,
                    "hasMonitors": False,
                    "hasMinifiedStackTrace": True,
                    "platform": "javascript",
                    "platforms": ["javascript"],
                    "latestRelease": None,
                    "hasUserReports": False,
                    "latestDeploys": None,
                },
            ],
            status_codes=["200"],
            response_only=True,
        )
    ]
