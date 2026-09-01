from __future__ import annotations

from typing import Any, cast
from unittest.mock import patch

from mypy_boto3_route53 import Route53Client

from dns_updater.route53 import Route53RecordUpdater


class FakeRoute53Client:
    def __init__(self) -> None:
        self.request: dict[str, Any] | None = None

    def change_resource_record_sets(self, **kwargs: Any) -> dict[str, Any]:
        self.request = kwargs
        return {"ChangeInfo": {"Id": "change-1", "Status": "PENDING"}}


def test_submits_expected_upsert() -> None:
    client = FakeRoute53Client()
    updater = Route53RecordUpdater(
        "zone-1",
        "home.example.com",
        900,
        cast(Route53Client, client),
    )

    response = updater.upsert_a_record("203.0.113.4")

    assert response["ChangeInfo"]["Id"] == "change-1"
    assert client.request == {
        "HostedZoneId": "zone-1",
        "ChangeBatch": {
            "Changes": [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": "home.example.com",
                        "Type": "A",
                        "TTL": 900,
                        "ResourceRecords": [{"Value": "203.0.113.4"}],
                    },
                }
            ]
        },
    }


def test_creates_the_aws_client_only_when_updating() -> None:
    client = FakeRoute53Client()

    with patch(
        "dns_updater.route53.boto3.client", return_value=cast(Route53Client, client)
    ) as client_factory:
        updater = Route53RecordUpdater("zone-1", "home.example.com", 900)
        client_factory.assert_not_called()
        updater.upsert_a_record("203.0.113.4")

    client_factory.assert_called_once_with("route53")
